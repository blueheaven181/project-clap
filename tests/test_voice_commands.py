import sys
import unittest
from pathlib import Path
from unittest.mock import call, patch


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_FOLDER / "src"))

import voice_commands


class VoiceRetryTests(unittest.TestCase):
    @patch("voice_commands.time.sleep")
    @patch("voice_commands.speak")
    @patch("voice_commands.listen_for_response", return_value="")
    def test_attempt_limit_returns_to_caller(
        self,
        listen_mock,
        speak_mock,
        _sleep,
    ):
        response = voice_commands.listen_until_response(
            "Please try again.",
            max_attempts=3,
        )

        self.assertEqual("", response)
        self.assertEqual(3, listen_mock.call_count)
        self.assertEqual(2, speak_mock.call_count)

    @patch("voice_commands.time.sleep")
    @patch("voice_commands.speak")
    @patch(
        "voice_commands.listen_for_response",
        side_effect=["", "no"],
    )
    def test_recognized_response_stops_retrying(
        self,
        listen_mock,
        speak_mock,
        _sleep,
    ):
        response = voice_commands.listen_until_response(
            "Please say yes or no.",
            max_attempts=3,
            phrase_time_limit=4,
        )

        self.assertEqual("no", response)
        self.assertEqual(2, listen_mock.call_count)
        self.assertEqual(1, speak_mock.call_count)
        self.assertEqual(
            [
                call(phrase_time_limit=4, pause_threshold=0.8),
                call(phrase_time_limit=4, pause_threshold=0.8),
            ],
            listen_mock.call_args_list,
        )


if __name__ == "__main__":
    unittest.main()
