import re
import time

from articulation_coach import (
    get_requested_exercise_mode,
    is_articulation_training_request,
    start_articulation_training,
)
from forex import (
    convert_aed_to_php,
    get_forex,
    open_forex_charts,
)
from greeting import speak
from weather import get_weather
from system_health import get_system_health
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
from news import (
    get_latest_news,
    get_news_item,
    summarize_news_article,
)
from google_calendar import (
    create_calendar_event,
    get_today_availability,
    get_todays_calendar,
    get_today_free_time,
    parse_calendar_event_request,
)
from voice_commands import (
    listen_for_response,
    listen_until_response,
)
from google_tasks import (
    create_task,
    get_requested_task_due_day,
    get_pending_tasks,
    is_task_read_request,
    parse_task_creation_request,
)
from switchbot_curtain import (
    get_curtain_status,
    parse_curtain_intent,
    set_curtain_position,
    stop_curtain,
)


def is_daily_briefing_request(command):
    """Return True when a transcript requests the daily briefing."""

    normalized_command = command.strip().lower()

    briefing_phrases = {
        "daily briefing",
        "morning briefing",
        "start the briefing",
        "start my briefing",
        "give me my briefing",
        "brief me",
    }

    if "briefing" in normalized_command:
        return True

    if any(
        phrase in normalized_command
        for phrase in briefing_phrases
    ):
        return True

    return (
        "daily breathing" in normalized_command
        or "morning breathing" in normalized_command
    )


def is_google_tasks_request(command):
    """Return True when a transcript belongs to the trusted Tasks module."""

    return bool(
        is_task_read_request(command)
        or parse_task_creation_request(command)
    )


def is_clear_task_creation_confirmation(response):
    """Accept only an unambiguous spoken yes for task creation."""

    normalized = response.strip().lower().replace("’", "'")
    response_words = set(re.findall(r"[a-z']+", normalized))
    denial_words = {"no", "nope", "cancel", "stop", "not", "don't"}
    if response_words.intersection(denial_words):
        return False

    yes_words = {"yes", "yeah", "yep", "sure", "okay", "ok", "confirm"}
    return bool(response_words.intersection(yes_words)) or normalized == "create it"


def is_clear_movement_confirmation(response):
    """Accept repeated affirmative words, but reject any denial or extra wording."""

    words = re.findall(r"[a-z']+", response.strip().lower().replace("’", "'"))
    if not words:
        return False
    denial_words = {"no", "nope", "cancel", "stop", "not", "don't"}
    if denial_words.intersection(words):
        return False
    return all(word in {"yes", "yeah", "yep", "confirm"} for word in words)


def is_switchbot_curtain_request(command):
    """Return True only for an explicitly supported trusted Curtain intent."""

    return parse_curtain_intent(command) is not None


