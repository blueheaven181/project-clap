import time
from pathlib import Path

import numpy as np
import sounddevice as sd
from openwakeword.model import Model


SAMPLE_RATE = 16000
CHUNK_SIZE = 1280
MICROPHONE_INDEX = 1

WAKE_WORD_THRESHOLD = 0.5
ACTIVATION_COOLDOWN = 2.0

CLAP_THRESHOLD = 20
DOUBLE_CLAP_WINDOW = 1.0
CLAP_COOLDOWN = 0.3


clap_times = []
last_clap_time = 0.0
last_activation_time = 0.0


def get_model_path():
    project_folder = Path(__file__).resolve().parent.parent

    return (
        project_folder
        / "models"
        / "wake_words"
        / "hey_Clap.onnx"
    )


model_path = get_model_path()

if not model_path.exists():
    raise FileNotFoundError(
        f"Wake-word model was not found: {model_path}"
    )


wake_word_model = Model(
    wakeword_models=[str(model_path)],
    inference_framework="onnx",
)


def detect_activation(indata, frames, time_info, status):
    global last_clap_time
    global last_activation_time

    if status:
        print("Audio status:", status)

    current_time = time.monotonic()

    if current_time - last_activation_time < ACTIVATION_COOLDOWN:
        return

    # Check for the Hey CLAP wake word.
    audio_frame = np.clip(
        indata.flatten(),
        -1.0,
        1.0,
    )

    audio_frame = (
        audio_frame * 32767
    ).astype(np.int16)

    predictions = wake_word_model.predict(audio_frame)

    for model_name, score in predictions.items():
        if score >= WAKE_WORD_THRESHOLD:
            print(
                "HEY CLAP DETECTED:",
                model_name,
                f"score={score:.2f}",
            )

            clap_times.clear()
            last_activation_time = current_time
            return

    # Check for a double clap.
    volume = np.linalg.norm(indata) * 10



    if volume <= CLAP_THRESHOLD:
        return

    if current_time - last_clap_time < CLAP_COOLDOWN:
        return

    last_clap_time = current_time
    clap_times.append(current_time)

    clap_times[:] = [
        clap_time
        for clap_time in clap_times
        if current_time - clap_time <= DOUBLE_CLAP_WINDOW
    ]

    if (
        len(clap_times) >= 2
        and clap_times[-1] - clap_times[-2]
        <= DOUBLE_CLAP_WINDOW
    ):
        print("DOUBLE CLAP DETECTED")

        clap_times.clear()
        last_activation_time = current_time


def run_activation_test():
    print("Listening for double clap or Hey CLAP...")
    print("Press Ctrl + C to stop.")

    with sd.InputStream(
        callback=detect_activation,
        device=MICROPHONE_INDEX,
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
        blocksize=CHUNK_SIZE,
    ):
        while True:
            time.sleep(0.1)


if __name__ == "__main__":
    try:
        run_activation_test()
    except KeyboardInterrupt:
        print("\nActivation test stopped.")
    except Exception as error:
        print("Activation test error:", error)