import os
import time
import threading

LOG_FILE = os.path.join(os.path.dirname(__file__), "debug.log")
_log_lock = threading.Lock()

def log(msg: str):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {msg}"
    print(entry)
    with _log_lock:
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(entry + "\n")
        except Exception:
            pass
