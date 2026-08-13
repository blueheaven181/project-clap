"""Optional local-first streaming voice path for conversational mode."""

import json
import re
from pathlib import Path

import requests


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_FOLDER / "config" / "conversation_voice.local.json"

DEFAULT_CONFIG = {
    "enabled": False,
    "backend": "ollama_sentence_stream",
    "minimum_chunk_characters": 48,
    "maximum_chunk_characters": 180,
}


def load_conversation_voice_config(path=CONFIG_PATH):
    """Load an explicit local experiment config, or return safe defaults."""

    config = dict(DEFAULT_CONFIG)
    if not path.exists():
        return config

    try:
        local_config = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print("Conversation voice config error:", type(error).__name__)
        return config

    if not isinstance(local_config, dict):
        return config

    if isinstance(local_config.get("enabled"), bool):
        config["enabled"] = local_config["enabled"]

    if local_config.get("backend") == "ollama_sentence_stream":
        config["backend"] = local_config["backend"]

    for key in ("minimum_chunk_characters", "maximum_chunk_characters"):
        value = local_config.get(key)
        if isinstance(value, int) and value > 0:
            config[key] = value

    config["maximum_chunk_characters"] = max(
        config["maximum_chunk_characters"],
        config["minimum_chunk_characters"],
    )
    return config


def _split_ready_chunks(buffer, minimum_characters, maximum_characters):
    """Return complete voice-friendly chunks and the remaining text."""

    chunks = []
    sentence_pattern = re.compile(r"(?<=[.!?])\s+")

    while len(buffer) >= minimum_characters:
        boundaries = [match.end() for match in sentence_pattern.finditer(buffer)]
        usable_boundaries = [
            boundary for boundary in boundaries if boundary <= maximum_characters
        ]

        if usable_boundaries:
            split_at = usable_boundaries[-1]
        elif len(buffer) >= maximum_characters:
            space_at = buffer.rfind(" ", 0, maximum_characters + 1)
            split_at = space_at + 1 if space_at >= minimum_characters else maximum_characters
        else:
            break

        chunk = buffer[:split_at].strip()
        buffer = buffer[split_at:].lstrip()
        if chunk:
            chunks.append(chunk)

    return chunks, buffer


def stream_ollama_sentences(
    url,
    model,
    messages,
    options,
    minimum_characters=48,
    maximum_characters=180,
    timeout=120,
):
    """Yield sentence-sized text chunks from Ollama's JSON-lines stream."""

    buffer = ""
    with requests.post(
        url,
        json={
            "model": model,
            "messages": messages,
            "stream": True,
            "options": options,
        },
        stream=True,
        timeout=timeout,
    ) as response:
        response.raise_for_status()

        for line in response.iter_lines():
            if not line:
                continue

            event = json.loads(line.decode("utf-8"))
            token = event.get("message", {}).get("content", "")
            if token:
                buffer += token

            ready, buffer = _split_ready_chunks(
                buffer,
                minimum_characters,
                maximum_characters,
            )
            yield from ready

        final_chunk = buffer.strip()
        if final_chunk:
            yield final_chunk


def stream_and_speak_conversation(
    user_message,
    conversation_history,
    url,
    model,
    options,
    speak,
    direct_address,
    config,
):
    """Stream one local response and speak it in chunks.

    Return ``None`` only when streaming fails before any speech, allowing the
    caller to use the established non-streaming fallback without duplication.
    """

    user_entry = {"role": "user", "content": user_message}
    conversation_history.append(user_entry)
    spoken_chunks = []

    try:
        chunks = stream_ollama_sentences(
            url=url,
            model=model,
            messages=conversation_history,
            options=options,
            minimum_characters=config["minimum_chunk_characters"],
            maximum_characters=config["maximum_chunk_characters"],
        )

        for chunk in chunks:
            spoken_chunk = direct_address(chunk)
            spoken_chunks.append(spoken_chunk)
            if not speak(spoken_chunk):
                break

    except (requests.RequestException, json.JSONDecodeError, UnicodeDecodeError) as error:
        if not spoken_chunks:
            if conversation_history and conversation_history[-1] is user_entry:
                conversation_history.pop()
            print("Experimental conversation voice fallback:", type(error).__name__)
            return None
        print("Experimental conversation voice ended early:", type(error).__name__)

    assistant_message = " ".join(spoken_chunks).strip()
    if assistant_message:
        conversation_history.append(
            {"role": "assistant", "content": assistant_message}
        )
    return assistant_message
