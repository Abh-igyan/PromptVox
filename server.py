"""
Localhost HTTP Bridge for Antigravity Voice
Listens on 127.0.0.1:5998 to allow VS Code, scripts, or extensions to trigger the mic.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading
from logger import log

class VoiceRequestHandler(BaseHTTPRequestHandler):
    engine = None
    ui = None

    def log_message(self, format, *args):
        pass

    def _send_json(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_GET(self):
        log(f"HTTP GET request: {self.path}")
        if self.path.startswith("/toggle"):
            auto_send = "auto_send=1" in self.path
            if self.ui:
                self.ui.threadsafe_toggle()
            elif self.engine:
                self.engine.toggle(auto_send=auto_send)
            self._send_json({"status": "toggled", "is_recording": getattr(self.engine, "is_recording", False)})

        elif self.path.startswith("/start"):
            auto_send = "auto_send=1" in self.path
            if self.engine and not self.engine.is_recording:
                if self.ui:
                    self.ui.threadsafe_toggle()
                else:
                    self.engine.start_recording(auto_send=auto_send)
            self._send_json({"status": "started", "is_recording": True})

        elif self.path == "/stop":
            if self.engine and self.engine.is_recording:
                auto_send = getattr(self.ui, "auto_send", False) if self.ui else False
                self.engine.stop_and_transcribe(auto_send=auto_send)
            self._send_json({"status": "stopped", "is_recording": False})

        elif self.path == "/status":
            state = getattr(self.ui, "state", "idle") if self.ui else ("listening" if getattr(self.engine, "is_recording", False) else "idle")
            self._send_json({
                "status": "ok",
                "is_recording": getattr(self.engine, "is_recording", False),
                "state": state,
                "auto_send": getattr(self.ui, "auto_send", False) if self.ui else False,
                "last_text": getattr(self.engine, "last_transcribed_text", "")
            })
        elif self.path == "/ping":
            self._send_json({"status": "pong"})
        else:
            self._send_json({"error": "not found"}, code=404)


def start_server(engine, ui=None, port=5998):
    VoiceRequestHandler.engine = engine
    VoiceRequestHandler.ui = ui
    try:
        server = HTTPServer(("127.0.0.1", port), VoiceRequestHandler)
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()
        log(f"HTTP Server listening on 127.0.0.1:{port}")
        return server
    except Exception as e:
        log(f"Warning: Could not start local HTTP server on port {port}: {e}")
        return None
