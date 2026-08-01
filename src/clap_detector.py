import sounddevice as sd
import numpy as np
import time
from conversation import start_voice_conversation



from greeting import (
    get_greeting,
    is_speaking,
    request_speech_control,
    set_speech_control_handler,
    speak,
)
from pathlib import Path
from openwakeword.model import Model
from weather import get_weather
from system_health import get_system_health
from forex import get_forex, open_forex_charts
from google_calendar import get_todays_calendar
from workspace import arrange_workspace
from spotify import play_spotify
from voice_commands import listen_for_response
from command_router import (
    is_daily_briefing_request,
    is_google_tasks_request,
    is_switchbot_curtain_request,
    route_command,
    should_offer_command_follow_up,
)
from background_music import (
    pause_background_music,
    resume_background_music,
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
SPEECH_CONTROL_CLAP_THRESHOLD = 12
SPEECH_CONTROL_SHARPNESS_THRESHOLD = 8.0
SPEECH_CONTROL_DOUBLE_CLAP_WINDOW = 0.8
SPEECH_CONTROL_MIN_CLAP_GAP = 0.18
SPEECH_CONTROL_PEAK_THRESHOLD = 0.55

clap_times = []
double_clap_detected = False
wake_word_detected = False
last_clap_time = 0

SAMPLE_RATE = 16000
CHUNK_SIZE = 1280
MICROPHONE_INDEX = 1

WAKE_WORD_THRESHOLD = 0.30
ACTIVATION_COOLDOWN = 3.0
SPEECH_CONTROL_ARM_DELAY = 3.0
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



def handle_speech_control():
    """
    Listen for Marc's instruction after speech is paused.
    """

    continue_phrases = {
        "continue",
        "resume",
        "carry on",
        "go ahead",
    }

    repeat_phrases = {
        "repeat",
        "repeat that",
        "say that again",
    }

    stop_phrases = {
        "stop",
        "cancel",
        "full stop",
        "stand by",
        "standby",
    }

    pause_background_music()

    print("Speech paused. Say continue, repeat, or stop.")



    for _attempt in range(3):
        response = listen_for_response(phrase_time_limit=4)

        if not response:
            print("Please say continue, repeat, or stop.")
            continue

        normalized_response = response.strip().lower()

        if normalized_response in continue_phrases:
            resume_background_music()
            return "continue"

        if normalized_response in repeat_phrases:
            resume_background_music()
            return "repeat"

        if normalized_response in stop_phrases:
            stop_background_music()
            return "stop"

        print("Please say continue, repeat, or stop.")

    print("No speech-control command understood. Continuing speech.")
    resume_background_music()
    return "continue"


set_speech_control_handler(handle_speech_control)


def detect_activation(indata, frames, time_info, status):
    global double_clap_detected
    global wake_word_detected
    global last_clap_time
    global ignore_activation_until

    currently_speaking = is_speaking()

    # Once activated, ignore more activation attempts unless CLAP
    # is speaking and the double clap is intended as speech control.
    if (
        (double_clap_detected or wake_word_detected)
        and not currently_speaking
    ):
        return

    current_time = time.monotonic()

    if current_time < ignore_activation_until:
        return

    # Wake-word detection is disabled while CLAP is speaking.
    # This prevents CLAP from hearing its own voice as "Hey CLAP".
    if not currently_speaking:
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
                ignore_activation_until = (
                    current_time + SPEECH_CONTROL_ARM_DELAY
                )
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

    active_volume_threshold = (
        SPEECH_CONTROL_CLAP_THRESHOLD
        if currently_speaking
        else CLAP_THRESHOLD
    )
    active_sharpness_threshold = (
        SPEECH_CONTROL_SHARPNESS_THRESHOLD
        if currently_speaking
        else CLAP_SHARPNESS_THRESHOLD
    )
    active_double_clap_window = (
        SPEECH_CONTROL_DOUBLE_CLAP_WINDOW
        if currently_speaking
        else DOUBLE_CLAP_WINDOW
    )

    if (
        volume <= active_volume_threshold
        or sharpness < active_sharpness_threshold
        or (
            currently_speaking
            and peak < SPEECH_CONTROL_PEAK_THRESHOLD
        )
    ):
        return

    if current_time - last_clap_time < CLAP_COOLDOWN:
        return

    last_clap_time = current_time
    clap_times.append(current_time)

    clap_times[:] = [
        clap_time
        for clap_time in clap_times
        if current_time - clap_time <= active_double_clap_window
    ]

    if (
        len(clap_times) >= 2
        and clap_times[-1] - clap_times[-2]
        >= SPEECH_CONTROL_MIN_CLAP_GAP
        and clap_times[-1] - clap_times[-2]
        <= active_double_clap_window
    ):
        clap_times.clear()

        if currently_speaking:
            if request_speech_control(trigger="double_clap"):
                print("SPEECH CONTROL DOUBLE CLAP DETECTED")

            return

        print("DOUBLE CLAP DETECTED")
        double_clap_detected = True
        ignore_activation_until = (
            current_time + SPEECH_CONTROL_ARM_DELAY
        )



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

           no_words = {
                "no",
                "nope",
                "nothing",
                "done",
                "stop",
                "stand by",
                "standby",
                "exit",
                "full stop",
                "thank you",
           }

           normalized_response = response.strip().lower()
           briefing_requested = is_daily_briefing_request(
               normalized_response
           )

           if normalized_response in no_words:
                speak("Okay Marc, standing by.")

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
                "spotify",
                "music",
                "song",
                "track",
                "relaxing",
                "relax",
                "relaxation",
                "calm",
                "chill",
                "sleep",
                "sleeping",
                "bedtime",
                "workout",
                "gym",
                "exercise",
                "training",
                "party",
                "dance",
                "volume",
                "mute",
                "unmute",
                "news",
                "latest",
                "technology",
                "tech",
                "cybersecurity",
                "cyber",
                "calendar",
                "schedule",
                "free",
                "availability",
                "add",
                "schedule",
                "calendar",
                "event",
                "appointment",
                "articulation",
                "communication",
                "speaking",

            }


           if (
               not briefing_requested
               and (
                   is_google_tasks_request(response)
                   or is_switchbot_curtain_request(response)
                   or any(
                       word in normalized_response
                       for word in direct_command_words
                   )
               )
           ):
                    route_command(response)

                    while should_offer_command_follow_up(response):
                        speak(
                        "Is there anything else I can help you with? "
                          "Say your next command, or say no."

                        )

                        time.sleep(1.5)



                        follow_up = listen_until_response(
                             "I did not hear you. Please say your next command, or say no.",
                             max_attempts=3,
                        )


                        if not follow_up:
                            speak("Okay Marc, standing by.")
                            break


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
            any(
                word in normalized_response.split()
                for word in yes_words
            )
            or briefing_requested
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
                    calendar_report = get_todays_calendar()

                    print(greeting)
                    print(weather_report)
                    print(system_report)
                    print(forex_report)
                    print(calendar_report)


                    briefing_completed = True

                    start_background_music()

                    try:
                        if not speak(weather_report):
                            briefing_completed = False

                        elif not speak(system_report):
                            briefing_completed = False

                        elif not speak(forex_report):
                            briefing_completed = False

                        elif not speak(calendar_report):
                            briefing_completed = False

                    finally:
                        stop_background_music()

                    if not briefing_completed:
                        print(
                            "Daily briefing stopped. "
                            "Returning to standby."
                        )

                        wake_word_model.reset()
                        clap_times.clear()
                        double_clap_detected = False
                        wake_word_detected = False
                        last_clap_time = time.monotonic()
                        ignore_activation_until = (
                            time.monotonic()
                            + ACTIVATION_COOLDOWN
                        )

                        print(
                            "Listening for double clap "
                            "or Hey CLAP..."
                        )
                        continue


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


