import sounddevice as sd
import numpy as np
import time
from conversation import start_voice_conversation


from greeting import speak
from pathlib import Path
from openwakeword.model import Model
from greeting import speak, get_greeting
from weather import get_weather
from system_health import get_system_health
from forex import get_forex, open_forex_charts
from workspace import arrange_workspace
from spotify import play_spotify
from voice_commands import listen_for_response
from command_router import route_command
from background_music import (
    start_background_music,
    stop_background_music,
)
from voice_commands import (
    listen_until_response,
)



CLAP_THRESHOLD = 12
CLAP_SHARPNESS_THRESHOLD = 6.0
DOUBLE_CLAP_WINDOW = 1.0
CLAP_COOLDOWN = 0.3

clap_times = []
double_clap_detected = False
wake_word_detected = False
last_clap_time = 0

SAMPLE_RATE = 16000
CHUNK_SIZE = 1280
MICROPHONE_INDEX = 1

WAKE_WORD_THRESHOLD = 0.30
ACTIVATION_COOLDOWN = 3.0
ignore_activation_until = 0.0



def get_wake_word_model_path():
    project_folder = Path(__file__).resolve().parent.parent

    return (
        project_folder
        / "models"
        / "wake_words"
        / "hey_Clap.onnx"
    )


wake_word_model_path = get_wake_word_model_path()

if not wake_word_model_path.exists():
    raise FileNotFoundError(
        f"Wake-word model was not found: {wake_word_model_path}"
    )


wake_word_model = Model(
    wakeword_models=[str(wake_word_model_path)],
    inference_framework="onnx",
)







def detect_activation(indata, frames, time_info, status):
    global double_clap_detected
    global wake_word_detected
    global last_clap_time
    global ignore_activation_until

    if double_clap_detected or wake_word_detected:
        return

    current_time = time.monotonic()

    if current_time < ignore_activation_until:
     return


     # Convert microphone audio for the wake-word model.
    audio_frame = np.clip(
        indata.flatten(),
        -1.0,
        1.0,
    )

    audio_frame = (
        audio_frame * 32767
    ).astype(np.int16)

    predictions = wake_word_model.predict(audio_frame)
    highest_wake_score = max(
        predictions.values(),
        default=0.0,
    )





    for model_name, score in predictions.items():
        if score >= WAKE_WORD_THRESHOLD:
            print(
                "HEY CLAP DETECTED:",
                model_name,
                f"score={score:.2f}",
            )

            clap_times.clear()
            wake_word_detected = True
            return

    # Do not interpret speech resembling "Hey CLAP" as claps.
    if highest_wake_score >= 0.10:
        clap_times.clear()
        return


    # Check for a physical double clap.
    volume = np.linalg.norm(indata) * 10

    samples = indata.flatten()
    peak = np.max(np.abs(samples))
    rms = np.sqrt(np.mean(samples ** 2)) + 0.000001
    sharpness = peak / rms

    spectrum = np.abs(np.fft.rfft(samples))
    frequencies = np.fft.rfftfreq(
    len(samples),
    d=1 / SAMPLE_RATE,
    )

    total_energy = np.sum(spectrum ** 2) + 0.000001
    high_energy = np.sum(
    spectrum[frequencies >= 2500] ** 2
    )
    high_frequency_ratio = high_energy / total_energy




    if (
        volume <= CLAP_THRESHOLD
        or sharpness < CLAP_SHARPNESS_THRESHOLD
    ):
        return

    if current_time - last_clap_time < CLAP_COOLDOWN:
        return

    last_clap_time = current_time
    clap_times.append(current_time)

    clap_times[:] = [
        clap_time
        for clap_time in clap_times
        if current_time - clap_time <= DOUBLE_CLAP_WINDOW
    ]

    if (
        len(clap_times) >= 2
        and clap_times[-1] - clap_times[-2]
        <= DOUBLE_CLAP_WINDOW
    ):
        print("DOUBLE CLAP DETECTED")

        clap_times.clear()
        double_clap_detected = True



print("Listening for double clap or Hey CLAP...")

with sd.InputStream(
    callback=detect_activation,
    device=MICROPHONE_INDEX,
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="float32",
    blocksize=CHUNK_SIZE,
    latency="high",
):

     while True:


        if not double_clap_detected and not wake_word_detected:
            time.sleep(0.05)
            continue

        if double_clap_detected or wake_word_detected:

           greeting = (
               f"{get_greeting()}. "
               f"CLAP is online "

)

           speak(greeting)

           speak("How can I help. ? "
                 "Say a command, or ask me anything"
                  )



           response = listen_for_response()

           if not response:
              response = listen_until_response(
                    "I did not hear you. Please say your command again."
              )




           yes_words = {"yes", "yeah", "yep", "sure", "okay", "ok"}


           direct_command_words = {
                "weather",
                "whether",
                "system",
                "health",
                "system",
                "health",
                "forex",
                "currency",
                "aed",
                "dirham",
                "peso",
                "pesos",
                "tradingview",
                "chart",
                "charts",

            }


           if any(word in response for word in direct_command_words):
                    route_command(response)

                    no_words = {
                        "no",
                        "nope",
                        "nothing",
                        "done",
                        "stop",
                        "thank you",
                    }

                    while True:
                        speak(
                        "Is there anything else I can help you with? "
                          "Say your next command, or say no."

                        )

                        time.sleep(1.5)



                        follow_up = listen_until_response(
                             "I did not hear you. Please say your next command, or say no."
                        )


                        if any(
                            phrase in follow_up
                            for phrase in no_words
                        ):
                            speak("Okay Marc, standing by.")
                            break

                        route_command(follow_up)



                    wake_word_model.reset()

                    clap_times.clear()
                    double_clap_detected = False
                    wake_word_detected = False
                    last_clap_time = time.monotonic()
                    ignore_activation_until = time.monotonic() + ACTIVATION_COOLDOWN

                    print("Listening for double clap or Hey CLAP...")
                    continue


        is_briefing = (
            any(word in response.split() for word in yes_words)
            or "briefing" in response
            )

        if not is_briefing:
            start_voice_conversation(
                initial_message=response
           )

            wake_word_model.reset()
            clap_times.clear()
            double_clap_detected = False
            wake_word_detected = False
            last_clap_time = time.monotonic()
            ignore_activation_until = (
                time.monotonic() + ACTIVATION_COOLDOWN
            )

            print("Listening for double clap or Hey CLAP...")
            continue

        if is_briefing:

                    weather_report = get_weather()
                    system_report = get_system_health()
                    forex_report = get_forex()

                    print(greeting)
                    print(weather_report)
                    print(system_report)
                    print(forex_report)


                    start_background_music()

                    try:
                        speak(weather_report)
                        speak(system_report)
                        speak(forex_report)

                    finally:
                        stop_background_music()


                    speak("Opening your trading workspace")
                    open_forex_charts()
                    time.sleep(5)

                    try:
                        arrange_workspace()
                    except Exception as e:
                        print("Workspace error:", e)

                    speak("Daily briefing complete.")



                    speak("Would you like me to launch Spotify?")

                    spotify_response = listen_until_response(
                        "I did not hear you. Please say yes or no."
                      )


                    print("Spotify response =", spotify_response)

                    if any(
                       word in spotify_response.split()
                     for word in yes_words
                    ):
                     speak("Launching Spotify.")
                     play_spotify()
                    else:
                     speak("Okay Marc. Spotify will remain closed.")


                    break


