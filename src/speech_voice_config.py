"""Load a private local Edge TTS voice preference with safe defaults."""

import json
import re
from pathlib import Path
from runtime_paths import data_path


DEFAULT_VOICE = "en-US-GuyNeural"
DEFAULT_RATE = "+8%"
CONFIG_PATH = data_path("config", "speech_voice.local.json")

_VOICE_PATTERN = re.compile(r"^[a-z]{2,3}-[A-Z]{2}-[A-Za-z]+(?:Multilingual)?Neural$")
_RATE_PATTERN = re.compile(r"^[+-](?:[0-9]|[1-4][0-9]|50)%$")


def load_speech_voice_config(path=CONFIG_PATH):
    config = {
        "voice": DEFAULT_VOICE,
        "rate": DEFAULT_RATE,
        "source": "default",
        "warning": None,
    }
    path = Path(path)
    if not path.exists():
        return config

    try:
        local = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(local, dict):
            raise ValueError("speech voice config must be a JSON object")
        if not local.get("enabled", False):
            return config

        voice = local.get("voice")
        rate = local.get("rate")
        if not isinstance(voice, str) or not _VOICE_PATTERN.fullmatch(voice):
            raise ValueError("invalid Edge neural voice name")
        if not isinstance(rate, str) or not _RATE_PATTERN.fullmatch(rate):
            raise ValueError("rate must be between -50% and +50%")

        config.update(voice=voice, rate=rate, source="local", warning=None)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        config["warning"] = str(error)

    return config