def route_command(command):
    """
    Understand a spoken command and run the correct CLAP module.

    Returns True when the command is recognized.
    Returns False when the command is unknown.
    """

    raw_command = command.strip()
    command = raw_command.lower()

    curtain_request = parse_curtain_intent(raw_command)
    if curtain_request:
        action = curtain_request["action"]
        if action == "invalid_position" or (
            action == "set_position" and not 0 <= curtain_request["position"] <= 100
        ):
            speak("Curtain position must be a whole number from 0 to 100.")
            return True
        if action == "status":
            result = get_curtain_status()
            print(result)
            speak(result)
            return True

        descriptions = {
            "open": "open the curtain",
            "close": "close the curtain",
            "stop": "stop the curtain",
            "set_position": f"move the curtain to {curtain_request.get('position')} percent closed",
        }
        speak(f"You want me to {descriptions[action]}. Shall I move it?")
        confirmation = listen_until_response(
            "I did not hear a clear yes. Curtain movement is cancelled.",
            max_attempts=1,
            phrase_time_limit=5,
        )
        if not is_clear_movement_confirmation(confirmation):
            speak("Okay. I did not move the curtain.")
            return True

        if action == "stop":
            result = stop_curtain()
        else:
            position = {"open": 0, "close": 100}.get(
                action, curtain_request.get("position")
            )
            result = set_curtain_position(position)
        print(result)
        speak(result)
        return True

    if is_articulation_training_request(command):
        exercise_mode = get_requested_exercise_mode(command)
        if exercise_mode:
            return start_articulation_training(exercise_mode=exercise_mode)
        return start_articulation_training()

    task_request = parse_task_creation_request(raw_command)

    if task_request:
        due_date = task_request["due_date"]
        due_phrase = (
            f", due {due_date.strftime('%A, %B %d')}" if due_date else ""
        )
        speak(
            f"You want me to add {task_request['title']} to your tasks"
            f"{due_phrase}. Shall I create it?"
        )
        confirmation = listen_until_response(
            "I did not hear you. Please say yes or no."
        )
        confirmed = is_clear_task_creation_confirmation(confirmation)

        if confirmed:
            result = create_task(task_request["title"], due_date)
        else:
            result = "Okay. I did not create the task."
        print(result)
        speak(result)
        return True

    if is_task_read_request(command):
        tasks_report = get_pending_tasks(
            due_day=get_requested_task_due_day(command)
        )
        print(tasks_report)
        speak(tasks_report)
        return True

    event_request = parse_calendar_event_request(command)

    if event_request:
        event_start = event_request["start"]
        spoken_schedule = event_start.strftime(
            "%A, %B %d at %I:%M %p"
        )

        speak(
            f"You want me to add {event_request['title']} "
            f"on {spoken_schedule} for one hour. "
            "Shall I create it?"
        )

        confirmation = listen_until_response(
            "I did not hear you. Please say yes or no."
        )

        yes_words = {
            "yes",
            "yeah",
            "yep",
            "sure",
            "okay",
            "ok",
            "confirm",
        }

        confirmation_words = set(
            confirmation.strip().lower().split()
        )

        confirmed = (
            bool(confirmation_words.intersection(yes_words))
            or "create it" in confirmation.lower()
        )

        if confirmed:
            result = create_calendar_event(
                event_request["title"],
                event_request["start"],
                event_request["duration_minutes"],
            )
        else:
            result = (
                "Okay. I did not create the calendar event."
            )

        print(result)
        speak(result)
        return True


    if (
        "what time am i free" in command
        or "when am i free" in command
        or "free time today" in command
        or "available time today" in command
    ):
        free_time_report = get_today_free_time()

        print(free_time_report)
        speak(free_time_report)

        return True

    if (
        "am i available" in command
        or "anything scheduled today" in command
        or "anything left today" in command
    ):
        availability_report = get_today_availability()

        print(availability_report)
        speak(availability_report)

        return True

    if "calendar" in command or "schedule" in command:
        calendar_report = get_todays_calendar()

        print(calendar_report)
        speak(calendar_report)
        return True

    headline_request = re.search(
        r"\b(?:headline|story)\s*(one|two|three|1|2|3)\b",
        command,
    )

    if headline_request and any(
        phrase in command
        for phrase in {
            "tell me more",
            "more about",
            "details",
            "explain",
        }
    ):
        number_lookup = {
            "one": 1,
            "two": 2,
            "three": 3,
            "1": 1,
            "2": 2,
            "3": 3,
        }

        requested_number = number_lookup[
            headline_request.group(1)
        ]

        selected_item = get_news_item(requested_number)

        if not selected_item:
            speak(
                "I do not have that headline in memory. "
                "Please request the latest news first."
            )
            return True


        print(
            "Selected news link:",
             selected_item["link"],
        )

        speak(
            f"Let me check headline {requested_number}."
        )

        article_summary = summarize_news_article(
            requested_number
        )

        print("News summary:", article_summary)
        speak(article_summary)
        return True



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
