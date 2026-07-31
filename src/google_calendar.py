from datetime import datetime, time, timedelta
from pathlib import Path
import re
from zoneinfo import ZoneInfo

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
]

CALENDAR_TIMEZONE_NAME = "Asia/Dubai"
ABU_DHABI_TIMEZONE = ZoneInfo(CALENDAR_TIMEZONE_NAME)

PROJECT_FOLDER = Path(__file__).resolve().parent.parent
CREDENTIALS_PATH = PROJECT_FOLDER / "config" / "credentials.json"
TOKEN_PATH = PROJECT_FOLDER / "config" / "token.json"


def get_calendar_credentials():
    """
    Load or create Google Calendar event authorization.
    """

    credentials = None

    if TOKEN_PATH.exists():
        credentials = Credentials.from_authorized_user_file(
            str(TOKEN_PATH),
            SCOPES,
        )

    if not credentials or not credentials.valid:
        if (
            credentials
            and credentials.expired
            and credentials.refresh_token
        ):
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_PATH),
                SCOPES,
            )
            credentials = flow.run_local_server(port=0)

        TOKEN_PATH.write_text(
            credentials.to_json(),
            encoding="utf-8",
        )

    return credentials

def get_calendar_service():
    """
    Build and return an authorized Google Calendar service.
    """

    credentials = get_calendar_credentials()

    return build(
        "calendar",
        "v3",
        credentials=credentials,
    )

