import sys
import unittest
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from wake_audio_session import register_wake_stream, suspend_wake_stream


class FakeStream:
    def __init__(self, active=True, start_failures=0, start_error=OSError):
        self.active = active
        self.calls = []
        self.start_failures = start_failures
        self.start_error = start_error

    def stop(self):
        self.calls.append("stop")
        self.active = False

    def start(self):
        self.calls.append("start")
        if self.start_failures:
            self.start_failures -= 1
            raise self.start_error("driver still releasing")
        self.active = True


class WakeAudioSessionTests(unittest.TestCase):
    @patch("wake_audio_session.time.sleep")
    def test_active_wake_stream_is_paused_and_resumed(self, _sleep):
        stream = FakeStream()
        register_wake_stream(stream)
        with suspend_wake_stream():
            self.assertFalse(stream.active)
        self.assertTrue(stream.active)
        self.assertEqual(["stop", "start"], stream.calls)

    @patch("wake_audio_session.time.sleep")
    def test_wake_stream_resume_retries_after_driver_delay(self, _sleep):
        stream = FakeStream(start_failures=1, start_error=RuntimeError)
        register_wake_stream(stream)
        with suspend_wake_stream():
            pass
        self.assertTrue(stream.active)
        self.assertEqual(["stop", "start", "start"], stream.calls)

    @patch("wake_audio_session.time.sleep")
    def test_inactive_wake_stream_is_not_started(self, _sleep):
        stream = FakeStream(active=False)
        register_wake_stream(stream)
        with suspend_wake_stream():
            pass
        self.assertEqual([], stream.calls)


if __name__ == "__main__":
    unittest.main()
