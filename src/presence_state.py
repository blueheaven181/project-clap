"""Fail-safe state bridge for CLAP's optional visual presence window."""

import socket
import json
import subprocess
import sys
import threading
from pathlib import Path
from runtime_paths import DATA_ROOT, IS_FROZEN, data_path


HOST = "127.0.0.1"
PORT = 47621
VALID_STATES = {"standby", "listening", "thinking", "speaking"}
CONFIG_PATH = data_path("config", "presence.local.json")

_state = "standby"
_lock = threading.Lock()


def get_presence_state():
    with _lock:
        return _state


def set_presence_state(state):
    """Remember and best-effort publish one non-sensitive visual state."""

    if state not in VALID_STATES:
        raise ValueError(f"Unsupported CLAP presence state: {state}")

    global _state
    with _lock:
        _state = state

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as channel:
            channel.sendto(state.encode("ascii"), (HOST, PORT))
    except OSError:
        pass


def stop_presence_window():
    """Best-effort request for the optional visualizer to close."""

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as channel:
            channel.sendto(b"shutdown", (HOST, PORT))
    except OSError:
        pass


def start_presence_window():
    """Launch the optional visualizer; never make CLAP depend on it."""

    preview_name = "clap_presence_preview.py"
    try:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        if config.get("mode") == "floating":
            preview_name = "clap_floating_orb_preview.py"
    except (OSError, json.JSONDecodeError):
        pass
    if IS_FROZEN:
        command = [sys.executable, "--orb", "--live"]
        working_folder = DATA_ROOT
    else:
        preview = Path(__file__).with_name(preview_name)
        executable = Path(sys.executable)
        pythonw = executable.with_name("pythonw.exe")
        if pythonw.exists():
            executable = pythonw
        command = [str(executable), str(preview), "--live"]
        working_folder = preview.parent.parent

    creationflags = 0
    if sys.platform == "win32":
        creationflags = (
            subprocess.CREATE_NEW_PROCESS_GROUP
            | subprocess.DETACHED_PROCESS
        )

    try:
        subprocess.Popen(
            command,
            cwd=str(working_folder),
            close_fds=True,
            creationflags=creationflags,
        )
    except OSError as error:
        print("CLAP presence window unavailable:", type(error).__name__)
