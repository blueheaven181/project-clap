from datetime import datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
]

ABU_DHABI_TIMEZONE = ZoneInfo("Asia/Dubai")

PROJECT_FOLDER = Path(__file__).resolve().parent.parent
CREDENTIALS_PATH = PROJECT_FOLDER / "config" / "credentials.json"
TOKEN_PATH = PROJECT_FOLDER / "config" / "token.json"


def get_calendar_credentials():
    """
    Load or create Google's read-only Calendar authorization.
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


if __name__ == "__main__":
    print(get_today_availability())