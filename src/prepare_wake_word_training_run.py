"""Prepare private wake-word manifests without playing or transcribing audio."""

import argparse
import hashlib
import json
import math
import random
import wave
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


SAMPLE_RATE = 16000
CHANNELS = 1
SAMPLE_WIDTH = 2
EXPECTED_DURATION_SECONDS = (2.0, 3.0)
SPLIT_SEED = 20260808


def inspect_wav(path):
    """Return technical signal metrics; never play or transcribe the clip."""

    with wave.open(str(path), "rb") as wav_file:
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        sample_rate = wav_file.getframerate()
        frame_count = wav_file.getnframes()
        raw_audio = wav_file.readframes(frame_count)

    samples = np.frombuffer(raw_audio, dtype="<i2").astype(np.float64)
    duration = frame_count / sample_rate if sample_rate else 0.0
    peak = float(np.max(np.abs(samples)) / 32768.0) if samples.size else 0.0
    rms = float(np.sqrt(np.mean(samples**2)) / 32768.0) if samples.size else 0.0
    rms_dbfs = 20 * math.log10(max(rms, 1e-12))
    clipping_fraction = (
        float(np.mean(np.abs(samples) >= 32760)) if samples.size else 0.0
    )
    active_fraction = (
        float(np.mean(np.abs(samples) >= 500)) if samples.size else 0.0
    )

    format_ok = (
        channels == CHANNELS
        and sample_width == SAMPLE_WIDTH
        and sample_rate == SAMPLE_RATE
        and any(
            abs(duration - expected_duration) < 0.01
            for expected_duration in EXPECTED_DURATION_SECONDS
        )
    )
    quality_flags = []
    if not format_ok:
        quality_flags.append("unexpected_format")
    if rms_dbfs < -45:
        quality_flags.append("very_quiet")
    if clipping_fraction > 0.01:
        quality_flags.append("clipping")
    if active_fraction < 0.02:
        quality_flags.append("little_active_audio")

    return {
        "sample_rate": sample_rate,
        "channels": channels,
        "sample_width_bytes": sample_width,
        "duration_seconds": round(duration, 4),
        "peak_normalized": round(peak, 6),
        "rms_dbfs": round(rms_dbfs, 2),
        "clipping_fraction": round(clipping_fraction, 8),
        "active_fraction": round(active_fraction, 6),
        "format_ok": format_ok,
        "quality_flags": quality_flags,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def collect_group(folder, label, category):
    records = []
    for path in sorted(folder.glob("*.wav")):
        records.append(
            {
                "source_path": str(path.resolve()),
                "label": label,
                "category": category,
                **inspect_wav(path),
            }
        )
    return records


def split_group(records, validation_count, randomizer):
    shuffled = list(records)
    randomizer.shuffle(shuffled)
    validation = shuffled[:validation_count]
    training = shuffled[validation_count:]
    return training, validation


def write_jsonl(path, records):
    with path.open("w", encoding="utf-8") as output_file:
        for record in records:
            output_file.write(json.dumps(record, sort_keys=True) + "\n")


def prepare_run(positive_dir, negative_dir, output_root):
    run_id = datetime.now().strftime("wake-candidate-%Y%m%d-%H%M%S")
    run_folder = output_root / run_id
    manifests_folder = run_folder / "manifests"
    manifests_folder.mkdir(parents=True, exist_ok=False)

    groups = {
        "positive": collect_group(positive_dir, 1, "positive"),
        "ordinary_speech": collect_group(
            negative_dir / "ordinary_speech", 0, "ordinary_speech"
        ),
        "speaker_playback": collect_group(
            negative_dir / "speaker_playback", 0, "speaker_playback"
        ),
    }
    expected_counts = {
        "positive": 20,
        "ordinary_speech": 20,
        "speaker_playback": 20,
    }
    actual_counts = {name: len(records) for name, records in groups.items()}
    if actual_counts != expected_counts:
        raise ValueError(
            f"Unexpected sample counts: {actual_counts}; expected {expected_counts}"
        )

    randomizer = random.Random(SPLIT_SEED)
    training = []
    validation = []
    for records in groups.values():
        group_training, group_validation = split_group(records, 4, randomizer)
        training.extend(group_training)
        validation.extend(group_validation)
    randomizer.shuffle(training)
    randomizer.shuffle(validation)

    all_records = training + validation
    flagged = [record for record in all_records if record["quality_flags"]]
    write_jsonl(manifests_folder / "train.jsonl", training)
    write_jsonl(manifests_folder / "validation.jsonl", validation)
    write_jsonl(manifests_folder / "quality_flags.jsonl", flagged)

    summary = {
        "run_id": run_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "split_seed": SPLIT_SEED,
        "source_counts": actual_counts,
        "train_count": len(training),
        "validation_count": len(validation),
        "quality_flag_count": len(flagged),
        "audio_played": False,
        "audio_transcribed": False,
    }
    (run_folder / "run_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"run_folder": str(run_folder), **summary}, indent=2))
    return run_folder


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--positive-dir", type=Path, required=True)
    parser.add_argument("--negative-dir", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    prepare_run(args.positive_dir, args.negative_dir, args.output_root)
