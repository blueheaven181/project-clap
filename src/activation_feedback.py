"""Minimal, local activation feedback for CLAP."""

import json
import math
import struct
import wave
import winsound
from datetime import datetime
from io import BytesIO
from pathlib import Path


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
STATE_PATH = PROJECT_FOLDER / "data" / "private" / "activation_greetings.json"


def get_day_period(hour):
    if hour < 12:
        return "morning"
    if hour < 18:
        return "afternoon"
    return "evening"


def should_speak_period_greeting(now=None, path=STATE_PATH):
    """Return True once per local calendar date and day period."""

    now = now or datetime.now()
    period = get_day_period(now.hour)
    marker = {"date": now.date().isoformat(), "period": period}
    try:
        previous = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        previous = {}
    if previous == marker:
        return False
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(marker), encoding="utf-8")
    return True


def play_activation_tone():
    """Play a short, gentle in-memory tone without creating an audio file."""

    sample_rate = 16000
    duration = 0.08
    frames = []
    for index in range(int(sample_rate * duration)):
        progress = index / (sample_rate * duration)
        envelope = math.sin(math.pi * progress) ** 2
        sample = int(32767 * 0.10 * envelope * math.sin(2 * math.pi * 660 * index / sample_rate))
        frames.append(struct.pack("<h", sample))
    audio = BytesIO()
    with wave.open(audio, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(b"".join(frames))
    # Memory playback is synchronous by default; Python exposes SND_ASYNC but
    # no SND_SYNC constant.
    winsound.PlaySound(audio.getvalue(), winsound.SND_MEMORY)


def acknowledge_activation(speak, greeting, now=None, path=STATE_PATH):
    if should_speak_period_greeting(now=now, path=path):
        speak(f"{greeting()}.")
        return "greeting"
    speak("Yes, Marc?")
    return "personal_acknowledgement"
