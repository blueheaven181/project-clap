import time
from pathlib import Path

import numpy as np
import sounddevice as sd
from openwakeword.model import Model


SAMPLE_RATE = 16000
CHUNK_SIZE = 1280
MICROPHONE_INDEX = 1
DETECTION_THRESHOLD = 0.5
DETECTION_COOLDOWN = 2.0


def get_model_path():
    project_folder = Path(__file__).resolve().parent.parent

    return (
        project_folder
        / "models"
        / "wake_words"
        / "hey_Clap.onnx"
    )


def listen_for_wake_word():
    model_path = get_model_path()

    if not model_path.exists():
        print("Wake-word model was not found.")
        return

    wake_word_model = Model(
        wakeword_models=[str(model_path)],
        inference_framework="onnx",
    )

    last_detection_time = 0.0

    print("Listening for the test wake word...")
    print('Say "Hey CLAP". Press Ctrl + C to stop.')

    with sd.InputStream(
        device=MICROPHONE_INDEX,
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16",
        blocksize=CHUNK_SIZE,
    ) as microphone:
        while True:
            audio, overflowed = microphone.read(CHUNK_SIZE)

            if overflowed:
                print("Microphone overflow detected.")

            audio_frame = np.asarray(
                audio.flatten(),
                dtype=np.int16,
            )

            predictions = wake_word_model.predict(audio_frame)

            for model_name, score in predictions.items():
                current_time = time.monotonic()

                if (
                    score >= DETECTION_THRESHOLD
                    and current_time - last_detection_time
                    >= DETECTION_COOLDOWN
                ):
                    print(
                        "WAKE WORD DETECTED:",
                        model_name,
                        f"score={score:.2f}",
                    )

                    last_detection_time = current_time


if __name__ == "__main__":
    try:
        listen_for_wake_word()
    except KeyboardInterrupt:
        print("\nWake-word test stopped.")
    except Exception as error:
        print("Wake-word test error:", error)