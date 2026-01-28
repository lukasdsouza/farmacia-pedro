import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from src.chat.engine import ChatEngine
from src.core.config import load_settings


class ChatHandler(BaseHTTPRequestHandler):
    engine = None

    def _send(self, status: int, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/health":
            self._send(200, {"ok": True})
            return
        self._send(404, {"ok": False, "error": "not_found"})

    def do_POST(self):
        if self.path != "/webhook":
            self._send(404, {"ok": False, "error": "not_found"})
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8", errors="ignore")
        try:
            payload = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            self._send(400, {"ok": False, "error": "invalid_json"})
            return

        user_id = payload.get("from") or payload.get("user") or payload.get("session_id") or "atendimento"
        text = payload.get("text") or payload.get("message") or ""
        if not text:
            self._send(400, {"ok": False, "error": "missing_text"})
            return

        response = self.engine.handle_message(user_id, text)
        self._send(200, {"ok": True, "reply": response})

    def log_message(self, format, *args):
        return


def main():
    settings = load_settings()
    ChatHandler.engine = ChatEngine(settings)
    server = HTTPServer((settings.chat_webhook_host, settings.chat_webhook_port), ChatHandler)
    print(f"Webhook ativo em http://{settings.chat_webhook_host}:{settings.chat_webhook_port}/webhook")
    server.serve_forever()


if __name__ == "__main__":
    main()
