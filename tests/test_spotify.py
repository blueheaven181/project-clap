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

    @patch("spotify.pyautogui.press")
    def test_existing_transport_controls_are_preserved(self, press):
        spotify.pause_spotify()
        spotify.resume_spotify()
        spotify.stop_spotify()
        spotify.next_spotify_track()
        spotify.previous_spotify_track()
        self.assertEqual(
            ["playpause", "playpause", "stop", "nexttrack", "prevtrack"],
            [call.args[0] for call in press.call_args_list],
        )

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

    @patch("spotify.os.startfile")
    @patch("spotify.start_context_playback", side_effect=RuntimeError("offline"))
    @patch("spotify.load_spotify_playlists", return_value={"relaxing": "spotify:playlist:abc123"})
    def test_mood_retains_desktop_fallback(self, _playlists, _start, startfile):
        self.assertTrue(spotify.play_spotify_mood("relaxing"))
        startfile.assert_called_once_with("spotify:playlist:abc123")

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


if __name__ == "__main__":
    unittest.main()
