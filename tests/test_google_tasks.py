import sys
import unittest
from datetime import date, datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_FOLDER / "src"))

import command_router
import google_auth
import google_tasks
from google_tasks import (
    DEFAULT_TASK_LIST,
    build_task_body,
    get_requested_task_due_day,
    get_pending_tasks,
    is_task_read_request,
    parse_task_creation_request,
)


class TaskIntentAndParsingTests(unittest.TestCase):
    def test_read_request_reaches_trusted_command_gate(self):
        for command in ("What tasks do I have?", "What task do I have?"):
            with self.subTest(command=command):
                self.assertTrue(
                    command_router.is_google_tasks_request(command)
                )

    def test_create_request_reaches_trusted_command_gate(self):
        self.assertTrue(
            command_router.is_google_tasks_request(
                "Add buy groceries to my tasks."
            )
        )

    def test_supported_read_intents_are_recognized(self):
        for command in (
            "What tasks do I have?",
            "What task do I have?",
            "What tasks are due today?",
            "What task is due today?",
            "Do I have any tasks?",
            "Do I have task today?",
            "What are my task today?",
            "What are my task tomorrow?",
            "Read my pending tasks.",
        ):
            with self.subTest(command=command):
                self.assertTrue(is_task_read_request(command))

    def test_spoken_date_variants_request_correct_due_day(self):
        commands = {
            "What tasks are due today?": "today",
            "What task is due today?": "today",
            "Do I have task today?": "today",
            "What are my task today?": "today",
            "What are my task tomorrow?": "tomorrow",
            "Do I have tasks due tomorrow?": "tomorrow",
        }
        for command, expected_day in commands.items():
            with self.subTest(command=command):
                self.assertEqual(
                    get_requested_task_due_day(command), expected_day
                )

    def test_task_title_is_preserved(self):
        request = parse_task_creation_request(
            "Add Buy LEGO set to my tasks."
        )
        self.assertEqual(request, {"title": "Buy LEGO set", "due_date": None})

    @patch("google_tasks.datetime")
    def test_due_today_uses_abu_dhabi_date(self, mock_datetime):
        mock_datetime.now.return_value.date.return_value = date(2026, 8, 1)
        request = parse_task_creation_request(
            "Add submit report to my tasks due today"
        )
        self.assertEqual(request["title"], "submit report")
        self.assertEqual(request["due_date"], date(2026, 8, 1))
        mock_datetime.now.assert_called_once_with(google_tasks.ABU_DHABI_TIMEZONE)

    def test_unrelated_add_command_is_not_a_task_request(self):
        self.assertIsNone(
            parse_task_creation_request("Add workout tomorrow at 7 PM")
        )

    def test_task_payload_preserves_title_and_due_date(self):
        self.assertEqual(
            build_task_body("Buy LEGO set", date(2026, 8, 2)),
            {
                "title": "Buy LEGO set",
                "due": "2026-08-02T00:00:00.000Z",
            },
        )


class TaskApiTests(unittest.TestCase):
    @patch("google_tasks.CREDENTIALS_PATH")
    @patch("google_tasks.get_tasks_service")
    def test_tomorrow_filter_excludes_other_pending_tasks(
        self, get_service, path
    ):
        path.exists.return_value = True
        today = datetime.now(google_tasks.ABU_DHABI_TIMEZONE).date()
        tomorrow = today + timedelta(days=1)
        service = get_service.return_value
        service.tasks.return_value.list.return_value.execute.return_value = {
            "items": [
                {
                    "title": "Tomorrow task",
                    "status": "needsAction",
                    "due": f"{tomorrow.isoformat()}T00:00:00.000Z",
                },
                {
                    "title": "Today task",
                    "status": "needsAction",
                    "due": f"{today.isoformat()}T00:00:00.000Z",
                },
                {"title": "Undated task", "status": "needsAction"},
            ]
        }

        report = get_pending_tasks(due_day="tomorrow")

        self.assertIn("Tomorrow task", report)
        self.assertNotIn("Today task", report)
        self.assertNotIn("Undated task", report)

    @patch("google_tasks.CREDENTIALS_PATH")
    @patch("google_tasks.get_tasks_service")
    def test_reads_pending_tasks_from_default_list(self, get_service, path):
        path.exists.return_value = True
        service = get_service.return_value
        service.tasks.return_value.list.return_value.execute.return_value = {
            "items": [
                {"title": "Buy groceries", "status": "needsAction"},
                {"title": "Old task", "status": "completed"},
            ]
        }

        report = get_pending_tasks()

        self.assertEqual(report, "Your pending tasks are Buy groceries.")
        service.tasks.return_value.list.assert_called_once_with(
            tasklist=DEFAULT_TASK_LIST,
            showCompleted=False,
            showDeleted=False,
            maxResults=100,
            pageToken=None,
        )

    @patch("google_tasks.CREDENTIALS_PATH")
    @patch("google_tasks.get_tasks_service")
    def test_empty_task_list_has_clear_response(self, get_service, path):
        path.exists.return_value = True
        get_service.return_value.tasks.return_value.list.return_value.execute.return_value = {}
        self.assertEqual(get_pending_tasks(), "You have no pending tasks.")

    @patch("google_tasks.CREDENTIALS_PATH")
    def test_missing_credentials_has_setup_response(self, path):
        path.exists.return_value = False
        self.assertIn("credentials were not found", get_pending_tasks())

    @patch("google_tasks.CREDENTIALS_PATH")
    @patch("google_tasks.get_tasks_service", side_effect=RuntimeError("offline"))
    def test_api_failure_is_handled(self, _get_service, path):
        path.exists.return_value = True
        self.assertEqual(
            get_pending_tasks(),
            "I could not connect to Google Tasks.",
        )

    @patch("google_tasks.CREDENTIALS_PATH")
    @patch("google_tasks.get_tasks_service")
    def test_create_uses_default_list_and_exact_payload(self, get_service, path):
        path.exists.return_value = True
        service = get_service.return_value
        service.tasks.return_value.insert.return_value.execute.return_value = {}

        result = google_tasks.create_task(
            "Buy LEGO set", date(2026, 8, 2)
        )

        self.assertIn("Task created", result)
        service.tasks.return_value.insert.assert_called_once_with(
            tasklist=DEFAULT_TASK_LIST,
            body={
                "title": "Buy LEGO set",
                "due": "2026-08-02T00:00:00.000Z",
            },
        )


