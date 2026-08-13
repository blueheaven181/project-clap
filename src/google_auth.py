from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from runtime_paths import data_path


CREDENTIALS_PATH = data_path("config", "credentials.json")
TOKEN_PATH = data_path("config", "token.json")

CALENDAR_SCOPE = "https://www.googleapis.com/auth/calendar.events"
TASKS_SCOPE = "https://www.googleapis.com/auth/tasks"
GOOGLE_SCOPES = [CALENDAR_SCOPE, TASKS_SCOPE]


def get_google_credentials():
    """Load Google credentials, requesting fresh consent for missing scopes."""

    credentials = None

    if TOKEN_PATH.exists():
        credentials = Credentials.from_authorized_user_file(str(TOKEN_PATH))

    has_required_scopes = bool(
        credentials and credentials.has_scopes(GOOGLE_SCOPES)
    )

    if credentials and has_required_scopes and not credentials.valid:
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            credentials = None

    if not credentials or not has_required_scopes:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(CREDENTIALS_PATH),
            GOOGLE_SCOPES,
        )
        credentials = flow.run_local_server(port=0, prompt="consent")

    if isinstance(TOKEN_PATH, Path):
        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_PATH.write_text(credentials.to_json(), encoding="utf-8")
    return credentials
