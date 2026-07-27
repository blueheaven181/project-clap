from greeting import speak
from weather import get_weather
from voice_commands import listen_for_response
from system_health import get_system_health
from forex import get_forex


def route_command(command):
    """
    Understand a spoken command and run the correct CLAP module.

    Returns True when the command is recognized.
    Returns False when the command is unknown.
    """

    command = command.strip().lower()

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