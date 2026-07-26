import os
import time
import pyautogui


def open_spotify():

    spotify_path = r"C:\Users\marcm\AppData\Roaming\Spotify\Spotify.exe"

    os.startfile(spotify_path)


def play_spotify():

    open_spotify()

    # Give Spotify time to launch
    time.sleep(8)

    print("Sending play command...")

    # Media play/pause key
    pyautogui.press("space")

if __name__ == "__main__":
    play_spotify()