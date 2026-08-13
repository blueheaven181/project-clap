import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_FOLDER / "src"))

import activation_feedback


class ActivationFeedbackTests(unittest.TestCase):
    @patch("activation_feedback.winsound.PlaySound")
    def test_tone_uses_supported_synchronous_memory_flag(self, play_sound):
        activation_feedback.play_activation_tone()
        audio, flags = play_sound.call_args.args
        self.assertTrue(audio.startswith(b"RIFF"))
        self.assertEqual(activation_feedback.winsound.SND_MEMORY, flags)

    def test_period_boundaries(self):
        self.assertEqual("morning", activation_feedback.get_day_period(11))
        self.assertEqual("afternoon", activation_feedback.get_day_period(12))
        self.assertEqual("evening", activation_feedback.get_day_period(18))

    def test_greeting_is_once_per_period(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            morning = datetime(2026, 8, 13, 9)
            self.assertTrue(
                activation_feedback.should_speak_period_greeting(morning, path)
            )
            self.assertFalse(
                activation_feedback.should_speak_period_greeting(morning, path)
            )
            afternoon = datetime(2026, 8, 13, 13)
            self.assertTrue(
                activation_feedback.should_speak_period_greeting(afternoon, path)
            )

    @patch("activation_feedback.play_activation_tone")
    def test_later_activation_uses_personal_acknowledgement(self, tone):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            now = datetime(2026, 8, 13, 13)
            speak = unittest.mock.Mock()
            greeting = unittest.mock.Mock(return_value="Good afternoon Marc")
            self.assertEqual(
                "greeting",
                activation_feedback.acknowledge_activation(
                    speak, greeting, now, path
                ),
            )
            self.assertEqual(
                "personal_acknowledgement",
                activation_feedback.acknowledge_activation(
                    speak, greeting, now, path
                ),
            )
            self.assertEqual(
                [
                    unittest.mock.call("Good afternoon Marc."),
                    unittest.mock.call("Yes, Marc?"),
                ],
                speak.call_args_list,
            )
            tone.assert_not_called()


if __name__ == "__main__":
    unittest.main()
