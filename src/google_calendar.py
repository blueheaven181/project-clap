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
        credentials = get_calendar_credentials()
        calendar_service = build(
            "calendar",
            "v3",
            credentials=credentials,
        )

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

        result = (
            calendar_service.events()
            .list(
                calendarId="primary",
                timeMin=start_of_day.isoformat(),
                timeMax=end_of_day.isoformat(),
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = result.get("items", [])

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


if __name__ == "__main__":
    print(get_todays_calendar())