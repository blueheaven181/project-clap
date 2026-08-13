"""Score local wake-word WAVs without playback, transcription, or training."""

import argparse
import json
from pathlib import Path

from openwakeword.model import Model

from evaluate_wake_word_preprocessing import score_clip


THRESHOLD = 0.30


def score_folder(sample_dir, model_path, resource_model_dir):
    model = Model(
        wakeword_models=[str(model_path)],
        inference_framework="onnx",
        melspec_model_path=str(resource_model_dir / "melspectrogram.onnx"),
        embedding_model_path=str(resource_model_dir / "embedding_model.onnx"),
    )
    records = []
    for path in sorted(sample_dir.glob("*.wav")):
        records.append(
            {
                "file": path.name,
                "score": round(score_clip(model, path), 6),
            }
        )

    scores = [record["score"] for record in records]
    summary = {
        "sample_count": len(records),
        "threshold": THRESHOLD,
        "detection_count": sum(score >= THRESHOLD for score in scores),
        "near_miss_count": sum(0.10 <= score < THRESHOLD for score in scores),
        "minimum_score": min(scores, default=0.0),
        "maximum_score": max(scores, default=0.0),
        "audio_played": False,
        "audio_transcribed": False,
        "model_path": str(model_path),
        "scores": records,
    }
    output_path = sample_dir / "current_model_scores.json"
    output_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({key: value for key, value in summary.items() if key != "scores"}, indent=2))
    print("output_path=", output_path)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-dir", type=Path, required=True)
    parser.add_argument("--model-path", type=Path, required=True)
    parser.add_argument("--resource-model-dir", type=Path, required=True)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    score_folder(args.sample_dir, args.model_path, args.resource_model_dir)
