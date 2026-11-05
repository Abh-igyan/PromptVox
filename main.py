"""
Antigravity Voice Typing Wrapper
Runs as a silent, background STT engine for VS Code & Antigravity chat.
Supports Alt+V, F8, Ctrl+Alt+V, and localhost HTTP bridge for in-editor triggers.
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from logger import log
from engine import VoiceEngine
from server import start_server
from hotkey import HotkeyListener

def main():
    show_gui = "--gui" in sys.argv
    log("=" * 60)
    log(f"  Antigravity Voice Typing Starting (GUI={show_gui})...")
    log("=" * 60)

    # 1. Initialize Whisper Voice Engine
    engine = VoiceEngine(model_size="base.en")

    ui = None
    if show_gui:
        try:
            from ui import VoiceFloatingPill
            ui = VoiceFloatingPill(engine)
        except Exception as e:
            log(f"Could not initialize GUI: {e}. Falling back to headless mode.")
            ui = None

    # 2. Start HTTP Bridge on 127.0.0.1:5998
    server = start_server(engine, ui, port=5998)

    # 3. Start Global Hotkey Listener
    trigger_fn = ui.threadsafe_toggle if ui else (lambda: engine.toggle())
    hotkey = HotkeyListener(on_trigger=trigger_fn)
    hotkey.start()

    log("Antigravity Voice is ready! (Hotkeys: Alt+V, F8, Ctrl+Alt+V)")

    # 4. Main Event Loop
    if ui:
        try:
            ui.run()
        except KeyboardInterrupt:
            pass
        finally:
            log("Antigravity Voice shutting down")
            ui.destroy()
    else:
        # Headless daemon loop
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        log("Antigravity Voice daemon exiting")

if __name__ == "__main__":
    main()
