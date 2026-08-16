import sys
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from wake_audio_session import (
    capture_command_audio,
    register_wake_stream,
    submit_wake_audio,
    suspend_wake_stream,
)


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
    def test_shared_stream_captures_speech_until_pause(self):
        def produce():
            time.sleep(0.02)
            frames = (
                [np.zeros(1280, dtype=np.int16)] * 7
                + [np.full(1280, 1200, dtype=np.int16)] * 3
                + [np.zeros(1280, dtype=np.int16)] * 12
            )
            for frame in frames:
                submit_wake_audio(frame)

        producer = threading.Thread(target=produce)
        producer.start()
        pcm = capture_command_audio(timeout_seconds=1, phrase_time_limit=2)
        producer.join()
        self.assertGreater(len(pcm), 0)
        self.assertEqual(0, len(pcm) % 2)

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