def get_calendar_events(start_datetime, end_datetime):
    """
    Retrieve calendar events between two dates and times.
    """

    calendar_service = get_calendar_service()

    result = (
        calendar_service.events()
        .list(
            calendarId="primary",
            timeMin=start_datetime.isoformat(),
            timeMax=end_datetime.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    return result.get("items", [])


def get_todays_calendar():
    """
    Return today's Google Calendar schedule in Abu Dhabi time.
    """

    if not CREDENTIALS_PATH.exists():
        return (
            "Google Calendar credentials were not found. "
            "Please complete the Calendar setup."
        )

    try:


        today = datetime.now(ABU_DHABI_TIMEZONE).date()

        start_of_day = datetime.combine(
            today,
            time.min,
            tzinfo=ABU_DHABI_TIMEZONE,
        )
        end_of_day = datetime.combine(
            today,
            time.max,
            tzinfo=ABU_DHABI_TIMEZONE,
        )

        events = get_calendar_events(
            start_of_day,
            end_of_day,
        )


        if not events:
            return "You have no events scheduled for today."

        schedule_items = []

        for event in events:
            event_title = event.get(
                "summary",
                "Untitled event",
            )
            event_start = event.get("start", {})

            if "dateTime" in event_start:
                start_time = datetime.fromisoformat(
                    event_start["dateTime"]
                ).astimezone(ABU_DHABI_TIMEZONE)

                spoken_time = start_time.strftime("%I:%M %p")
                schedule_items.append(
                    f"{spoken_time}: {event_title}"
                )
            else:
                schedule_items.append(
                    f"All day: {event_title}"
                )

        return (
            "Here is your calendar for today. "
            + ". ".join(schedule_items)
            + "."
        )

    except HttpError as error:
        print("Google Calendar API error:", error)
        return "I could not retrieve your Google Calendar."

    except Exception as error:
        print("Google Calendar error:", error)
        return "I could not connect to your Google Calendar."


def get_today_availability():
    """
    Tell Marc whether he has any remaining events today.
    """

    try:
        current_time = datetime.now(ABU_DHABI_TIMEZONE)

        end_of_day = datetime.combine(
            current_time.date(),
            time.max,
            tzinfo=ABU_DHABI_TIMEZONE,
        )

        events = get_calendar_events(
            current_time,
            end_of_day,
        )

        if not events:
            return "You are free for the rest of today."

        next_event = events[0]
        event_title = next_event.get(
            "summary",
            "Untitled event",
        )
        event_start = next_event.get("start", {})

        if "dateTime" in event_start:
            start_time = datetime.fromisoformat(
                event_start["dateTime"]
            ).astimezone(ABU_DHABI_TIMEZONE)

            spoken_time = start_time.strftime("%I:%M %p")

            return (
                "You still have something scheduled today. "
                f"Your next event is {event_title} "
                f"at {spoken_time}."
            )

        return (
            "You have an all-day event today called "
            f"{event_title}."
        )

    except HttpError as error:
        print("Google Calendar API error:", error)
        return "I could not check your availability."

    except Exception as error:
        print("Google Calendar error:", error)
        return "I could not check your availability."

def get_today_free_time():
    """
    Return Marc's available time periods for the rest of today.
    """

    if not CREDENTIALS_PATH.exists():
        return (
            "Google Calendar credentials were not found. "
            "Please complete the Calendar setup."
        )

    try:
        now = datetime.now(ABU_DHABI_TIMEZONE)
        end_of_day = datetime.combine(
            now.date(),
            time.max,
            tzinfo=ABU_DHABI_TIMEZONE,
        )

        events = get_calendar_events(now, end_of_day)

        timed_events = []

        for event in events:
            event_start = event.get("start", {})
            event_end = event.get("end", {})

            if (
                "dateTime" not in event_start
                or "dateTime" not in event_end
            ):
                continue

            start_time = datetime.fromisoformat(
                event_start["dateTime"]
            ).astimezone(ABU_DHABI_TIMEZONE)

            end_time = datetime.fromisoformat(
                event_end["dateTime"]
            ).astimezone(ABU_DHABI_TIMEZONE)

            timed_events.append((start_time, end_time))

        timed_events.sort(key=lambda event_times: event_times[0])

        if not timed_events:
            return "You are free for the rest of today."

        free_periods = []
        available_from = now

        for start_time, end_time in timed_events:
            if start_time > available_from:
                free_periods.append(
                    (available_from, start_time)
                )

            if end_time > available_from:
                available_from = end_time

        if available_from < end_of_day:
            free_periods.append(
                (available_from, end_of_day)
            )

        if not free_periods:
            return "You have no free time remaining today."

        spoken_periods = []

        for start_time, end_time in free_periods:
            spoken_periods.append(
                f"from {start_time.strftime('%I:%M %p')} "
                f"until {end_time.strftime('%I:%M %p')}"
            )

        return (
            "Your available time today is "
            + ", and ".join(spoken_periods)
            + "."
        )

    except HttpError as error:
        print("Google Calendar API error:", error)
        return "I could not retrieve your Google Calendar."

    except Exception as error:
        print("Google Calendar error:", error)
        return "I could not calculate your available time."


def parse_calendar_event_request(command):
    """
    Understand a simple calendar request such as:
    "Add workout tomorrow at 7 PM"
    """

    normalized_command = command.strip().lower()

    date_match = re.search(
        r"\b(today|tomorrow)\b",
        normalized_command,
    )

    time_match = re.search(
        r"\bat\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b",
        normalized_command,
    )

    if not date_match or not time_match:
        return None

    date_word = date_match.group(1)
    hour = int(time_match.group(1))
    minute = int(time_match.group(2) or 0)
    meridiem = time_match.group(3)

    if hour < 1 or hour > 12 or minute > 59:
        return None

    if meridiem == "pm" and hour != 12:
        hour += 12
    elif meridiem == "am" and hour == 12:
        hour = 0

    event_date = datetime.now(ABU_DHABI_TIMEZONE).date()

    if date_word == "tomorrow":
        event_date += timedelta(days=1)

    event_start = datetime.combine(
        event_date,
        time(hour, minute),
        tzinfo=ABU_DHABI_TIMEZONE,
    )

    title_text = re.sub(
        r"^(?:please\s+)?(?:add|create|schedule)\s+",
        "",
        normalized_command,
    )

    title_text = re.split(
        r"\b(?:today|tomorrow)\b",
        title_text,
        maxsplit=1,
    )[0]

    event_title = title_text.strip(" ,.-")

    if not event_title:
        return None

    return {
        "title": event_title.title(),
        "start": event_start,
        "duration_minutes": 60,
    }


def build_calendar_event_body(
    event_title,
    start_datetime,
    duration_minutes=60,
):
    """Build an event payload using an explicit Abu Dhabi timezone."""

    if start_datetime.tzinfo is None:
        raise ValueError("Calendar event start time must include a timezone.")

    if duration_minutes <= 0:
        raise ValueError("Calendar event duration must be greater than zero.")

    localized_start = start_datetime.astimezone(ABU_DHABI_TIMEZONE)
    event_end = localized_start + timedelta(minutes=duration_minutes)

    return {
        "summary": event_title,
        "start": {
            "dateTime": localized_start.isoformat(),
            "timeZone": CALENDAR_TIMEZONE_NAME,
        },
        "end": {
            "dateTime": event_end.isoformat(),
            "timeZone": CALENDAR_TIMEZONE_NAME,
        },
        "reminders": {
            "useDefault": True,
        },
    }


def create_calendar_event(
    event_title,
    start_datetime,
    duration_minutes=60,
):
    """
    Create a Google Calendar event after CLAP receives confirmation.
    """

    if not CREDENTIALS_PATH.exists():
        return (
            "Google Calendar credentials were not found. "
            "Please complete the Calendar setup."
        )

    try:
        calendar_service = get_calendar_service()

        event_body = build_calendar_event_body(
            event_title,
            start_datetime,
            duration_minutes,
        )

        created_event = (
            calendar_service.events()
            .insert(
                calendarId="primary",
                body=event_body,
            )
            .execute()
        )

        event_time = start_datetime.strftime(
            "%A at %I:%M %p"
        )

        print(
            "Created Google Calendar event:",
            created_event.get("htmlLink", ""),
        )

        return (
            "Calendar event created. "
            f"{event_title}, {event_time}."
        )

    except HttpError as error:
        print("Google Calendar API error:", error)
        return "I could not create the Google Calendar event."

    except Exception as error:
        print("Google Calendar error:", error)
        return "I could not connect to your Google Calendar."


if __name__ == "__main__":
    print(get_today_availability())
