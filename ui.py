"""
Antigravity Voice Floating Widget
Thread-safe, sleek floating pill widget (ChatGPT & Gemini web style)
with dynamic waveform visualizer and focus-preserving window attributes.
"""

import sys
import os
import json
import time
import math
import ctypes
import tkinter as tk
from logger import log

GWL_EXSTYLE = -20
WS_EX_NOACTIVATE = 0x08000000
WS_EX_TOPMOST = 0x00000008

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

def load_config():
    default_config = {
        "x": 980,
        "y": 590,
        "auto_send": False,
        "hotkey": "F8"
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                default_config.update(data)
        except Exception:
            pass
    return default_config

def save_config(config):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except Exception:
        pass


class VoiceFloatingPill:
    def __init__(self, engine):
        self.engine = engine
        self.config = load_config()

        self.root = tk.Tk()
        self.root.title("Antigravity Voice")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.96)

        # Transparent outer background
        self.root.attributes("-transparentcolor", "#000001")
        self.root.configure(bg="#000001")

        self.width = 230
        self.height = 44

        # Validate screen bounds (1280x720 safe default)
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        self.x = self.config.get("x", 980)
        self.y = self.config.get("y", 590)

        # Clamp inside visible desktop area (above taskbar)
        if self.x > screen_w - self.width - 20 or self.x < 10:
            self.x = screen_w - self.width - 40
        if self.y > screen_h - self.height - 60 or self.y < 10:
            self.y = screen_h - self.height - 80

        self.root.geometry(f"{self.width}x{self.height}+{self.x}+{self.y}")

        # Windows focus-preservation (WS_EX_NOACTIVATE)
        self._set_no_activate()

        # Canvas for custom rendering
        self.canvas = tk.Canvas(
            self.root,
            width=self.width,
            height=self.height,
            bg="#000001",
            highlightthickness=0,
            cursor="hand2"
        )
        self.canvas.pack(fill="both", expand=True)

        # State tracking
        self.state = "loading"
        self.status_text = "Loading STT model..."
        self.volume_level = 0.0
        self.recording_start_time = 0
        self.pulse_phase = 0.0
        self.auto_send = self.config.get("auto_send", False)

        # Dragging variables
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._click_moved = False

        # Bindings
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Button-3>", self._toggle_auto_send)

        # Wire thread-safe engine callbacks
        self.engine.on_state_change = self.threadsafe_state_change
        self.engine.on_volume = self.threadsafe_volume

        log(f"UI initialized at ({self.x}, {self.y}) on screen ({screen_w}x{screen_h})")
        self.animate()

    def _set_no_activate(self):
        try:
            self.root.update()
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id()) or self.root.winfo_id()
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_NOACTIVATE | WS_EX_TOPMOST)
            log("WS_EX_NOACTIVATE set successfully")
        except Exception as e:
            log(f"Failed to set WS_EX_NOACTIVATE: {e}")

    def threadsafe_toggle(self):
        self.root.after(0, self.toggle)

    def threadsafe_state_change(self, state, msg=""):
        self.root.after(0, lambda: self.update_state(state, msg))

    def threadsafe_volume(self, rms):
        self.volume_level = min(1.0, max(0.0, rms * 18.0))

    def _on_press(self, event):
        self._drag_start_x = event.x
        self._drag_start_y = event.y
        self._click_moved = False

    def _on_drag(self, event):
        dx = event.x - self._drag_start_x
        dy = event.y - self._drag_start_y
        if abs(dx) > 3 or abs(dy) > 3:
            self._click_moved = True
            new_x = self.root.winfo_x() + dx
            new_y = self.root.winfo_y() + dy
            self.root.geometry(f"+{new_x}+{new_y}")

    def _on_release(self, event):
        if not self._click_moved:
            log("UI clicked: toggling mic")
            self.toggle()
        else:
            self.config["x"] = self.root.winfo_x()
            self.config["y"] = self.root.winfo_y()
            save_config(self.config)
            log(f"Saved new UI position: ({self.config['x']}, {self.config['y']})")

    def _toggle_auto_send(self, event):
        self.auto_send = not self.auto_send
        self.config["auto_send"] = self.auto_send
        save_config(self.config)
        msg = "Auto-Send: ON" if self.auto_send else "Auto-Send: OFF"
        log(f"Toggled auto_send to {self.auto_send}")
        self.status_text = msg
        self.root.after(1200, lambda: self.update_state(self.state, "Ready (F8)"))

    def toggle(self):
        log(f"Toggle invoked. Current state: {self.state}")
        if self.state == "loading":
            return
        if self.state == "listening":
            self.engine.stop_and_transcribe(auto_send=self.auto_send)
        else:
            self.recording_start_time = time.time()
            self.engine.start_recording()

    def update_state(self, state, msg=""):
        log(f"UI state changed to '{state}' (msg: '{msg}')")
        self.state = state
        if msg:
            self.status_text = msg
        if state == "listening":
            self.recording_start_time = time.time()

    def _draw_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.canvas.create_polygon(points, smooth=True, **kwargs)

    def animate(self):
        self.pulse_phase += 0.16
        self.canvas.delete("all")

        w, h = self.width, self.height

        # Dynamic aesthetic styling
        if self.state == "listening":
            border_col = "#ef4444"
            bg_col = "#1c0d10"
        elif self.state == "transcribing":
            border_col = "#3b82f6"
            bg_col = "#0f172a"
        elif self.state == "done":
            border_col = "#10b981"
            bg_col = "#062817"
        else:
            border_col = "#3f3f46"
            bg_col = "#141418"

        self._draw_rounded_rect(2, 2, w - 2, h - 2, radius=21, fill=bg_col, outline=border_col, width=2)

        mic_cx = 24
        mic_cy = h // 2

        if self.state == "listening":
            pulse_rad = 13 + int(math.sin(self.pulse_phase) * 3) + int(self.volume_level * 5)
            self.canvas.create_oval(
                mic_cx - pulse_rad, mic_cy - pulse_rad,
                mic_cx + pulse_rad, mic_cy + pulse_rad,
                fill="#3b1115", outline="#ef4444", width=1
            )
            self.canvas.create_oval(
                mic_cx - 8, mic_cy - 8,
                mic_cx + 8, mic_cy + 8,
                fill="#ef4444", outline="#ffffff", width=1
            )
        elif self.state == "transcribing":
            spin_rad = 8
            x_s = mic_cx + int(math.cos(self.pulse_phase) * spin_rad)
            y_s = mic_cy + int(math.sin(self.pulse_phase) * spin_rad)
            self.canvas.create_oval(
                mic_cx - 8, mic_cy - 8, mic_cx + 8, mic_cy + 8,
                fill="#1e293b", outline="#3b82f6", width=1
            )
            self.canvas.create_oval(
                x_s - 3, y_s - 3, x_s + 3, y_s + 3,
                fill="#60a5fa", outline=""
            )
        elif self.state == "done":
            self.canvas.create_oval(
                mic_cx - 8, mic_cy - 8, mic_cx + 8, mic_cy + 8,
                fill="#10b981", outline="#ffffff", width=1
            )
            self.canvas.create_text(mic_cx, mic_cy, text="✓", fill="#ffffff", font=("Segoe UI", 9, "bold"))
        else:
            self.canvas.create_oval(
                mic_cx - 9, mic_cy - 9, mic_cx + 9, mic_cy + 9,
                fill="#27272a", outline="#52525b", width=1
            )
            self.canvas.create_text(mic_cx, mic_cy - 1, text="🎙️", font=("Segoe UI Emoji", 8))

        text_x = 44

        if self.state == "listening":
            # Dynamic Waveform Bars
            num_bars = 5
            bar_start_x = 46
            bar_width = 3
            bar_spacing = 4
            for i in range(num_bars):
                var = math.sin(self.pulse_phase * 1.6 + i * 0.9)
                bar_h = 4 + int(self.volume_level * 20 * (0.5 + 0.5 * var))
                bx = bar_start_x + i * (bar_width + bar_spacing)
                self.canvas.create_rectangle(
                    bx, mic_cy - bar_h // 2,
                    bx + bar_width, mic_cy + bar_h // 2,
                    fill="#ef4444", outline=""
                )

            elapsed = int(time.time() - self.recording_start_time)
            mins = elapsed // 60
            secs = elapsed % 60
            timer_text = f"{mins}:{secs:02d}"
            self.canvas.create_text(
                95, mic_cy,
                text=timer_text,
                fill="#fca5a5",
                font=("Consolas", 10, "bold"),
                anchor="w"
            )
            self.canvas.create_text(
                142, mic_cy,
                text="[Stop]",
                fill="#94a3b8",
                font=("Segoe UI", 8),
                anchor="w"
            )

        elif self.state == "transcribing":
            self.canvas.create_text(
                text_x, mic_cy,
                text="Transcribing...",
                fill="#93c5fd",
                font=("Segoe UI", 9, "bold"),
                anchor="w"
            )

        elif self.state == "done":
            self.canvas.create_text(
                text_x, mic_cy,
                text="Typed into Chat!",
                fill="#6ee7b7",
                font=("Segoe UI", 9, "bold"),
                anchor="w"
            )

        else:
            self.canvas.create_text(
                text_x, mic_cy - 6,
                text="Antigravity Voice",
                fill="#f1f5f9",
                font=("Segoe UI", 8, "bold"),
                anchor="w"
            )
            auto_str = "Auto-Send" if self.auto_send else "F8 or Click"
            self.canvas.create_text(
                text_x, mic_cy + 7,
                text=f"{self.status_text[:14]} • {auto_str}",
                fill="#94a3b8",
                font=("Segoe UI", 7),
                anchor="w"
            )

        badge_x = w - 16
        badge_col = "#10b981" if self.auto_send else "#52525b"
        self.canvas.create_oval(
            badge_x - 3, mic_cy - 3, badge_x + 3, mic_cy + 3,
            fill=badge_col, outline=""
        )

        self.root.after(35, self.animate)

    def run(self):
        self.root.mainloop()

    def destroy(self):
        try:
            self.root.destroy()
        except Exception:
            pass
