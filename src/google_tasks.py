from datetime import datetime, timedelta
import re

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from google_auth import CREDENTIALS_PATH, get_google_credentials
from google_calendar import ABU_DHABI_TIMEZONE


DEFAULT_TASK_LIST = "@default"


def is_task_read_request(command):
    """Return True for supported requests to read pending Google Tasks."""

    normalized = command.strip().lower()
    return "task" in normalized and any(
        phrase in normalized
        for phrase in {
            "what tasks",
            "tasks do i have",
            "tasks are due today",
            "read my pending tasks",
            "pending tasks",
        }
    )


def get_tasks_service():
    """Build an authorized Google Tasks service."""

    return build("tasks", "v1", credentials=get_google_credentials())


def parse_task_creation_request(command):
    """Parse a request to add a task, optionally due today or tomorrow."""

    match = re.match(
        r"^\s*(?:please\s+)?add\s+(.+?)\s+to\s+(?:my\s+)?tasks?"
        r"(?:\s+(?:due\s+)?(today|tomorrow))?\s*[.!?]?\s*$",
        command,
        flags=re.IGNORECASE,
    )
    if not match:
        return None

    title = match.group(1).strip(" ,.-")
    if not title:
        return None

    due_date = None
    date_word = match.group(2)
    if date_word:
        due_date = datetime.now(ABU_DHABI_TIMEZONE).date()
        if date_word.lower() == "tomorrow":
            due_date += timedelta(days=1)

    return {"title": title, "due_date": due_date}


def build_task_body(title, due_date=None):
    """Build a Google Tasks payload without changing the supplied title."""

    if not title or not title.strip():
        raise ValueError("Task title must not be empty.")

    body = {"title": title}
    if due_date is not None:
        body["due"] = f"{due_date.isoformat()}T00:00:00.000Z"
    return body


def _parse_task_due_date(task):
    due_value = task.get("due")
    if not due_value:
        return None
    return datetime.fromisoformat(due_value.replace("Z", "+00:00")).date()


def get_pending_tasks(due_today=False):
    """Read incomplete tasks from the user's default task list."""

    if not CREDENTIALS_PATH.exists():
        return "Google credentials were not found. Please complete the Google setup."

    try:
        service = get_tasks_service()
        tasks = []
        page_token = None

        while True:
            result = (
                service.tasks()
                .list(
                    tasklist=DEFAULT_TASK_LIST,
                    showCompleted=False,
                    showDeleted=False,
                    maxResults=100,
                    pageToken=page_token,
                )
                .execute()
            )
            tasks.extend(result.get("items", []))
            page_token = result.get("nextPageToken")
            if not page_token:
                break

        tasks = [task for task in tasks if task.get("status") != "completed"]
        if due_today:
            today = datetime.now(ABU_DHABI_TIMEZONE).date()
            tasks = [task for task in tasks if _parse_task_due_date(task) == today]

        if not tasks:
            if due_today:
                return "You have no pending tasks due today."
            return "You have no pending tasks."

        spoken_tasks = []
        for task in tasks:
            title = task.get("title") or "Untitled task"
            due_date = _parse_task_due_date(task)
            if due_date:
                spoken_tasks.append(
                    f"{title}, due {due_date.strftime('%A, %B %d')}"
                )
            else:
                spoken_tasks.append(title)

        introduction = (
            "Your pending tasks due today are "
            if due_today
            else "Your pending tasks are "
        )
        return introduction + ". ".join(spoken_tasks) + "."

    except HttpError as error:
        print("Google Tasks API error:", error)
        return "I could not retrieve your Google Tasks."
    except Exception as error:
        print("Google Tasks error:", error)
        return "I could not connect to Google Tasks."


def create_task(title, due_date=None):
    """Create a new task in the default list after router confirmation."""

    if not CREDENTIALS_PATH.exists():
        return "Google credentials were not found. Please complete the Google setup."

    try:
        body = build_task_body(title, due_date)
        (
            get_tasks_service()
            .tasks()
            .insert(tasklist=DEFAULT_TASK_LIST, body=body)
            .execute()
        )

        if due_date:
            return f"Task created. {title}, due {due_date.strftime('%A, %B %d')}."
        return f"Task created. {title}."
    except HttpError as error:
        print("Google Tasks API error:", error)
        return "I could not create the Google Task."
    except Exception as error:
        print("Google Tasks error:", error)
        return "I could not connect to Google Tasks."
