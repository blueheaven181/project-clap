"""Isolated borderless floating preview of CLAP's production orb."""

import math
import json
import socket
import sys
import time
import tkinter as tk
import ctypes
from pathlib import Path

from clap_presence_preview import STATE_STYLE, blend, make_points, rotate_point
from runtime_paths import data_path


SIZE = 510
TRANSPARENT = "#010203"
STATES = ("standby", "listening", "thinking", "speaking")
STATE_HOST = "127.0.0.1"
STATE_PORT = 47621
POSITION_PATH = data_path("data", "private", "floating_orb_position.json")
ORB_MUTEX_NAME = "Local\\ProjectCLAPFloatingOrb"
_orb_mutex_handle = None


def target_presentation(state):
    """Return adaptive orb scale and whether its status stays visible."""

    if state == "standby":
        return 0.72, False
    return 1.0, True


def acquire_orb_instance(kernel32=None):
    """Allow only one floating Production Orb per Windows session."""

    global _orb_mutex_handle
    if sys.platform != "win32":
        return True
    if kernel32 is None:
        kernel32 = ctypes.windll.kernel32
    kernel32.CreateMutexW.restype = ctypes.c_void_p
    handle = kernel32.CreateMutexW(None, False, ORB_MUTEX_NAME)
    if not handle:
        raise ctypes.WinError()
    if kernel32.GetLastError() == 183:
        kernel32.CloseHandle(handle)
        return False
    _orb_mutex_handle = handle
    return True


