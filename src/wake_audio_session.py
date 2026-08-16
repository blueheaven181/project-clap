"""Coordinate exclusive microphone access between wake and speech listeners."""

import threading
import time
import queue
from contextlib import contextmanager

import numpy as np


_lock = threading.RLock()
_wake_stream = None
_command_capture_active = False
_command_audio = queue.Queue(maxsize=256)


def register_wake_stream(stream):
    global _wake_stream
    with _lock:
        _wake_stream = stream


def submit_wake_audio(indata):
    """Forward one wake-stream frame to packaged command capture when active."""

    if not _command_capture_active:
        return False
    frame = np.asarray(indata, dtype=np.int16).flatten().copy()
    try:
        _command_audio.put_nowait(frame)
    except queue.Full:
        try:
            _command_audio.get_nowait()
        except queue.Empty:
            pass
        _command_audio.put_nowait(frame)
    return True


def capture_command_audio(
    timeout_seconds=5,
    phrase_time_limit=8,
    pause_threshold=0.8,
    sample_rate=16000,
    chunk_size=1280,
):
    """Capture speech from CLAP's existing wake stream as signed 16-bit PCM."""

    global _command_capture_active
    while True:
        try:
            _command_audio.get_nowait()
        except queue.Empty:
            break
    _command_capture_active = True
    try:
        ambient_chunks = max(1, round(0.5 * sample_rate / chunk_size))
        ambient = [_command_audio.get(timeout=2) for _ in range(ambient_chunks)]
        ambient_levels = [
            np.sqrt(np.mean(frame.astype(np.float32) ** 2)) for frame in ambient
        ]
        # A user often starts speaking immediately after the acknowledgement.
        # Use the quiet half of calibration instead of allowing those first
        # spoken frames to raise the threshold above the user's own voice.
        quiet_level = float(np.percentile(ambient_levels, 35))
        noise = min(1200.0, max(180.0, quiet_level * 1.8))
        wait_chunks = max(1, round(timeout_seconds * sample_rate / chunk_size))
        frames = []
        for _ in range(wait_chunks):
            frame = _command_audio.get(timeout=2)
            rms = float(np.sqrt(np.mean(frame.astype(np.float32) ** 2)))
            if rms >= noise:
                frames.append(frame)
                break
        if not frames:
            raise TimeoutError("No response was heard.")

        max_chunks = max(1, round(phrase_time_limit * sample_rate / chunk_size))
        silent_limit = max(1, round(pause_threshold * sample_rate / chunk_size))
        silent_chunks = 0
        for _ in range(max_chunks - 1):
            frame = _command_audio.get(timeout=2)
            frames.append(frame)
            rms = float(np.sqrt(np.mean(frame.astype(np.float32) ** 2)))
            silent_chunks = silent_chunks + 1 if rms < noise else 0
            if silent_chunks >= silent_limit:
                break
        return np.concatenate(frames).astype(np.int16).tobytes()
    finally:
        _command_capture_active = False


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
