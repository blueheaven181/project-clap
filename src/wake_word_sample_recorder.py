"""Record local, labeled wake-word samples without loading Project CLAP."""

import argparse
import json
import time
import wave
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import sounddevice as sd


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
OUTPUT_ROOT = PROJECT_FOLDER / "recordings" / "wake_word_training"
SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = "int16"
DEFAULT_DEVICE = 1
DEFAULT_COUNT = 20
DEFAULT_DURATION = 3.0
PRE_ROLL_SECONDS = 0.5
LABEL = "hey_clap_positive"


def write_wav(path, audio):
    """Write one mono 16-bit WAV recording."""

    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(CHANNELS)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(np.asarray(audio, dtype=np.int16).tobytes())


def measure_signal(audio):
    """Return technical level/activity metrics without interpreting speech."""

    samples = np.asarray(audio, dtype=np.int16).reshape(-1).astype(np.float64)
    normalized = samples / 32768.0
    peak = float(np.max(np.abs(normalized))) if samples.size else 0.0
    rms = float(np.sqrt(np.mean(normalized**2))) if samples.size else 0.0
    rms_dbfs = float(20 * np.log10(max(rms, 1e-12)))
    active_fraction = (
        float(np.mean(np.abs(samples) >= 250)) if samples.size else 0.0
    )
    clipping_fraction = (
        float(np.mean(np.abs(samples) >= 32760)) if samples.size else 0.0
    )
    retry_recommended = peak < 0.015 or active_fraction < 0.03
    return {
        "peak_normalized": round(peak, 6),
        "rms_dbfs": round(rms_dbfs, 2),
        "active_fraction": round(active_fraction, 6),
        "clipping_fraction": round(clipping_fraction, 8),
        "retry_recommended": retry_recommended,
    }


def record_samples(count, duration, device):
    """Interactively capture explicitly confirmed positive wake samples."""

    device_info = sd.query_devices(device, "input")
    session_name = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_folder = OUTPUT_ROOT / "positive" / session_name
    metadata_path = session_folder / "metadata.jsonl"

    print("Wake-word clean positive-sample recorder")
    print(f"Microphone: {device_info['name']} (index {device})")
    print(f"Samples: {count}; duration: {duration:.1f} seconds each")
    print(f"Local output: {session_folder}")
    print('For each sample, say "Hey CLAP" once at normal distance.')
    print(
        f"The microphone starts {PRE_ROLL_SECONDS:.1f} seconds before "
        "the SPEAK NOW prompt."
    )
    print("No recording starts until you press Enter for that sample.")
    print("Every recording must be explicitly accepted or retried.")
    print("Type Q and press Enter at any prompt to stop without deleting saved files.")

    confirmation = input("Type START CLEAN POSITIVE CAPTURE to begin: ").strip()
    if confirmation != "START CLEAN POSITIVE CAPTURE":
        print("Capture cancelled. No audio was recorded.")
        return None

    session_folder.mkdir(parents=True, exist_ok=False)

    stopped = False
    for index in range(1, count + 1):
        attempts = 0
        while True:
            response = input(
                f"Sample {index}/{count}: press Enter to arm (Q stops): "
            ).strip()
            if response.lower() == "q":
                print("Capture stopped. Existing samples were kept locally.")
                stopped = True
                break

            attempts += 1
            audio = sd.rec(
                int(duration * SAMPLE_RATE),
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                dtype=DTYPE,
                device=device,
            )
            print("Microphone is live. Get ready...")
            time.sleep(PRE_ROLL_SECONDS)
            print('SPEAK NOW: say "Hey CLAP" once naturally.')
            sd.wait()

            signal = measure_signal(audio)
            print(
                "Technical check: "
                f"peak={signal['peak_normalized']:.3f}, "
                f"RMS={signal['rms_dbfs']:.1f} dBFS, "
                f"active={signal['active_fraction'] * 100:.1f}%, "
                f"clipping={signal['clipping_fraction'] * 100:.3f}%"
            )
            if signal["retry_recommended"]:
                print(
                    "RETRY RECOMMENDED: the phrase activity is weak. "
                    "Stay at normal distance and begin only after SPEAK NOW."
                )
            else:
                print("Technical level looks usable.")

            decision = ""
            while decision not in {"a", "r", "q"}:
                decision = input(
                    "Type A to accept, R to retry, or Q to stop: "
                ).strip().lower()
            if decision == "r":
                print("Retrying this sample; nothing was saved.")
                continue
            if decision == "q":
                print("Capture stopped. Existing samples were kept locally.")
                stopped = True
                break
            break

        if stopped:
            break

        filename = f"hey_clap_positive_{index:03d}.wav"
        sample_path = session_folder / filename
        write_wav(sample_path, audio)

        metadata = {
            "file": filename,
            "label": LABEL,
            "sample_rate": SAMPLE_RATE,
            "channels": CHANNELS,
            "duration_seconds": duration,
            "device_index": device,
            "device_name": device_info["name"],
            "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
            "capture_context": "normal_distance_quiet_room_clean_capture",
            "pre_roll_seconds": PRE_ROLL_SECONDS,
            "attempts_for_accepted_sample": attempts,
            "signal_metrics": signal,
        }
        with metadata_path.open("a", encoding="utf-8") as metadata_file:
            metadata_file.write(json.dumps(metadata) + "\n")

        print(f"Saved {filename}")
        time.sleep(0.3)

    saved_count = len(list(session_folder.glob("*.wav")))
    print(f"Capture complete: {saved_count} sample(s) saved locally.")
    print(f"Session folder: {session_folder}")
    return session_folder


def parse_args():
    parser = argparse.ArgumentParser(
        description="Record isolated local Hey CLAP positive training samples."
    )
    parser.add_argument("--count", type=int, default=DEFAULT_COUNT)
    parser.add_argument("--duration", type=float, default=DEFAULT_DURATION)
    parser.add_argument("--device", type=int, default=DEFAULT_DEVICE)
    args = parser.parse_args()

    if not 1 <= args.count <= 100:
        parser.error("--count must be between 1 and 100")
    if not 0.5 <= args.duration <= 5.0:
        parser.error("--duration must be between 0.5 and 5.0 seconds")
    return args


if __name__ == "__main__":
    arguments = parse_args()
    try:
        record_samples(arguments.count, arguments.duration, arguments.device)
    except KeyboardInterrupt:
        print("\nCapture stopped. Existing samples were kept locally.")
    except Exception as error:
        print("Recorder error:", error)