class FloatingOrbPreview:
    def __init__(self, live=False, position_path=POSITION_PATH):
        self.root = tk.Tk()
        self.root.title("CLAP Floating Orb Preview")
        self.position_path = Path(position_path)
        x, y = self.load_position()
        self.root.geometry(f"{SIZE}x{SIZE}+{x}+{y}")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg=TRANSPARENT)
        try:
            self.root.wm_attributes("-transparentcolor", TRANSPARENT)
        except tk.TclError:
            pass

        self.canvas = tk.Canvas(
            self.root,
            width=SIZE,
            height=SIZE,
            bg=TRANSPARENT,
            highlightthickness=0,
            cursor="fleur",
        )
        self.canvas.pack(fill="both", expand=True)
        self.points = make_points()
        self.particles = [
            self.canvas.create_oval(0, 0, 2, 2, outline="", fill="#20345d")
            for _ in self.points
        ]
        self.handle_shadow = self.canvas.create_oval(
            173, 457, 337, 497, fill="#0b1028", outline=""
        )
        self.handle = self.canvas.create_oval(
            176, 452, 334, 490, fill="#111936", outline="#334b92", width=1
        )
        self.status_item = self.canvas.create_text(
            SIZE / 2,
            471,
            text="STANDBY",
            fill=STATE_STYLE["standby"][0],
            font=("Segoe UI Semibold", 10),
        )
        self.state = "standby"
        self.started = time.perf_counter()
        self.state_changed_at = self.started
        self.visual_scale = 1.0
        self.drag_origin = None
        self.live = live
        self.available = True
        self.state_socket = None

        if live:
            self.state_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.state_socket.setblocking(False)
            try:
                self.state_socket.bind((STATE_HOST, STATE_PORT))
            except OSError:
                self.state_socket.close()
                self.state_socket = None
                self.available = False
                self.root.destroy()
                return

        for target in (self.canvas, self.root):
            target.bind("<ButtonPress-1>", self.begin_drag)
            target.bind("<B1-Motion>", self.drag)
        for item in (self.handle_shadow, self.handle, self.status_item):
            self.canvas.tag_bind(item, "<ButtonPress-1>", self.begin_drag)
            self.canvas.tag_bind(item, "<B1-Motion>", self.drag)
        self.root.bind("<space>", self.cycle_state)
        for key, state in (("1", "standby"), ("2", "listening"),
                           ("3", "thinking"), ("4", "speaking")):
            self.root.bind(key, lambda _event, value=state: self.set_state(value))
        self.root.bind("<Escape>", lambda _event: self.root.destroy())
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        if live:
            self.root.after(50, self.poll_live_state)
        self.root.after(20, self.animate)

    def load_position(self):
        try:
            saved = json.loads(self.position_path.read_text(encoding="utf-8"))
            return int(saved["x"]), int(saved["y"])
        except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
            return 120, 100

    def save_position(self):
        try:
            self.position_path.parent.mkdir(parents=True, exist_ok=True)
            self.position_path.write_text(
                json.dumps({"x": self.root.winfo_x(), "y": self.root.winfo_y()}),
                encoding="utf-8",
            )
        except OSError:
            pass

    def begin_drag(self, event):
        self.drag_origin = (
            event.x_root,
            event.y_root,
            self.root.winfo_x(),
            self.root.winfo_y(),
        )

    def drag(self, event):
        if not self.drag_origin:
            return
        start_x, start_y, window_x, window_y = self.drag_origin
        self.root.geometry(
            f"+{window_x + event.x_root - start_x}"
            f"+{window_y + event.y_root - start_y}"
        )
        self.save_position()

    def set_state(self, state):
        self.state = state
        self.state_changed_at = time.perf_counter()
        self.canvas.itemconfigure(
            self.status_item,
            text=state.upper(),
            fill=STATE_STYLE[state][0],
        )

    def cycle_state(self, _event=None):
        self.set_state(STATES[(STATES.index(self.state) + 1) % len(STATES)])

    def poll_live_state(self):
        if not self.state_socket or not self.root.winfo_exists():
            return
        try:
            while True:
                payload, _address = self.state_socket.recvfrom(64)
                state = payload.decode("ascii", errors="ignore")
                if state == "shutdown":
                    self.root.destroy()
                    return
                if state in STATES:
                    self.set_state(state)
        except BlockingIOError:
            pass
        except OSError:
            return
        self.root.after(50, self.poll_live_state)

    def animate(self):
        if not self.root.winfo_exists():
            return
        elapsed = time.perf_counter() - self.started
        primary, secondary, energy = STATE_STYLE[self.state]
        target_scale, persistent_status = target_presentation(self.state)
        self.visual_scale += (target_scale - self.visual_scale) * 0.10
        pulse_speed = {
            "standby": 1.0,
            "listening": 2.1,
            "thinking": 1.6,
            "speaking": 4.0,
        }[self.state]
        pulse = 1 + (0.025 + energy * 0.035) * math.sin(elapsed * pulse_speed)
        radius = 186 * pulse * self.visual_scale
        yaw = elapsed * (0.13 if self.state == "standby" else 0.25)
        pitch = 0.18 * math.sin(elapsed * 0.32)
        center_x = SIZE / 2
        center_y = SIZE / 2 - 17

        show_status = persistent_status or (
            time.perf_counter() - self.state_changed_at < 2.0
        )
        handle_state = "normal" if show_status else "hidden"
        for item in (self.handle_shadow, self.handle, self.status_item):
            self.canvas.itemconfigure(item, state=handle_state)
        if show_status:
            self.canvas.itemconfigure(
                self.handle,
                outline=blend(secondary, primary, 0.60),
                fill=blend("#0b1028", secondary, 0.18 + energy * 0.06),
            )
            self.canvas.itemconfigure(self.status_item, fill=primary)

        for index, (x, y, z, seed) in enumerate(self.points):
            wave = math.sin(elapsed * (2.0 + energy * 2.0) + y * 8 + seed * 2.5)
            deformation = 1 + wave * (0.018 + energy * 0.028)
            if self.state == "listening":
                deformation += max(0, y) * 0.035 * math.sin(elapsed * 3.2)
            elif self.state == "thinking":
                deformation += 0.035 * math.sin(
                    elapsed * 2.4 + math.atan2(z, x) * 3
                )
            elif self.state == "speaking":
                deformation += 0.05 * math.sin(elapsed * 5.5 + y * 10)

            rx, ry, rz = rotate_point(
                x * deformation, y * deformation, z * deformation, yaw, pitch
            )
            perspective = 1 + rz * 0.16
            px = center_x + rx * radius * perspective
            py = center_y + ry * radius * perspective
            depth = (rz + 1) / 2
            color = blend(secondary, primary, min(1, max(0, depth + 0.12)))
            if self.state == "standby":
                color = blend("#17203d", color, 0.56)
            size = (0.9 if depth < 0.34 else 1.5 if depth < 0.78 else 2.3)
            size *= 0.78 + self.visual_scale * 0.22
            self.canvas.coords(
                self.particles[index],
                px - size, py - size, px + size, py + size,
            )
            self.canvas.itemconfigure(self.particles[index], fill=color)

        self.root.after(25, self.animate)

    def run(self):
        if not self.available:
            return
        self.root.lift()
        self.root.focus_force()
        self.root.mainloop()
        if self.state_socket:
            self.state_socket.close()


if __name__ == "__main__":
    if acquire_orb_instance():
        FloatingOrbPreview(live="--live" in sys.argv[1:]).run()
