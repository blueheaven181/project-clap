"""Create derived wake clips and compare scores without training a model."""

import argparse
import json
import math
import wave
from collections import defaultdict
from pathlib import Path

import numpy as np
from openwakeword.model import Model

from prepare_wake_word_training_run import inspect_wav


SAMPLE_RATE = 16000
CLIP_SAMPLES = SAMPLE_RATE * 2
FRAME_SAMPLES = 320
HOP_SAMPLES = 160
MARGIN_SAMPLES = int(0.15 * SAMPLE_RATE)
TARGET_RMS_DBFS = -24.0
MAX_GAIN = 12.0
PEAK_CEILING = 0.95
DETECTION_THRESHOLD = 0.30


def write_wav(path, audio):
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(np.asarray(audio, dtype=np.int16).tobytes())


def load_wav(path):
    with wave.open(str(path), "rb") as wav_file:
        if (
            wav_file.getnchannels() != 1
            or wav_file.getsampwidth() != 2
            or wav_file.getframerate() != SAMPLE_RATE
        ):
            raise ValueError(f"Unsupported WAV format: {path}")
        return np.frombuffer(
            wav_file.readframes(wav_file.getnframes()), dtype="<i2"
        ).astype(np.float64) / 32768.0


def active_bounds(samples):
    """Find a relative-energy region with a small preserved margin."""

    if len(samples) < FRAME_SAMPLES:
        return 0, len(samples)
    frame_rms = []
    starts = range(0, len(samples) - FRAME_SAMPLES + 1, HOP_SAMPLES)
    starts = list(starts)
    for start in starts:
        frame = samples[start : start + FRAME_SAMPLES]
        frame_rms.append(float(np.sqrt(np.mean(frame**2))))
    frame_rms = np.asarray(frame_rms)
    maximum = float(frame_rms.max(initial=0.0))
    if maximum <= 1e-8:
        return 0, len(samples)
    active = np.flatnonzero(frame_rms >= max(maximum * 0.10, 1e-5))
    if not active.size:
        return 0, len(samples)
    start = max(0, starts[int(active[0])] - MARGIN_SAMPLES)
    end = min(
        len(samples),
        starts[int(active[-1])] + FRAME_SAMPLES + MARGIN_SAMPLES,
    )
    return start, end


def preprocess(samples):
    start, end = active_bounds(samples)
    trimmed = samples[start:end]
    rms = float(np.sqrt(np.mean(trimmed**2))) if trimmed.size else 0.0
    target_rms = 10 ** (TARGET_RMS_DBFS / 20)
    gain = min(MAX_GAIN, target_rms / max(rms, 1e-12))
    peak = float(np.max(np.abs(trimmed))) if trimmed.size else 0.0
    if peak > 0:
        gain = min(gain, PEAK_CEILING / peak)
    normalized = np.clip(trimmed * gain, -PEAK_CEILING, PEAK_CEILING)

    if len(normalized) > CLIP_SAMPLES:
        offset = (len(normalized) - CLIP_SAMPLES) // 2
        normalized = normalized[offset : offset + CLIP_SAMPLES]
    output = np.zeros(CLIP_SAMPLES, dtype=np.float64)
    offset = (CLIP_SAMPLES - len(normalized)) // 2
    output[offset : offset + len(normalized)] = normalized
    return np.rint(output * 32767).astype(np.int16), {
        "trim_start_seconds": round(start / SAMPLE_RATE, 4),
        "trim_end_seconds": round(end / SAMPLE_RATE, 4),
        "gain": round(gain, 4),
    }


def score_clip(model, path):
    samples = load_wav(path)
    integer_samples = np.rint(np.clip(samples, -1, 1) * 32767).astype(np.int16)
    model.reset()
    maximum = 0.0
    for start in range(0, len(integer_samples), 1280):
        frame = integer_samples[start : start + 1280]
        if len(frame) < 1280:
            frame = np.pad(frame, (0, 1280 - len(frame)))
        predictions = model.predict(frame)
        maximum = max(maximum, max(predictions.values(), default=0.0))
    return float(maximum)


def load_manifests(run_folder):
    records = []
    for name in ("train.jsonl", "validation.jsonl"):
        path = run_folder / "manifests" / name
        for line in path.read_text(encoding="utf-8").splitlines():
            record = json.loads(line)
            record["split"] = path.stem
            records.append(record)
    return records


def summarize(records):
    summary = {}
    grouped = defaultdict(list)
    for record in records:
        grouped[record["category"]].append(record)
    for category, group in sorted(grouped.items()):
        summary[category] = {
            "count": len(group),
            "original_detections": sum(
                item["original_score"] >= DETECTION_THRESHOLD for item in group
            ),
            "derived_detections": sum(
                item["derived_score"] >= DETECTION_THRESHOLD for item in group
            ),
            "original_score_max": round(
                max(item["original_score"] for item in group), 4
            ),
            "derived_score_max": round(
                max(item["derived_score"] for item in group), 4
            ),
            "derived_rms_dbfs_min": min(
                item["derived_metrics"]["rms_dbfs"] for item in group
            ),
            "derived_rms_dbfs_max": max(
                item["derived_metrics"]["rms_dbfs"] for item in group
            ),
        }
    return summary


def evaluate(run_folder, model_path, resource_model_dir):
    derived_root = run_folder / "derived" / "trimmed_normalized"
    metrics_folder = run_folder / "metrics"
    derived_root.mkdir(parents=True, exist_ok=True)
    metrics_folder.mkdir(parents=True, exist_ok=True)

    model = Model(
        wakeword_models=[str(model_path)],
        inference_framework="onnx",
        melspec_model_path=str(resource_model_dir / "melspectrogram.onnx"),
        embedding_model_path=str(resource_model_dir / "embedding_model.onnx"),
    )
    results = []
    for record in load_manifests(run_folder):
        source = Path(record["source_path"])
        output_folder = derived_root / record["category"]
        output_folder.mkdir(parents=True, exist_ok=True)
        derived = output_folder / source.name
        processed, preprocessing = preprocess(load_wav(source))
        write_wav(derived, processed)
        results.append(
            {
                "source_path": str(source),
                "derived_path": str(derived),
                "label": record["label"],
                "category": record["category"],
                "split": record["split"],
                "preprocessing": preprocessing,
                "original_score": round(score_clip(model, source), 6),
                "derived_score": round(score_clip(model, derived), 6),
                "derived_metrics": inspect_wav(derived),
            }
        )

    comparison_path = metrics_folder / "preprocessing_comparison.jsonl"
    with comparison_path.open("w", encoding="utf-8") as output_file:
        for result in results:
            output_file.write(json.dumps(result, sort_keys=True) + "\n")
    summary = {
        "model_path": str(model_path),
        "detection_threshold": DETECTION_THRESHOLD,
        "target_rms_dbfs": TARGET_RMS_DBFS,
        "max_gain": MAX_GAIN,
        "audio_played": False,
        "audio_transcribed": False,
        "categories": summarize(results),
    }
    (metrics_folder / "preprocessing_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-folder", type=Path, required=True)
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--resource-model-dir", type=Path, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    evaluate(args.run_folder, args.model_path, args.resource_model_dir)
