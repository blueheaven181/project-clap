import sys
import threading
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_FOLDER / "src"))

import greeting


class SpeechPausePolicyTests(unittest.TestCase):
    def test_stopped_speech_status_is_exposed_for_callers(self):
        with patch.object(greeting, "_speech_stopped", True):
            self.assertTrue(greeting.was_speech_stopped())

        with patch.object(greeting, "_speech_stopped", False):
            self.assertFalse(greeting.was_speech_stopped())

    def test_speech_playback_is_serialized(self):
        first_started = threading.Event()
        release_first = threading.Event()
        calls = []

        def fake_speak_locked(message):
            calls.append(message)
            if message == "first":
                first_started.set()
                release_first.wait(timeout=1)

        with patch("greeting._speak_locked", side_effect=fake_speak_locked):
            first = threading.Thread(target=greeting.speak, args=("first",))
            second = threading.Thread(target=greeting.speak, args=("second",))
            first.start()
            self.assertTrue(first_started.wait(timeout=1))
            second.start()
            self.assertEqual(calls, ["first"])
            release_first.set()
            first.join(timeout=1)
            second.join(timeout=1)

        self.assertEqual(calls, ["first", "second"])

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
