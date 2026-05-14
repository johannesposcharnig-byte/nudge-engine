"""Minimal local HTTP API for guarded Nudge Engine analysis."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from typing import Any

from .analysis_service import run_analysis


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
MAX_REQUEST_BYTES = 2_000_000


def analyze_payload(payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
    """Validate and analyze a JSON payload without leaking raw exceptions."""

    if not isinstance(payload, dict):
        return 400, _error("invalid_payload", "Request body must be a JSON object.")
    if "customer_rows" not in payload:
        return 400, _error("missing_customer_rows", "Payload must include customer_rows.")
    if not isinstance(payload.get("customer_rows"), list):
        return 400, _error("invalid_customer_rows", "customer_rows must be a list of objects.")
    if "question" not in payload:
        payload = {**payload, "question": "Analyze activation and recommend safe next steps."}
    try:
        return 200, run_analysis(payload)
    except Exception:
        return 500, _error(
            "analysis_failed",
            "Analysis failed safely. Check server logs in development; no raw exception is exposed in API output.",
        )


def _error(code: str, message: str) -> dict[str, Any]:
    return {
        "error": {
            "code": code,
            "message": message,
        }
    }


class NudgeEngineRequestHandler(BaseHTTPRequestHandler):
    server_version = "NudgeEngineLocalAPI/0.1"

    def do_OPTIONS(self) -> None:
        self._send_json(204, {})

    def do_GET(self) -> None:
        if self.path == "/health":
            self._send_json(200, {"status": "ok", "service": "nudge-engine-local-api"})
            return
        self._send_json(404, _error("not_found", "Endpoint not found."))

    def do_POST(self) -> None:
        if self.path != "/analyze":
            self._send_json(404, _error("not_found", "Endpoint not found."))
            return
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length <= 0:
            self._send_json(400, _error("empty_body", "Request body is required."))
            return
        if length > MAX_REQUEST_BYTES:
            self._send_json(413, _error("payload_too_large", "Request body exceeds local API limit."))
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except json.JSONDecodeError:
            self._send_json(400, _error("invalid_json", "Request body must be valid JSON."))
            return
        status, body = analyze_payload(payload)
        self._send_json(status, body)

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _send_json(self, status: int, body: dict[str, Any]) -> None:
        raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        if status != 204:
            self.wfile.write(raw)


def run_server(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    server = ThreadingHTTPServer((host, port), NudgeEngineRequestHandler)
    print(f"Nudge Engine local API running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
