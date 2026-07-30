import re
import time

from forex import (
    convert_aed_to_php,
    get_forex,
    open_forex_charts,
)
from greeting import speak
from weather import get_weather
from voice_commands import listen_for_response
from system_health import get_system_health
from forex import get_forex
from workspace import arrange_workspace
from spotify import (
    next_spotify_track,
    pause_spotify,
    play_spotify,
    play_spotify_mood,
    previous_spotify_track,
    resume_spotify,
    stop_spotify,
)
from system_volume import (
    change_system_volume,
    mute_system_volume,
    set_system_volume,
    unmute_system_volume,
)
from news import get_latest_news


def route_command(command):
    """
    Understand a spoken command and run the correct CLAP module.

    Returns True when the command is recognized.
    Returns False when the command is unknown.
    """

    command = command.strip().lower()

    news_request_words = {
        "news",
        "latest",
        "what's new",
        "what is new",
    }

    if any(
        phrase in command
        for phrase in news_request_words
    ):
        if (
            "artificial intelligence" in command
            or " ai " in f" {command} "
        ):
            news_category = "ai"

        elif (
            "cybersecurity" in command
            or "cyber security" in command
            or "cyber" in command
        ):
            news_category = "cybersecurity"

        elif (
            "forex" in command
            or "currency" in command
        ):
            news_category = "forex"

        elif (
            "technology" in command
            or "tech" in command
        ):
            news_category = "technology"

        else:
            news_category = "general"

        news_report = get_latest_news(news_category)

        print(news_report)
        speak(news_report)

        return True

    if "unmute" in command:
        unmute_system_volume()
        speak("System audio unmuted.")
        return True

    if "mute" in command:
        speak("Muting system audio.")
        mute_system_volume()
        return True

    if "volume" in command:
        amount_match = re.search(
            r"\b(\d+(?:\.\d+)?)\b",
            command,
        )

        if not amount_match:
            speak(
                "Please include the volume percentage "
                "you want me to use."
            )
            return True

        amount = float(amount_match.group(1))

        if any(
            word in command
            for word in {
                "reduce",
                "lower",
                "decrease",
                "down",
                "quieter",
            }
        ):
            final_volume = change_system_volume(-amount)
            speak(
                f"System volume reduced to "
                f"{final_volume} percent."
            )
            return True

        if any(
            word in command
            for word in {
                "increase",
                "raise",
                "up",
                "louder",
            }
        ):
            final_volume = change_system_volume(amount)
            speak(
                f"System volume increased to "
                f"{final_volume} percent."
            )
            return True

        if "set" in command or "change" in command:
            final_volume = set_system_volume(amount)
            speak(
                f"System volume set to "
                f"{final_volume} percent."
            )
            return True

        speak(
            "Please say set, increase, or reduce volume, "
            "followed by a percentage."
        )
        return True




    mood_commands = {
        "relaxing": {
            "relaxing",
            "relax",
            "relaxation",
            "calm",
            "chill",
        },
        "sleep": {
            "sleep",
            "sleeping",
            "bedtime",
        },
        "workout": {
            "workout",
            "gym",
            "exercise",
            "training",
        },
        "party": {
            "party",
            "dance",
        },
    }

    for mood, keywords in mood_commands.items():
        if any(keyword in command for keyword in keywords):
            if play_spotify_mood(mood):
                speak(f"Playing your {mood} music.")
            else:
                speak(
                    f"You have not configured a {mood} "
                    "Spotify playlist yet."
                )

            return True

    spotify_words = {
        "spotify",
        "music",
        "song",
        "track",
    }

    if any(word in command for word in spotify_words):
        if "pause" in command:
            speak("Pausing Spotify.")
            pause_spotify()
            return True

        if "resume" in command or "continue" in command:
            speak("Resuming Spotify.")
            resume_spotify()
            return True

        if "stop" in command:
            speak("Stopping Spotify.")
            stop_spotify()
            return True

        if "next" in command or "skip" in command:
            speak("Skipping to the next track.")
            next_spotify_track()
            return True

        if "previous" in command or "back" in command:
            speak("Returning to the previous track.")
            previous_spotify_track()
            return True

        if "play" in command or "open" in command:
            speak("Launching Spotify.")
            play_spotify()
            return True

    if "weather" in command:
        weather_report = get_weather()

        print(weather_report)
        speak(weather_report)

        return True

    if "system" in command or "health" in command:
        system_report = get_system_health()

        print(system_report)
        speak(system_report)

        return True



    if (
         "aed" in command
         or "dirham" in command
         or "peso" in command
    ):
        amount_match = re.search(
            r"\b(\d+(?:\.\d+)?)\b",
            command,
        )

        if amount_match:
            amount = float(amount_match.group(1))
            conversion_report = convert_aed_to_php(amount)

            print(conversion_report)
            speak(conversion_report)
        else:
            speak("Please include the amount you want to convert.")

        return True



    if "tradingview" in command or "chart" in command:
        speak("Opening your TradingView charts.")

        open_forex_charts()
        time.sleep(5)

        try:
            arrange_workspace()
        except Exception as error:
            print("Workspace error:", error)
            speak(
            "The charts opened, but I could not arrange the windows."
            )

        return True

    if "forex" in command or "currency" in command:
        forex_report = get_forex()

        print(forex_report)
        speak(forex_report)

        return True
     

    speak("Sorry Marc, I do not understand that command yet.")
    return False


if __name__ == "__main__":
    speak("How can I help?")

    test_command = listen_for_response()

    if not test_command:
        test_command = input(
            "Voice recognition failed. Please type your command: "
        )

    route_command(test_command)