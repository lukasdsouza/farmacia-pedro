import json
import time
from collections import defaultdict
from http.server import BaseHTTPRequestHandler, HTTPServer

from src.chat.engine import ChatEngine
from src.core.config import load_settings

_MAX_BODY_BYTES = 16_384  # 16 KB
_MAX_TEXT_LEN = 2048
_RATE_LIMIT_RPM = 60
_rate_counters: dict = defaultdict(list)


def _check_rate_limit(ip: str) -> bool:
    now = time.time()
    window = now - 60
    _rate_counters[ip] = [t for t in _rate_counters[ip] if t > window]
    if len(_rate_counters[ip]) >= _RATE_LIMIT_RPM:
        return False
    _rate_counters[ip].append(now)
    return True


class ChatHandler(BaseHTTPRequestHandler):
    engine = None

    def _send(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def _cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._cors_headers()
        self.end_headers()

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send(200, {"ok": True})
            return
        self._send(404, {"ok": False, "error": "not_found"})

    def do_POST(self) -> None:
        if self.path != "/webhook":
            self._send(404, {"ok": False, "error": "not_found"})
            return

        ip = self.client_address[0]
        if not _check_rate_limit(ip):
            self._send(429, {"ok": False, "error": "rate_limit_exceeded"})
            return

        raw_length = int(self.headers.get("Content-Length", "0"))
        if raw_length > _MAX_BODY_BYTES:
            self._send(413, {"ok": False, "error": "payload_too_large"})
            return

        raw = self.rfile.read(min(raw_length, _MAX_BODY_BYTES)).decode("utf-8", errors="ignore")
        try:
            payload = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            self._send(400, {"ok": False, "error": "invalid_json"})
            return

        if not isinstance(payload, dict):
            self._send(400, {"ok": False, "error": "invalid_payload"})
            return

        user_id = str(payload.get("from") or payload.get("user") or payload.get("session_id") or "atendimento")[:128]
        text = str(payload.get("text") or payload.get("message") or "")
        if not text:
            self._send(400, {"ok": False, "error": "missing_text"})
            return
        if len(text) > _MAX_TEXT_LEN:
            self._send(400, {"ok": False, "error": "text_too_long"})
            return

        response = self.engine.handle_message(user_id, text)
        self._send(200, {"ok": True, "reply": response})

    def log_message(self, format, *args):
        return


def main() -> None:
    settings = load_settings()
    ChatHandler.engine = ChatEngine(settings)
    server = HTTPServer((settings.chat_webhook_host, settings.chat_webhook_port), ChatHandler)
    print(f"Webhook ativo em http://{settings.chat_webhook_host}:{settings.chat_webhook_port}/webhook")
    server.serve_forever()


if __name__ == "__main__":
    main()
