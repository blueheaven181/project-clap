"""Resolve CLAP's wake-word model with a production-safe local override."""

import json
from pathlib import Path


DEFAULT_THRESHOLD = 0.30
MINIMUM_THRESHOLD = 0.30


def production_model_path(project_folder):
    return Path(project_folder) / "models" / "wake_words" / "hey_Clap.onnx"


def load_wake_word_selection(project_folder, config_path=None):
    project_folder = Path(project_folder)
    production = production_model_path(project_folder)
    selection = {
        "model_path": production,
        "threshold": DEFAULT_THRESHOLD,
        "source": "production",
        "warning": None,
    }
    config_path = Path(config_path or project_folder / "config" / "wake_word.local.json")

    if not config_path.exists():
        return selection

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        if not config.get("enabled", False):
            return selection

        configured = Path(config["model_path"])
        if not configured.is_absolute():
            configured = project_folder / configured
        configured = configured.resolve()
        threshold = float(config.get("threshold", DEFAULT_THRESHOLD))

        if threshold < MINIMUM_THRESHOLD:
            raise ValueError(
                f"threshold {threshold} is below guarded minimum {MINIMUM_THRESHOLD}"
            )
        if not configured.is_file():
            raise FileNotFoundError(f"candidate model not found: {configured}")

        selection.update(
            model_path=configured,
            threshold=threshold,
            source="local_candidate",
        )
    except (KeyError, TypeError, ValueError, OSError, json.JSONDecodeError) as error:
        selection["warning"] = str(error)

    return selection
