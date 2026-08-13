"""Private, local-only Spotify OAuth authorization using PKCE."""

import base64
import hashlib
import json
import secrets
import threading
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen


PROJECT_FOLDER = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_FOLDER / "config" / "spotify_api.local.json"
TOKEN_PATH = PROJECT_FOLDER / "config" / "spotify_token.local.json"
AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE_URL = "https://api.spotify.com/v1"
SCOPES = "user-modify-playback-state user-read-playback-state"


def load_spotify_api_config(path=CONFIG_PATH):
    with Path(path).open("r", encoding="utf-8") as config_file:
        config = json.load(config_file)
    client_id = str(config.get("client_id", "")).strip()
    redirect_uri = str(config.get("redirect_uri", "")).strip()
    if not client_id or not redirect_uri:
        raise ValueError("Spotify client_id and redirect_uri are required.")
    parsed = urlparse(redirect_uri)
    if parsed.scheme != "http" or parsed.hostname != "127.0.0.1":
        raise ValueError("Spotify redirect_uri must use local 127.0.0.1 HTTP.")
    return {"client_id": client_id, "redirect_uri": redirect_uri}


def build_pkce_pair():
    verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    return verifier, challenge


def build_authorization_url(config, challenge, state):
    return AUTHORIZE_URL + "?" + urlencode({
        "client_id": config["client_id"],
        "response_type": "code",
        "redirect_uri": config["redirect_uri"],
        "scope": SCOPES,
        "code_challenge_method": "S256",
        "code_challenge": challenge,
        "state": state,
    })


def exchange_code(config, code, verifier):
    payload = urlencode({
        "client_id": config["client_id"],
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": config["redirect_uri"],
        "code_verifier": verifier,
    }).encode("ascii")
    request = Request(
        TOKEN_URL,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urlopen(request, timeout=20) as response:
        token = json.load(response)
    token["expires_at"] = int(time.time()) + int(token.get("expires_in", 3600))
    return token


def load_token(path=TOKEN_PATH):
    with Path(path).open("r", encoding="utf-8") as token_file:
        return json.load(token_file)


def save_token(token, path=TOKEN_PATH):
    Path(path).write_text(json.dumps(token, indent=2), encoding="utf-8")


def refresh_access_token(config, refresh_token):
    payload = urlencode({
        "client_id": config["client_id"],
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }).encode("ascii")
    request = Request(
        TOKEN_URL,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urlopen(request, timeout=20) as response:
        refreshed = json.load(response)
    refreshed.setdefault("refresh_token", refresh_token)
    refreshed["expires_at"] = int(time.time()) + int(refreshed.get("expires_in", 3600))
    save_token(refreshed)
    return refreshed


def get_access_token():
    config = load_spotify_api_config()
    token = load_token()
    if int(token.get("expires_at", 0)) <= int(time.time()) + 30:
        token = refresh_access_token(config, token["refresh_token"])
    return token["access_token"]


def spotify_api_request(method, path, body=None, expect_json=True):
    data = None if body is None else json.dumps(body).encode("utf-8")
    request = Request(
        API_BASE_URL + path,
        data=data,
        headers={
            "Authorization": f"Bearer {get_access_token()}",
            "Content-Type": "application/json",
        },
        method=method,
    )
    with urlopen(request, timeout=20) as response:
        raw_body = response.read()
        if not expect_json or not raw_body:
            return None
        return json.loads(raw_body.decode("utf-8-sig"))


def start_context_playback(context_uri):
    spotify_api_request(
        "PUT", "/me/player/play", {"context_uri": context_uri}, expect_json=False
    )
    return True


def pause_playback():
    spotify_api_request("PUT", "/me/player/pause", expect_json=False)
    return True


def resume_playback():
    spotify_api_request("PUT", "/me/player/play", expect_json=False)
    return True


def next_track():
    spotify_api_request("POST", "/me/player/next", expect_json=False)
    return True


def previous_track():
    spotify_api_request("POST", "/me/player/previous", expect_json=False)
    return True


def search_and_play_track(query):
    search_path = "/search?" + urlencode({
        "q": query,
        "type": "track",
        "limit": 1,
    })
    result = spotify_api_request("GET", search_path)
    items = result.get("tracks", {}).get("items", [])
    if not items:
        return None
    track = items[0]
    spotify_api_request(
        "PUT", "/me/player/play", {"uris": [track["uri"]]}, expect_json=False
    )
    artists = ", ".join(artist["name"] for artist in track.get("artists", []))
    return {"name": track["name"], "artists": artists}


def authorize():
    config = load_spotify_api_config()
    redirect = urlparse(config["redirect_uri"])
    if not redirect.port:
        raise ValueError("Spotify redirect_uri must include a local port.")
    verifier, challenge = build_pkce_pair()
    expected_state = secrets.token_urlsafe(24)
    result = {}

    class CallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            values = parse_qs(urlparse(self.path).query)
            result.update({key: value[0] for key, value in values.items()})
            message = b"Spotify authorization received. You may close this tab."
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(message)))
            self.end_headers()
            self.wfile.write(message)

        def log_message(self, _format, *_args):
            return

    server = HTTPServer((redirect.hostname, redirect.port), CallbackHandler)
    thread = threading.Thread(target=server.handle_request, daemon=True)
    thread.start()
    webbrowser.open(build_authorization_url(config, challenge, expected_state))
    print("Complete Spotify authorization in the browser...")
    thread.join(timeout=180)
    server.server_close()
    if thread.is_alive():
        raise TimeoutError("Spotify authorization timed out.")
    if result.get("state") != expected_state:
        raise ValueError("Spotify authorization state did not match.")
    if "error" in result:
        raise PermissionError(f"Spotify authorization failed: {result['error']}")
    token = exchange_code(config, result["code"], verifier)
    save_token(token)
    print("Spotify authorization completed and stored locally.")


if __name__ == "__main__":
    authorize()
