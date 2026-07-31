import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_FOLDER / "src"))

import command_router
from google_calendar import (
    ABU_DHABI_TIMEZONE,
    build_calendar_event_body,
    parse_calendar_event_request,
)


class CalendarParsingTests(unittest.TestCase):
    def test_seven_pm_is_parsed_in_abu_dhabi_time(self):
        request = parse_calendar_event_request(
            "add workout tomorrow at 7 PM"
        )

        self.assertEqual(request["start"].hour, 19)
        self.assertEqual(request["start"].tzinfo, ABU_DHABI_TIMEZONE)
        self.assertEqual(request["duration_minutes"], 60)

    def test_event_payload_preserves_seven_pm_abu_dhabi(self):
        start = datetime(2026, 8, 2, 15, 0, tzinfo=timezone.utc)

        payload = build_calendar_event_body("Workout", start)

        self.assertEqual(
            payload["start"],
            {
                "dateTime": "2026-08-02T19:00:00+04:00",
                "timeZone": "Asia/Dubai",
            },
        )
        self.assertEqual(
            payload["end"]["dateTime"],
            "2026-08-02T20:00:00+04:00",
        )
        self.assertTrue(payload["reminders"]["useDefault"])

    def test_event_payload_rejects_a_time_without_timezone(self):
        with self.assertRaises(ValueError):
            build_calendar_event_body(
                "Workout",
                datetime(2026, 8, 2, 19, 0),
            )


class CalendarRoutingTests(unittest.TestCase):
    @patch("command_router.speak")
    @patch("command_router.create_calendar_event")
    @patch("command_router.listen_until_response", return_value="no")
    def test_event_creation_requires_confirmation(
        self,
        _listen,
        create_event,
        _speak,
    ):
        recognized = command_router.route_command(
            "add workout tomorrow at 7 pm"
        )

        self.assertTrue(recognized)
        create_event.assert_not_called()

    @patch("command_router.speak")
    @patch(
        "command_router.create_calendar_event",
        return_value="Calendar event created.",
    )
    @patch("command_router.listen_until_response", return_value="yes")
    def test_confirmed_event_is_created(
        self,
        _listen,
        create_event,
        _speak,
    ):
        recognized = command_router.route_command(
            "add workout tomorrow at 7 pm"
        )

        self.assertTrue(recognized)
        create_event.assert_called_once()

    @patch("command_router.speak")
    @patch("command_router.get_weather", return_value="Sunny")
    def test_calendar_routing_does_not_block_other_commands(
        self,
        get_weather,
        _speak,
    ):
        recognized = command_router.route_command("weather")

        self.assertTrue(recognized)
        get_weather.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
