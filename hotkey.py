"""
Global Hotkey Listener for Antigravity Voice
Listens globally for Alt+V, F8, Ctrl+Alt+V, and Ctrl+Shift+V to toggle voice typing.
"""

from pynput import keyboard
from logger import log

class HotkeyListener:
    def __init__(self, on_trigger):
        self.on_trigger = on_trigger
        self.ctrl_pressed = False
        self.alt_pressed = False
        self.shift_pressed = False
        self.listener = None

    def start(self):
        log("HotkeyListener starting for Alt+V, F8, Ctrl+Alt+V, Ctrl+Shift+V...")

        def on_press(key):
            try:
                # F8 key (or Fn+F8 on laptops)
                if key == keyboard.Key.f8:
                    log("F8 hotkey detected")
                    self.on_trigger()
                    return

                if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
                    self.ctrl_pressed = True
                elif key in (keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt_gr):
                    self.alt_pressed = True
                elif key in (keyboard.Key.shift, keyboard.Key.shift_r):
                    self.shift_pressed = True
                elif hasattr(key, 'char') and key.char:
                    ch = key.char.lower()
                    # Alt + V (one hand quick shortcut)
                    if ch == 'v' and self.alt_pressed and not self.ctrl_pressed:
                        log("Alt+V hotkey detected")
                        self.on_trigger()
                    # Ctrl + Alt + V
                    elif ch == 'v' and self.ctrl_pressed and self.alt_pressed:
                        log("Ctrl+Alt+V hotkey detected")
                        self.on_trigger()
                    # Ctrl + Shift + V
                    elif ch == 'v' and self.ctrl_pressed and self.shift_pressed:
                        log("Ctrl+Shift+V hotkey detected")
                        self.on_trigger()
            except Exception as e:
                log(f"Hotkey press error: {e}")

        def on_release(key):
            try:
                if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
                    self.ctrl_pressed = False
                elif key in (keyboard.Key.alt_l, keyboard.Key.alt_r, keyboard.Key.alt_gr):
                    self.alt_pressed = False
                elif key in (keyboard.Key.shift, keyboard.Key.shift_r):
                    self.shift_pressed = False
            except Exception:
                pass

        self.listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.listener.daemon = True
        self.listener.start()
        log("HotkeyListener running")
