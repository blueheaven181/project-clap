import sounddevice as sd
import numpy as np
import time

from greeting import speak, get_greeting




CLAP_THRESHOLD = 5
DOUBLE_CLAP_WINDOW = 1.0
CLAP_COOLDOWN = 0.3

clap_times = []
double_clap_detected = False
last_clap_time = 0



def detect_clap(indata, frames, time_info, status):

    global double_clap_detected
    global last_clap_time

    volume = np.linalg.norm(indata) * 10



    current_time = time.time()

    if volume > CLAP_THRESHOLD:

        if current_time - last_clap_time < CLAP_COOLDOWN:
            return

        last_clap_time = current_time

        clap_times.append(current_time)

        clap_times[:] = [
            t for t in clap_times
            if current_time - t <= DOUBLE_CLAP_WINDOW
        ]


        

        if len(clap_times) >= 2:

            if clap_times[-1] - clap_times[-2] <= DOUBLE_CLAP_WINDOW:

                print("DOUBLE CLAP DETECTED")

                double_clap_detected = True

    


print("Listening for claps...")

with sd.InputStream(callback=detect_clap):

    while True:

        if double_clap_detected:
         

         print(get_greeting())
         speak(f"{get_greeting()}. Project CLAP activated.")

         break

        time.sleep(0.1)