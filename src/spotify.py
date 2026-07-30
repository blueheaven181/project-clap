import json
import os
import time
from pathlib import Path

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


def load_spotify_playlists():
    """
    Load Marc's private Spotify mood-playlist configuration.
    """

    project_folder = Path(__file__).resolve().parent.parent
    playlist_path = (
        project_folder
        / "config"
        / "spotify_playlists.local.json"
    )

    try:
        with playlist_path.open(
            "r",
            encoding="utf-8",
        ) as playlist_file:
            return json.load(playlist_file)

    except FileNotFoundError:
        print("Spotify playlist configuration was not found.")
        return {}

    except json.JSONDecodeError as error:
        print("Spotify playlist configuration is invalid:", error)
        return {}


def play_spotify_mood(mood):
    """
    Open and play the configured Spotify playlist for a mood.
    """

    normalized_mood = mood.strip().lower()
    playlists = load_spotify_playlists()
    playlist_uri = playlists.get(normalized_mood)

    if not playlist_uri:
        print(
            f"No Spotify playlist is configured for {normalized_mood}."
        )
        return False

    print(f"Playing {normalized_mood} Spotify music...")

    # Stop existing media before selecting the new playlist.
    pyautogui.press("stop")

    os.startfile(playlist_uri)

    # Give Spotify time to open the selected playlist.
    time.sleep(5)

    pyautogui.press("space")
    return True



def pause_spotify():
    """
    Pause the current Spotify playback.
    """

    print("Pausing Spotify...")
    pyautogui.press("playpause")


def resume_spotify():
    """
    Resume paused Spotify playback.
    """

    print("Resuming Spotify...")
    pyautogui.press("playpause")


def stop_spotify():
    """
    Stop the current Spotify playback.
    """

    print("Stopping Spotify...")
    pyautogui.press("stop")


def next_spotify_track():
    """
    Skip to the next Spotify track.
    """

    print("Skipping to the next track...")
    pyautogui.press("nexttrack")


def previous_spotify_track():
    """
    Return to the previous Spotify track.
    """

    print("Returning to the previous track...")
    pyautogui.press("prevtrack")


if __name__ == "__main__":
    play_spotify()