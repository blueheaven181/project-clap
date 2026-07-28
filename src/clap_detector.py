import sounddevice as sd
import numpy as np
import time




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






CLAP_THRESHOLD = 5
DOUBLE_CLAP_WINDOW = 1.0
CLAP_COOLDOWN = 0.3

clap_times = []
double_clap_detected = False
last_clap_time = 0



def detect_clap(indata, frames, time_info, status):

    global double_clap_detected
    global last_clap_time

    volume = np.linalg.norm(indata) * 10



    current_time = time.time()

    if double_clap_detected:
     return



    if volume > CLAP_THRESHOLD:

        if current_time - last_clap_time < CLAP_COOLDOWN:
            return

        last_clap_time = current_time

        clap_times.append(current_time)

        clap_times[:] = [
            t for t in clap_times
            if current_time - t <= DOUBLE_CLAP_WINDOW
        ]




        if len(clap_times) >= 2:

            if clap_times[-1] - clap_times[-2] <= DOUBLE_CLAP_WINDOW:

                print("DOUBLE CLAP DETECTED")

                clap_times.clear()

                double_clap_detected = True




print("Listening for claps...")

with sd.InputStream(callback=detect_clap):



     while True:

        if double_clap_detected:

           greeting = (
               f"{get_greeting()}. "
               f"CLAP is online "

)

           speak(greeting)

           speak("How can I help. ? "
                 "Say daily briefing. weather, system health, or forex."
                  )



           response = listen_for_response()

           if not response:
              response = input(
                 "Voice recognition failed. Please type yes or no: "
               ).lower()




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
                "pesos"
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

                        follow_up = listen_for_response()

                        if not follow_up:
                            follow_up = input(
                                "Voice recognition failed. "
                                "Please type your next command or no: "
                            ).lower()

                        if any(
                            word in follow_up.split()
                            for word in no_words
                        ):
                            speak("Okay Marc, standing by.")
                            break

                        route_command(follow_up)


                    double_clap_detected = False
                    print("Listening for claps...")
                    continue


           if (
                any(word in response.split() for word in yes_words)
                or "briefing" in response
            ):

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


           else:
                speak("Okay Marc,Standing by")


           speak("Would you like me to launch Spotify?")

           spotify_response = listen_for_response()

           if not spotify_response:
                spotify_response = input(
                    "Voice recognition failed. Please type yes or no: "
                     ).lower()

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


