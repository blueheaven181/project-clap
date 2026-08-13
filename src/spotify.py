import json
import os
import re
import time
from pathlib import Path
from urllib.parse import quote

import pyautogui

from spotify_auth import (
    next_track,
    pause_playback,
    previous_track,
    resume_playback,
    search_and_play_track,
    start_context_playback,
)


SPOTIFY_SEARCH_TYPES = {
    "artist": "artist",
    "artists": "artist",
    "song": "track",
    "songs": "track",
    "track": "track",
    "tracks": "track",
    "album": "album",
    "albums": "album",
    "playlist": "playlist",
    "playlists": "playlist",
}


def get_spotify_launcher():
    """Return this Windows user's Spotify launcher, if installed."""

    candidates = (
        Path(os.environ.get("LOCALAPPDATA", ""))
        / "Microsoft"
        / "WindowsApps"
        / "Spotify.exe",
        Path(os.environ.get("APPDATA", "")) / "Spotify" / "Spotify.exe",
    )

    return next((path for path in candidates if path.is_file()), None)


def open_spotify():
    launcher = get_spotify_launcher()
    if launcher is None:
        print("Spotify is not installed for the current Windows user.")
        return False

    os.startfile(str(launcher))
    return True


def parse_spotify_search_request(command):
    """Return a safe Spotify search query and optional content type."""

    normalized = " ".join(command.strip().lower().split())
    patterns = (
        r"^(?:search|find|look up) (?:spotify )?(?:for )?(?P<body>.+)$",
        r"^(?:play|open) (?:the )?(?P<body>.+?) on spotify$",
    )
    body = None
    for pattern in patterns:
        match = re.match(pattern, normalized)
        if match:
            body = match.group("body").strip()
            break

    if not body:
        return None

    search_type = None
    type_match = re.match(
        r"^(?:the )?(artist|artists|song|songs|track|tracks|album|albums|playlist|playlists)\s+(?:called |named )?(?P<query>.+)$",
        body,
    )
    if type_match:
        search_type = SPOTIFY_SEARCH_TYPES[type_match.group(1)]
        body = type_match.group("query").strip()

    body = re.sub(r"\s+on spotify$", "", body).strip(" .?!")
    if not body or len(body) > 200:
        return None

    return {"query": body, "type": search_type}


def parse_spotify_play_request(command):
    """Parse a natural request to play one specific Spotify track."""

    normalized = " ".join(command.strip().lower().split())
    match = re.match(
        r"^(?:(?:can|could|would) you )?play (?:the (?:song|track) )?"
        r"(?P<query>.+?) (?:on|in) spotify$",
        normalized,
    )
    if not match:
        return None
    query = match.group("query").strip(" .?!")
    if not query or len(query) > 200:
        return None
    return query


def play_spotify_track(query):
    """Play Spotify's top track result and return its display metadata."""

    return search_and_play_track(query)


def build_spotify_search_uri(query, search_type=None):
    search_text = query.strip()
    if search_type:
        if search_type not in {"artist", "track", "album", "playlist"}:
            raise ValueError("Unsupported Spotify search type")
        search_text = f"{search_type}:{search_text}"
    return "spotify:search:" + quote(search_text, safe="")


def search_spotify(query, search_type=None):
    """Open Spotify's results page without selecting or playing a result."""

    if get_spotify_launcher() is None:
        print("Spotify is not installed for the current Windows user.")
        return False

    os.startfile(build_spotify_search_uri(query, search_type))
    return True


def play_spotify():

    if not open_spotify():
        return False

    # Give Spotify time to launch
    time.sleep(8)

    print("Sending play command...")

    # Media play/pause key
    pyautogui.press("playpause")
    return True


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

    context_uri = normalize_spotify_context_uri(playlist_uri)
    try:
        start_context_playback(context_uri)
        return True
    except Exception as error:
        print(f"Spotify API playback unavailable; using desktop fallback: {error}")
        os.startfile(playlist_uri)
        return True


def normalize_spotify_context_uri(value):
    """Return an album, artist, or playlist Spotify context URI."""

    cleaned = str(value).strip()
    if re.fullmatch(r"spotify:(?:album|artist|playlist):[A-Za-z0-9]+", cleaned):
        return cleaned
    match = re.match(
        r"https?://open\.spotify\.com/(album|artist|playlist)/([A-Za-z0-9]+)",
        cleaned,
    )
    if match:
        return f"spotify:{match.group(1)}:{match.group(2)}"
    raise ValueError("Unsupported Spotify playback context.")



def pause_spotify():
    """
    Pause the current Spotify playback.
    """

    print("Pausing Spotify...")
    try:
        pause_playback()
        return True
    except Exception as error:
        print(f"Spotify API pause unavailable; using media-key fallback: {error}")
        pyautogui.press("playpause")
        return True


def resume_spotify():
    """
    Resume paused Spotify playback.
    """

    print("Resuming Spotify...")
    try:
        resume_playback()
        return True
    except Exception as error:
        print(f"Spotify API resume unavailable; using media-key fallback: {error}")
        pyautogui.press("playpause")
        return True


def stop_spotify():
    """
    Stop the current Spotify playback.
    """

    print("Stopping Spotify...")
    try:
        pause_playback()
        return True
    except Exception as error:
        print(f"Spotify API pause unavailable; using media-key fallback: {error}")
        pyautogui.press("playpause")
        return True


def next_spotify_track():
    """
    Skip to the next Spotify track.
    """

    print("Skipping to the next track...")
    try:
        next_track()
        return True
    except Exception as error:
        print(f"Spotify API next unavailable; using media-key fallback: {error}")
        pyautogui.press("nexttrack")
        return True


def previous_spotify_track():
    """
    Return to the previous Spotify track.
    """

    print("Returning to the previous track...")
    try:
        previous_track()
        return True
    except Exception as error:
        print(f"Spotify API previous unavailable; using media-key fallback: {error}")
        pyautogui.press("prevtrack")
        return True


if __name__ == "__main__":
    play_spotify()