class TaskAuthorizationTests(unittest.TestCase):
    @patch("google_auth.TOKEN_PATH")
    @patch("google_auth.Credentials.from_authorized_user_file")
    @patch("google_auth.InstalledAppFlow.from_client_secrets_file")
    def test_missing_tasks_scope_requires_fresh_authorization(
        self, create_flow, load_credentials, token_path
    ):
        token_path.exists.return_value = True
        existing = MagicMock()
        existing.has_scopes.return_value = False
        load_credentials.return_value = existing
        replacement = MagicMock()
        replacement.to_json.return_value = "{}"
        create_flow.return_value.run_local_server.return_value = replacement

        result = google_auth.get_google_credentials()

        self.assertIs(result, replacement)
        create_flow.assert_called_once_with(
            str(google_auth.CREDENTIALS_PATH), google_auth.GOOGLE_SCOPES
        )
        create_flow.return_value.run_local_server.assert_called_once_with(
            port=0, prompt="consent"
        )
        existing.refresh.assert_not_called()

    @patch("google_auth.TOKEN_PATH")
    @patch("google_auth.Credentials.from_authorized_user_file")
    def test_expired_fully_scoped_token_is_refreshed(
        self, load_credentials, token_path
    ):
        token_path.exists.return_value = True
        credentials = MagicMock()
        credentials.has_scopes.return_value = True
        credentials.valid = False
        credentials.expired = True
        credentials.refresh_token = "refresh-token"
        credentials.to_json.return_value = "{}"
        load_credentials.return_value = credentials

        result = google_auth.get_google_credentials()

        self.assertIs(result, credentials)
        credentials.refresh.assert_called_once()
        token_path.write_text.assert_called_once_with("{}", encoding="utf-8")

    @patch("google_auth.TOKEN_PATH")
    @patch("google_auth.Credentials.from_authorized_user_file")
    @patch("google_auth.InstalledAppFlow.from_client_secrets_file")
    def test_failed_scope_upgrade_does_not_overwrite_token(
        self, create_flow, load_credentials, token_path
    ):
        token_path.exists.return_value = True
        existing = MagicMock()
        existing.has_scopes.return_value = False
        load_credentials.return_value = existing
        create_flow.return_value.run_local_server.side_effect = RuntimeError(
            "authorization cancelled"
        )

        with self.assertRaises(RuntimeError):
            google_auth.get_google_credentials()

        token_path.write_text.assert_not_called()


class TaskRoutingTests(unittest.TestCase):
    def test_mixed_yes_and_no_is_not_clear_confirmation(self):
        self.assertFalse(
            command_router.is_clear_task_creation_confirmation("yes yes no")
        )

    def test_do_not_create_is_not_confirmation(self):
        self.assertFalse(
            command_router.is_clear_task_creation_confirmation(
                "do not create it"
            )
        )

    @patch("command_router.speak")
    @patch("command_router.create_task")
    @patch("command_router.listen_until_response", return_value="no")
    def test_task_creation_requires_confirmation(self, _listen, create, _speak):
        self.assertTrue(
            command_router.route_command("Add buy groceries to my tasks")
        )
        create.assert_not_called()

    @patch("command_router.speak")
    @patch("command_router.create_task", return_value="Task created.")
    @patch("command_router.listen_until_response", return_value="yes")
    def test_confirmed_task_is_created(self, _listen, create, _speak):
        command_router.route_command("Add Buy LEGO set to my tasks")
        create.assert_called_once_with("Buy LEGO set", None)

    @patch("command_router.speak")
    @patch("command_router.create_task")
    @patch("command_router.listen_until_response", return_value="")
    def test_failed_confirmation_does_not_create(self, _listen, create, _speak):
        command_router.route_command("Add buy groceries to my tasks")
        create.assert_not_called()

    @patch("command_router.speak")
    @patch("command_router.create_task")
    @patch("command_router.listen_until_response", return_value="yes yes no")
    def test_mixed_confirmation_does_not_create(self, _listen, create, _speak):
        command_router.route_command("Add buy groceries to my tasks")
        create.assert_not_called()

    @patch("command_router.speak")
    @patch("command_router.get_pending_tasks", return_value="No tasks.")
    def test_due_today_routes_with_filter(self, get_tasks, _speak):
        for command in (
            "What tasks are due today?",
            "Do I have task today?",
            "What are my task today?",
            "What task is due today?",
        ):
            with self.subTest(command=command):
                get_tasks.reset_mock()
                self.assertTrue(command_router.route_command(command))
                get_tasks.assert_called_once_with(due_day="today")

    @patch("command_router.speak")
    @patch("command_router.get_pending_tasks", return_value="No tasks.")
    def test_tomorrow_routes_with_filter(self, get_tasks, _speak):
        self.assertTrue(
            command_router.route_command("What are my task tomorrow?")
        )
        get_tasks.assert_called_once_with(due_day="tomorrow")


if __name__ == "__main__":
    unittest.main()
