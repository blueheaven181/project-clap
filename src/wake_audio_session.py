"""Coordinate exclusive microphone access between wake and speech listeners."""

import threading
import time
from contextlib import contextmanager


_lock = threading.RLock()
_wake_stream = None


def register_wake_stream(stream):
    global _wake_stream
    with _lock:
        _wake_stream = stream


@contextmanager
def suspend_wake_stream():
    """Pause the active wake stream while another audio backend listens."""

    with _lock:
        stream = _wake_stream
        was_active = bool(stream is not None and stream.active)
        if was_active:
            stream.stop()
    try:
        yield
    finally:
        with _lock:
            if was_active:
                last_error = None
                for delay in (0.25, 0.5, 1.0):
                    time.sleep(delay)
                    try:
                        stream.start()
                        last_error = None
                        break
                    except Exception as error:
                        last_error = error
                if last_error is not None:
                    # Do not discard speech that was already captured merely
                    # because Windows delayed releasing the audio driver.
                    print(
                        "Wake microphone resume error:",
                        last_error,
                        flush=True,
                    )
