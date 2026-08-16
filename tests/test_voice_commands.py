import sys
import unittest
from pathlib import Path
from unittest.mock import call, patch


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_FOLDER / "src"))

import voice_commands


class PackagedRecognitionTests(unittest.TestCase):
    @patch("voice_commands.subprocess.Popen")
    @patch("voice_commands.requests.Session")
    def test_packaged_recognition_ignores_windows_proxy_settings(
        self, session_class, popen
    ):
        response = unittest.mock.MagicMock()
        response.text = '{"result":[{"alternative":[{"transcript":"system health"}],"final":true}]}'
        session_class.return_value.post.return_value = response
        popen.return_value.communicate.return_value = (b"flac", b"")
        popen.return_value.returncode = 0
        audio = voice_commands.sr.AudioData(b"\x00\x00" * 1600, 16000, 2)

        result = voice_commands.recognize_google_packaged(audio)

        self.assertEqual(result, "system health")
        self.assertFalse(session_class.return_value.trust_env)
        response.raise_for_status.assert_called_once_with()
        self.assertEqual(
            popen.call_args.kwargs["creationflags"],
            getattr(voice_commands.subprocess, "CREATE_NO_WINDOW", 0),
        )


class VoiceRetryTests(unittest.TestCase):
    def test_late_microphone_close_error_is_contained(self):
        microphone = unittest.mock.MagicMock()
        microphone.__exit__.side_effect = RuntimeError("driver release")
        self.assertFalse(voice_commands.close_microphone_safely(microphone))

    def test_repeated_stop_words_are_accepted(self):
        self.assertTrue(
            voice_commands.is_repeated_exact_word("stop stop", "stop")
        )

    def test_mixed_stop_words_are_rejected(self):
        self.assertFalse(
            voice_commands.is_repeated_exact_word("yes stop", "stop")
        )

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
