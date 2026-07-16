import sounddevice as sd
import numpy as np
import time

from greeting import speak, get_greeting

speak(f"{get_greeting()}. Project CLAP activated.")


CLAP_THRESHOLD = 0.30
DOUBLE_CLAP_WINDOW = 1.0

clap_times = []
double_clap_detected = False


def detect_clap(indata, frames, time_info, status):

    global double_clap_detected

    volume = np.linalg.norm(indata) * 10

    if volume > CLAP_THRESHOLD:

        current_time = time.time()
        clap_times.append(current_time)

        if len(clap_times) >= 2:

            if clap_times[-1] - clap_times[-2] <= DOUBLE_CLAP_WINDOW:

                print("DOUBLE CLAP DETECTED")

                double_clap_detected = True


print("Listening for claps...")

with sd.InputStream(callback=detect_clap):

    while True:

        if double_clap_detected:

            speak("Good evening Marc. Project CLAP activated.")

            break

        time.sleep(0.1)