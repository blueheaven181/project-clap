"""Windows system-tray shell for Project CLAP.

Preview mode intentionally does not start, stop, or control the listener.
"""

import argparse
import subprocess
import sys
import threading
import time
from pathlib import Path

import pystray
from PIL import Image, ImageDraw
from runtime_paths import DATA_ROOT, IS_FROZEN, SOURCE_ROOT, data_path


PROJECT_FOLDER = SOURCE_ROOT
WORKING_FOLDER = DATA_ROOT if IS_FROZEN else SOURCE_ROOT
LOG_FOLDER = data_path("data", "private", "logs")


def listener_command():
    if getattr(sys, "frozen", False):
        return [sys.executable, "--listener"]
    return [sys.executable, str(PROJECT_FOLDER / "src" / "clap_detector.py")]


def orb_command(live=True):
    if getattr(sys, "frozen", False):
        command = [sys.executable, "--orb"]
    else:
        command = [
            str(Path(sys.executable).with_name("pythonw.exe"))
            if Path(sys.executable).with_name("pythonw.exe").exists()
            else sys.executable,
            str(PROJECT_FOLDER / "src" / "clap_floating_orb_preview.py"),
        ]
    if live:
        command.append("--live")
    return command


class ClapController:
    """Own exactly the listener process launched from the tray."""

    def __init__(self, popen=subprocess.Popen):
        self.process = None
        self._popen = popen
        self._lock = threading.Lock()

    def is_running(self):
        return self.process is not None and self.process.poll() is None

    def start(self):
        with self._lock:
            if self.is_running():
                return False
            LOG_FOLDER.mkdir(parents=True, exist_ok=True)
            log_path = LOG_FOLDER / "clap.log"
            log_handle = log_path.open("a", encoding="utf-8")
            self.process = self._popen(
                listener_command(),
                cwd=str(WORKING_FOLDER),
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                creationflags=(
                    subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                ),
            )
            return True

    def stop(self, timeout=5):
        with self._lock:
            if not self.is_running():
                self.process = None
                return False
            self.process.terminate()
            try:
                self.process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=timeout)
            self.process = None
        from presence_state import stop_presence_window

        stop_presence_window()
        return True

    def restart(self):
        self.stop()
        return self.start()


def create_tray_image(size=64):
    """Create a small CLAP particle-orb icon in memory."""

    image = Image.new("RGBA", (size, size), (7, 8, 22, 255))
    draw = ImageDraw.Draw(image)
    center = size / 2
    colors = ("#29f2db", "#5575c8", "#a35cff")
    for ring, count in ((22, 22), (16, 15), (9, 8)):
        for index in range(count):
            import math

            angle = math.tau * index / count + ring * 0.04
            x = center + math.cos(angle) * ring
            y = center + math.sin(angle) * ring
            radius = 1.4 if ring < 20 else 1.1
            draw.ellipse(
                (x - radius, y - radius, x + radius, y + radius),
                fill=colors[(index + ring) % len(colors)],
            )
    draw.ellipse((29, 29, 35, 35), fill="#d7fbff")
    return image


def open_orb(_icon=None, _item=None):
    """Open a standalone floating orb without starting the listener."""

    subprocess.Popen(
        orb_command(live=True),
        cwd=str(WORKING_FOLDER),
        close_fds=True,
    )


def preview_menu():
    return pystray.Menu(
        pystray.MenuItem("CLAP — Tray Preview", None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Status: Preview only", None, enabled=False),
        pystray.MenuItem("Open Floating Orb", open_orb),
        pystray.MenuItem("Start listening", None, enabled=False),
        pystray.MenuItem("Pause listening", None, enabled=False),
        pystray.MenuItem("Restart CLAP", None, enabled=False),
        pystray.MenuItem("Settings (coming next)", None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Exit Preview", lambda icon, _item: icon.stop()),
    )


def application_menu(controller, icon):
    from presence_state import stop_presence_window

    def refresh():
        icon.update_menu()

    def start(_icon=None, _item=None):
        controller.start()
        refresh()

    def pause(_icon=None, _item=None):
        controller.stop()
        refresh()

    def restart(_icon=None, _item=None):
        controller.restart()
        refresh()

    def hide_orb(_icon=None, _item=None):
        stop_presence_window()

    def exit_clap(_icon=None, _item=None):
        controller.stop()
        icon.stop()

    return pystray.Menu(
        pystray.MenuItem("Project CLAP", None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(
            lambda _item: "Status: Running" if controller.is_running() else "Status: Paused",
            None,
            enabled=False,
        ),
        pystray.MenuItem("Show Orb", open_orb),
        pystray.MenuItem("Hide Orb", hide_orb),
        pystray.MenuItem("Start listening", start, enabled=lambda _item: not controller.is_running()),
        pystray.MenuItem("Pause listening", pause, enabled=lambda _item: controller.is_running()),
        pystray.MenuItem("Restart CLAP", restart, enabled=lambda _item: controller.is_running()),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Exit CLAP", exit_clap),
    )


def run_preview():
    icon = pystray.Icon(
        "ProjectCLAPPreview",
        create_tray_image(),
        "Project CLAP — Tray Preview",
        preview_menu(),
    )
    icon.run()


def run_application():
    controller = ClapController()
    icon = pystray.Icon(
        "ProjectCLAP",
        create_tray_image(),
        "Project CLAP",
    )
    icon.menu = application_menu(controller, icon)
    controller.start()
    icon.run()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", action="store_true")
    parser.add_argument("--listener", action="store_true")
    parser.add_argument("--orb", action="store_true")
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    selected_modes = sum((args.preview, args.listener, args.orb))
    if selected_modes > 1:
        raise SystemExit("Select only one CLAP runtime mode.")
    if args.listener:
        import clap_detector  # noqa: F401 - module is the listener entry point
    elif args.orb:
        from clap_floating_orb_preview import (
            FloatingOrbPreview,
            acquire_orb_instance,
        )

        if acquire_orb_instance():
            FloatingOrbPreview(live=args.live).run()
    elif args.preview:
        run_preview()
    else:
        run_application()


if __name__ == "__main__":
    main()
