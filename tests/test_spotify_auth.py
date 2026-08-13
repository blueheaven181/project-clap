import json
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from unittest.mock import patch


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_FOLDER / "src"))

import spotify_auth


class SpotifyAuthTests(unittest.TestCase):
    def test_loads_private_config_without_client_secret(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "spotify.json"
            path.write_text(json.dumps({
                "client_id": "local-client-id",
                "redirect_uri": "http://127.0.0.1:8888/callback",
            }), encoding="utf-8")
            self.assertEqual("local-client-id", spotify_auth.load_spotify_api_config(path)["client_id"])

    def test_rejects_non_loopback_redirect(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "spotify.json"
            path.write_text(json.dumps({
                "client_id": "local-client-id",
                "redirect_uri": "https://example.com/callback",
            }), encoding="utf-8")
            with self.assertRaises(ValueError):
                spotify_auth.load_spotify_api_config(path)

    def test_authorization_url_uses_pkce_and_required_scopes(self):
        url = spotify_auth.build_authorization_url(
            {"client_id": "client", "redirect_uri": "http://127.0.0.1:8888/callback"},
            "challenge",
            "state",
        )
        query = parse_qs(urlparse(url).query)
        self.assertEqual(["S256"], query["code_challenge_method"])
        self.assertIn("user-modify-playback-state", query["scope"][0])
        self.assertNotIn("client_secret", query)

    @patch("spotify_auth.spotify_api_request")
    def test_start_context_playback_uses_official_player_endpoint(self, request):
        self.assertTrue(spotify_auth.start_context_playback("spotify:playlist:abc123"))
        request.assert_called_once_with(
            "PUT",
            "/me/player/play",
            {"context_uri": "spotify:playlist:abc123"},
        )


if __name__ == "__main__":
    unittest.main()
