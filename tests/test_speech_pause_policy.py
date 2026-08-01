import sys
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_FOLDER / "src"))

import greeting


class SpeechPausePolicyTests(unittest.TestCase):
    @patch("greeting._pause_speaking")
    def test_voice_command_cannot_pause_speech(self, pause_mock):
        paused = greeting.request_speech_control(trigger="voice_command")

        self.assertFalse(paused)
        pause_mock.assert_not_called()

    @patch("greeting._pause_speaking")
    def test_speech_activity_cannot_pause_speech(self, pause_mock):
        paused = greeting.request_speech_control(trigger="speech")

        self.assertFalse(paused)
        pause_mock.assert_not_called()

    @patch("greeting._speech_control_event")
    @patch("greeting._pause_speaking")
    @patch("greeting.is_speaking", return_value=True)
    def test_double_clap_can_request_pause(
        self,
        _is_speaking,
        pause_mock,
        event_mock,
    ):
        event_mock.is_set.return_value = False

        paused = greeting.request_speech_control(trigger="double_clap")

        self.assertTrue(paused)
        pause_mock.assert_called_once_with()
        event_mock.set.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
