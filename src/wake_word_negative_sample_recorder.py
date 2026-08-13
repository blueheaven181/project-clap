"""Record labeled negative wake-word samples without loading Project CLAP."""

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import sounddevice as sd

from wake_word_sample_recorder import (
    CHANNELS,
    DEFAULT_DEVICE,
    DTYPE,
    OUTPUT_ROOT,
    SAMPLE_RATE,
    write_wav,
)


SAMPLES_PER_CATEGORY = 20
DURATION_SECONDS = 2.0
CATEGORIES = (
    (
        "ordinary_speech",
        "Speak naturally near the microphone without addressing CLAP.",
    ),
    (
        "speaker_playback",
        "Play ordinary conversation through the usual nearby speaker volume.",
    ),
)
EXCLUDED_PHRASES = (
    "Hey CLAP",
    "CLAP",
    "Hey app",
    "Hey clap",
    "Okay CLAP",
)


def record_negative_samples(device=DEFAULT_DEVICE):
    """Interactively capture two explicitly labeled negative categories."""

    device_info = sd.query_devices(device, "input")
    session_name = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_folder = OUTPUT_ROOT / "negative" / session_name
    metadata_path = session_folder / "metadata.jsonl"

    print("Wake-word negative-sample recorder")
    print(f"Microphone: {device_info['name']} (index {device})")
    print(
        f"Plan: {SAMPLES_PER_CATEGORY} ordinary-speech samples and "
        f"{SAMPLES_PER_CATEGORY} speaker-playback samples"
    )
    print(f"Duration: {DURATION_SECONDS:.1f} seconds per sample")
    print(f"Local output: {session_folder}")
    print("Exclude the wake phrase and close variants from every sample:")
    for phrase in EXCLUDED_PHRASES:
        print(f"- {phrase}")
    print("No recording starts until you press Enter for that sample.")
    print("Type Q and press Enter at any sample prompt to stop safely.")

    confirmation = input("Type START NEGATIVE CAPTURE to begin: ").strip()
    if confirmation != "START NEGATIVE CAPTURE":
        print("Capture cancelled. No audio was recorded.")
        return None

    exclusion_confirmation = input(
        "Type EXCLUSIONS CONFIRMED after checking all speech/playback: "
    ).strip()
    if exclusion_confirmation != "EXCLUSIONS CONFIRMED":
        print("Capture cancelled. No audio was recorded.")
        return None

    session_folder.mkdir(parents=True, exist_ok=False)
    stopped = False

    for category, instruction in CATEGORIES:
        category_folder = session_folder / category
        category_folder.mkdir()
        print(f"\nCategory: {category}")
        print(instruction)

        for index in range(1, SAMPLES_PER_CATEGORY + 1):
            response = input(
                f"{category} {index}/{SAMPLES_PER_CATEGORY}: "
                "press Enter to record (Q stops): "
            ).strip()
            if response.lower() == "q":
                stopped = True
                break

            print("Recording now...")
            audio = sd.rec(
                int(DURATION_SECONDS * SAMPLE_RATE),
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                dtype=DTYPE,
                device=device,
            )
            sd.wait()

            filename = f"{category}_{index:03d}.wav"
            relative_file = Path(category) / filename
            write_wav(session_folder / relative_file, audio)

            metadata = {
                "file": relative_file.as_posix(),
                "label": "hey_clap_negative",
                "category": category,
                "sample_rate": SAMPLE_RATE,
                "channels": CHANNELS,
                "duration_seconds": DURATION_SECONDS,
                "device_index": device,
                "device_name": device_info["name"],
                "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
                "wake_phrase_excluded": True,
            }
            with metadata_path.open("a", encoding="utf-8") as metadata_file:
                metadata_file.write(json.dumps(metadata) + "\n")

            print(f"Saved {relative_file}")
            time.sleep(0.3)

        if stopped:
            break

    saved_count = len(list(session_folder.rglob("*.wav")))
    print(f"Capture complete: {saved_count} negative sample(s) saved locally.")
    print(f"Session folder: {session_folder}")
    return session_folder


if __name__ == "__main__":
    try:
        record_negative_samples()
    except KeyboardInterrupt:
        print("\nCapture stopped. Existing samples were kept locally.")
    except Exception as error:
        print("Recorder error:", error)
