import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import call, patch


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_FOLDER / "src"))

import spotify
import command_router


class SpotifyTests(unittest.TestCase):
    def test_store_alias_is_preferred_for_current_user(self):
        with tempfile.TemporaryDirectory() as directory:
            local = Path(directory) / "local"
            launcher = local / "Microsoft" / "WindowsApps" / "Spotify.exe"
            launcher.parent.mkdir(parents=True)
            launcher.write_bytes(b"")
            with patch.dict(os.environ, {"LOCALAPPDATA": str(local), "APPDATA": ""}):
                self.assertEqual(launcher, spotify.get_spotify_launcher())

    @patch("spotify.os.startfile")
    @patch("spotify.get_spotify_launcher", return_value=Path("Spotify.exe"))
    def test_open_spotify_uses_detected_launcher(self, _launcher, startfile):
        self.assertTrue(spotify.open_spotify())
        startfile.assert_called_once_with("Spotify.exe")

    @patch("spotify.pyautogui.press")
    @patch("spotify.time.sleep")
    @patch("spotify.open_spotify", return_value=True)
    def test_play_uses_media_key_not_focused_space(self, _open, _sleep, press):
        self.assertTrue(spotify.play_spotify())
        press.assert_called_once_with("playpause")

    @patch("spotify.previous_track", return_value=True)
    @patch("spotify.next_track", return_value=True)
    @patch("spotify.resume_playback", return_value=True)
    @patch("spotify.pause_playback", return_value=True)
    @patch("spotify.pyautogui.press")
    def test_transport_controls_use_api(
        self, press, pause, resume, next_api, previous_api
    ):
        spotify.pause_spotify()
        spotify.resume_spotify()
        spotify.stop_spotify()
        spotify.next_spotify_track()
        spotify.previous_spotify_track()
        press.assert_not_called()
        self.assertEqual(2, pause.call_count)
        resume.assert_called_once_with()
        next_api.assert_called_once_with()
        previous_api.assert_called_once_with()

    @patch("spotify.pyautogui.press")
    @patch("spotify.pause_playback", side_effect=RuntimeError("offline"))
    def test_stop_retains_media_key_fallback(self, _pause, press):
        self.assertTrue(spotify.stop_spotify())
        press.assert_called_once_with("playpause")

    def test_parse_artist_search(self):
        self.assertEqual(
            {"query": "adele", "type": "artist"},
            spotify.parse_spotify_search_request("search Spotify for artist Adele"),
        )

    def test_parse_song_search(self):
        self.assertEqual(
            {"query": "yellow", "type": "track"},
            spotify.parse_spotify_search_request("find the song Yellow"),
        )

    def test_parse_album_search(self):
        self.assertEqual(
            {"query": "25", "type": "album"},
            spotify.parse_spotify_search_request("search for the album 25"),
        )

    def test_parse_generic_search(self):
        self.assertEqual(
            {"query": "coldplay", "type": None},
            spotify.parse_spotify_search_request("search Spotify for Coldplay"),
        )

    def test_non_search_command_is_not_parsed(self):
        self.assertIsNone(spotify.parse_spotify_search_request("pause Spotify"))

    def test_parse_natural_play_request_with_in_spotify(self):
        self.assertEqual(
            "smooth criminal",
            spotify.parse_spotify_play_request(
                "can you play Smooth Criminal in Spotify"
            ),
        )

    def test_transport_command_is_not_specific_play_request(self):
        self.assertIsNone(spotify.parse_spotify_play_request("resume Spotify"))

    @patch("command_router.stop_spotify")
    @patch("command_router.speak")
    def test_stop_music_routes_to_spotify_pause(self, speak, stop):
        self.assertTrue(command_router.route_command("stop music"))
        speak.assert_called_once_with("Stopping Spotify.")
        stop.assert_called_once_with()

    def test_search_uri_is_encoded_and_type_qualified(self):
        self.assertEqual(
            "spotify:search:track%3AYellow%20Submarine",
            spotify.build_spotify_search_uri("Yellow Submarine", "track"),
        )

    def test_normalizes_playlist_url_to_context_uri(self):
        self.assertEqual(
            "spotify:playlist:abc123",
            spotify.normalize_spotify_context_uri(
                "https://open.spotify.com/playlist/abc123?si=private"
            ),
        )

    @patch("spotify.start_context_playback", return_value=True)
    @patch("spotify.load_spotify_playlists", return_value={"relaxing": "spotify:playlist:abc123"})
    def test_mood_uses_exact_api_context(self, _playlists, start):
        self.assertTrue(spotify.play_spotify_mood("relaxing"))
        start.assert_called_once_with("spotify:playlist:abc123")

    @patch("spotify.time.sleep")
    @patch("spotify.os.startfile")
    @patch(
        "spotify.start_context_playback",
        side_effect=[RuntimeError("no active device"), True],
    )
    @patch("spotify.load_spotify_playlists", return_value={"relaxing": "spotify:playlist:abc123"})
    def test_mood_opens_spotify_and_retries_when_device_is_inactive(
        self, _playlists, start, startfile, sleep
    ):
        self.assertTrue(spotify.play_spotify_mood("relaxing"))
        startfile.assert_called_once_with("spotify:playlist:abc123")
        sleep.assert_called_once_with(5)
        self.assertEqual(2, start.call_count)

    @patch("spotify.time.sleep")
    @patch("spotify.os.startfile")
    @patch("spotify.start_context_playback", side_effect=RuntimeError("offline"))
    @patch("spotify.load_spotify_playlists", return_value={"relaxing": "spotify:playlist:abc123"})
    def test_mood_reports_failure_after_one_safe_retry(
        self, _playlists, start, _startfile, _sleep
    ):
        self.assertFalse(spotify.play_spotify_mood("relaxing"))
        self.assertEqual(2, start.call_count)

    @patch("spotify.os.startfile")
    @patch("spotify.get_spotify_launcher", return_value=Path("Spotify.exe"))
    def test_search_opens_results_without_clicking(self, _launcher, startfile):
        self.assertTrue(spotify.search_spotify("Adele", "artist"))
        startfile.assert_called_once_with("spotify:search:artist%3AAdele")

    @patch("command_router.speak")
    @patch("command_router.search_spotify", return_value=True)
    def test_artist_voice_command_routes_to_search(self, search, speak):
        self.assertTrue(command_router.route_command("search for artist Adele"))
        search.assert_called_once_with("adele", "artist")
        speak.assert_called_once_with("Showing artist search results for adele.")

    @patch("command_router.speak")
    @patch("command_router.search_spotify", return_value=True)
    def test_album_voice_command_routes_to_search(self, search, _speak):
        self.assertTrue(command_router.route_command("find the album 25"))
        search.assert_called_once_with("25", "album")

    @patch("command_router.speak")
    @patch("command_router.search_spotify", return_value=True)
    def test_song_voice_command_routes_to_search(self, search, _speak):
        self.assertTrue(command_router.route_command("find the song Yellow"))
        search.assert_called_once_with("yellow", "track")

    @patch("command_router.speak")
    @patch(
        "command_router.play_spotify_track",
        return_value={"name": "Smooth Criminal", "artists": "Michael Jackson"},
    )
    def test_natural_play_command_routes_to_exact_track(self, play, speak):
        self.assertTrue(
            command_router.route_command(
                "can you play Smooth Criminal in Spotify"
            )
        )
        play.assert_called_once_with("smooth criminal")
        speak.assert_called_once_with(
            "Playing Smooth Criminal by Michael Jackson on Spotify."
        )


if __name__ == "__main__":
    unittest.main()
