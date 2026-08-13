"""Standalone native-window prototype for CLAP's animated presence."""

import math
import random
import socket
import sys
import time
import tkinter as tk


WIDTH = 760
HEIGHT = 760
POINT_COUNT = 900
STATE_HOST = "127.0.0.1"
STATE_PORT = 47621
CENTER_X = WIDTH / 2
CENTER_Y = HEIGHT / 2 - 18

STATE_STYLE = {
    "standby": ("#5575c8", "#592a93", 0.18),
    "listening": ("#20ddff", "#256eff", 0.52),
    "thinking": ("#a35cff", "#1bbbea", 0.42),
    "speaking": ("#29f2db", "#655eff", 0.78),
}


def make_points():
    rng = random.Random(181)
    golden_angle = math.pi * (3 - math.sqrt(5))
    points = []
    for index in range(POINT_COUNT):
        y = 1 - (index / (POINT_COUNT - 1)) * 2
        radius = math.sqrt(max(0.0, 1 - y * y))
        theta = golden_angle * index
        points.append(
            (
                math.cos(theta) * radius,
                y,
                math.sin(theta) * radius,
                rng.uniform(-1.0, 1.0),
            )
        )
    return points


def rotate_point(x, y, z, yaw, pitch):
    cos_yaw, sin_yaw = math.cos(yaw), math.sin(yaw)
    x, z = x * cos_yaw - z * sin_yaw, x * sin_yaw + z * cos_yaw
    cos_pitch, sin_pitch = math.cos(pitch), math.sin(pitch)
    return x, y * cos_pitch - z * sin_pitch, y * sin_pitch + z * cos_pitch


def hex_to_rgb(color):
    return tuple(int(color[index:index + 2], 16) for index in (1, 3, 5))


def blend(first, second, amount):
    first_rgb, second_rgb = hex_to_rgb(first), hex_to_rgb(second)
    values = [
        int(first_rgb[index] * (1 - amount) + second_rgb[index] * amount)
        for index in range(3)
    ]
    return "#{:02x}{:02x}{:02x}".format(*values)


class PresencePreview:
    def __init__(self, live=False):
        self.root = tk.Tk()
        self.root.title("CLAP")
        self.root.geometry(f"{WIDTH}x{HEIGHT}+90+70")
        self.root.configure(bg="#070816")
        self.root.minsize(620, 620)

        self.canvas = tk.Canvas(
            self.root,
            width=WIDTH,
            height=HEIGHT,
            bg="#070816",
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)

        self.points = make_points()
        self.particles = [
            self.canvas.create_oval(0, 0, 2, 2, outline="", fill="#20345d")
            for _ in self.points
        ]
        self.state = "standby"
        self.started = time.perf_counter()
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

        self.state_item = self.canvas.create_text(
            WIDTH / 2,
            HEIGHT - 88,
            text="STANDBY",
            fill=STATE_STYLE["standby"][0],
            font=("Segoe UI Semibold", 13),
        )
        for key, state in (("1", "standby"), ("2", "listening"),
                           ("3", "thinking"), ("4", "speaking")):
            self.root.bind(key, lambda _event, value=state: self.set_state(value))
        self.root.bind("<Escape>", lambda _event: self.root.destroy())
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        if self.live:
            self.root.after(50, self.poll_live_state)
        self.root.after(20, self.animate)

    def set_state(self, state):
        self.state = state
        self.canvas.itemconfigure(
            self.state_item,
            text=state.upper(),
            fill=STATE_STYLE[state][0],
        )

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
                if state in STATE_STYLE:
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
        pulse_speed = {
            "standby": 1.0,
            "listening": 2.1,
            "thinking": 1.6,
            "speaking": 4.0,
        }[self.state]
        pulse = 1 + (0.025 + energy * 0.035) * math.sin(elapsed * pulse_speed)
        radius = 238 * pulse
        yaw = elapsed * (0.13 if self.state == "standby" else 0.25)
        pitch = 0.18 * math.sin(elapsed * 0.32)

        width = max(1, self.canvas.winfo_width())
        height = max(1, self.canvas.winfo_height())
        center_x, center_y = width / 2, height / 2 - 18

        rendered = []
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
                x * deformation,
                y * deformation,
                z * deformation,
                yaw,
                pitch,
            )
            perspective = 1 + rz * 0.16
            px = center_x + rx * radius * perspective
            py = center_y + ry * radius * perspective
            depth = (rz + 1) / 2
            color = blend(secondary, primary, min(1.0, max(0.0, depth + 0.12)))
            size = 1.0 if depth < 0.34 else 1.7 if depth < 0.78 else 2.5
            rendered.append((index, px, py, color, size))

        for index, px, py, color, size in rendered:
            self.canvas.coords(
                self.particles[index],
                px - size,
                py - size,
                px + size,
                py + size,
            )
            self.canvas.itemconfigure(self.particles[index], fill=color)

        self.canvas.coords(self.state_item, center_x, height - 88)
        self.root.after(25, self.animate)

    def run(self):
        if not self.available:
            return
        self.root.lift()
        self.root.focus_force()
        self.root.mainloop()
        if self.state_socket:
            self.state_socket.close()


def main():
    PresencePreview(live="--live" in sys.argv[1:]).run()


if __name__ == "__main__":
    main()
