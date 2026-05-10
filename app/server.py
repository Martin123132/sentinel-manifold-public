"""Local HTTP server for the Sentinel Manifold MVP."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from auth import auth_required, is_admin_authorized, is_authorized, public_demo_enabled
from evidence import build_evidence_bundle, list_evidence_packs, load_evidence_pack, save_evidence_pack, verify_evidence_pack
from guardrail import run_guardrail
from openai_compat import run_chat_completions, run_chat_completions_stream
from policies import apply_policy_template, list_policy_templates
from providers import ProviderError, build_generation_payload, generate_candidates, list_providers
from samples import DEMO_PAYLOAD, DEMO_SUITE
from suites import run_suite


ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = ROOT / "web"
EVIDENCE_DIR = ROOT / "out" / "audits"
PUBLIC_DEMO_GET_PATHS = {"/api/demo", "/api/demo-suite", "/api/policies", "/api/providers"}
PUBLIC_DEMO_POST_PATHS = {"/api/check", "/api/suite"}
MAX_PUBLIC_BODY_BYTES = 200_000
MAX_PUBLIC_TEXT_CHARS = 24_000
MAX_PUBLIC_REFERENCES = 20
MAX_PUBLIC_CANDIDATES = 5
MAX_PUBLIC_SUITE_CASES = 5


class SentinelHandler(BaseHTTPRequestHandler):
    server_version = "SentinelManifold/0.1"

    def do_OPTIONS(self) -> None:
        self._send_json({"ok": True})

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            self._send_json(
                {
                    "ok": True,
                    "service": "sentinel-manifold",
                    "auth_required": auth_required(),
                    "public_demo": public_demo_enabled(),
                    "admin_auth_configured": auth_required(),
                }
            )
            return
        if self._requires_auth("GET", parsed.path) and not self._is_authorized_for_route("GET", parsed.path):
            self._send_auth_error()
            return
        if parsed.path == "/api/demo":
            self._send_json(DEMO_PAYLOAD)
            return
        if parsed.path == "/api/demo-suite":
            self._send_json(DEMO_SUITE)
            return
        if parsed.path == "/api/policies":
            self._send_json({"policies": list_policy_templates()})
            return
        if parsed.path == "/api/providers":
            providers = list_providers()
            if self._is_public_sandbox_request("GET", parsed.path):
                providers = [provider for provider in providers if provider["id"] == "local_demo"]
            self._send_json({"providers": providers})
            return
        if parsed.path == "/api/audits/export":
            limit = _parse_limit(parsed.query, default=25)
            self._send_zip(build_evidence_bundle(EVIDENCE_DIR, limit=limit), filename="sentinel-evidence-bundle.zip")
            return
        if parsed.path == "/api/audits":
            limit = _parse_limit(parsed.query, default=25)
            self._send_json({"audits": list_evidence_packs(EVIDENCE_DIR, limit=limit)})
            return
        if parsed.path.startswith("/api/audits/"):
            audit_path = parsed.path.rstrip("/")
            verify_only = audit_path.endswith("/verify")
            check_id = audit_path.split("/")[-2] if verify_only else audit_path.rsplit("/", 1)[-1]
            file_path = EVIDENCE_DIR / f"{check_id}.evidence.json"
            if not file_path.exists():
                self._send_json({"error": "audit_not_found"}, status=404)
                return
            if verify_only:
                self._send_json(verify_evidence_pack(file_path))
                return
            self._send_json(load_evidence_pack(file_path))
            return
        self._serve_static(parsed.path)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path not in {"/api/check", "/api/generate-check", "/api/suite", "/v1/chat/completions"}:
            self._send_json({"error": "not_found"}, status=404)
            return
        if self._requires_auth("POST", parsed.path) and not self._is_authorized_for_route("POST", parsed.path):
            self._send_auth_error()
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if self._is_public_sandbox_request("POST", parsed.path) and length > MAX_PUBLIC_BODY_BYTES:
                self._send_json(
                    {
                        "error": "public_demo_limit",
                        "detail": f"Public demo requests are limited to {MAX_PUBLIC_BODY_BYTES} bytes.",
                    },
                    status=413,
                )
                return
            body = self.rfile.read(length).decode("utf-8")
            payload = json.loads(body or "{}")
            if self._is_public_sandbox_request("POST", parsed.path):
                validation_error = self._public_demo_validation_error(parsed.path, payload)
                if validation_error:
                    self._send_json({"error": "public_demo_limit", "detail": validation_error}, status=400)
                    return
            if parsed.path == "/v1/chat/completions":
                if payload.get("stream") is True:
                    self._send_sse(run_chat_completions_stream(payload, EVIDENCE_DIR))
                    return
                self._send_json(run_chat_completions(payload, EVIDENCE_DIR))
                return
            if parsed.path == "/api/suite":
                save_evidence = not self._is_public_sandbox_request("POST", parsed.path)
                self._send_json(run_suite(payload, EVIDENCE_DIR, save_evidence=save_evidence))
                return
            if parsed.path == "/api/generate-check":
                generated = generate_candidates(payload)
                payload = build_generation_payload(payload, generated)
            normalized_payload = apply_policy_template(payload)
            result = run_guardrail(normalized_payload)
            if normalized_payload.get("provider_trace"):
                result["provider_trace"] = normalized_payload["provider_trace"]
                result["provider"] = normalized_payload.get("provider")
                result["model"] = normalized_payload.get("model")
            if self._is_public_sandbox_request("POST", parsed.path):
                result["evidence"] = {"saved": False, "reason": "public_demo"}
            else:
                result["evidence"] = save_evidence_pack(normalized_payload, result, EVIDENCE_DIR)
            self._send_json(result)
        except json.JSONDecodeError:
            self._send_json({"error": "invalid_json"}, status=400)
        except ProviderError as exc:
            self._send_json({"error": "provider_failed", "detail": str(exc)}, status=502)
        except Exception as exc:  # pragma: no cover - visible API protection
            self._send_json({"error": "check_failed", "detail": str(exc)}, status=500)

    def log_message(self, format: str, *args: object) -> None:
        print(f"[sentinel] {self.address_string()} - {format % args}")

    def _serve_static(self, path: str) -> None:
        if path in {"", "/"}:
            file_path = WEB_ROOT / "index.html"
        else:
            relative = unquote(path.lstrip("/"))
            file_path = (WEB_ROOT / relative).resolve()
            if not str(file_path).startswith(str(WEB_ROOT.resolve())):
                self._send_json({"error": "invalid_path"}, status=400)
                return

        if not file_path.exists() or not file_path.is_file():
            self._send_json({"error": "not_found"}, status=404)
            return

        content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        content = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)

    def _send_json(self, payload: dict, status: int = 200) -> None:
        content = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-API-Key")
        self.end_headers()
        self.wfile.write(content)

    def _send_zip(self, content: bytes, *, filename: str) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "application/zip")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-API-Key")
        self.end_headers()
        self.wfile.write(content)

    def _send_sse(self, chunks: list[str]) -> None:
        content_length = sum(len(chunk.encode("utf-8")) for chunk in chunks)
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Content-Length", str(content_length))
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "close")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-API-Key")
        self.end_headers()
        for chunk in chunks:
            self.wfile.write(chunk.encode("utf-8"))
            self.wfile.flush()
        self.close_connection = True

    def _send_auth_error(self) -> None:
        self._send_json(
            {
                "error": "unauthorized",
                "detail": "Set Authorization: Bearer <SENTINEL_API_KEY> or X-API-Key.",
            },
            status=401,
        )

    def _is_authorized_for_route(self, method: str, path: str) -> bool:
        if not public_demo_enabled():
            return is_authorized(self.headers)
        if is_admin_authorized(self.headers):
            return True
        return self._is_public_demo_route(method, path)

    def _is_public_sandbox_request(self, method: str, path: str) -> bool:
        return public_demo_enabled() and not is_admin_authorized(self.headers) and self._is_public_demo_route(method, path)

    @staticmethod
    def _requires_auth(method: str, path: str) -> bool:
        if method == "GET" and path == "/api/health":
            return False
        return path.startswith("/api/") or path.startswith("/v1/")

    @staticmethod
    def _is_public_demo_route(method: str, path: str) -> bool:
        if method == "GET":
            return path in PUBLIC_DEMO_GET_PATHS
        if method == "POST":
            return path in PUBLIC_DEMO_POST_PATHS
        return False

    @staticmethod
    def _public_demo_validation_error(path: str, payload: object) -> str | None:
        if not isinstance(payload, dict):
            return "Public demo requests must be JSON objects."
        if _text_size(payload) > MAX_PUBLIC_TEXT_CHARS:
            return f"Public demo payload text is limited to {MAX_PUBLIC_TEXT_CHARS} characters."

        if path == "/api/check":
            return _validate_public_check_payload(payload)
        if path == "/api/suite":
            return _validate_public_suite_payload(payload)
        return None


def _validate_public_check_payload(payload: dict) -> str | None:
    references = payload.get("references", [])
    candidates = payload.get("candidates", [])
    provider = str(payload.get("provider") or "local_demo")
    if provider != "local_demo":
        return "Public demo checks only allow the local_demo provider."
    if not isinstance(references, list) or len(references) > MAX_PUBLIC_REFERENCES:
        return f"Public demo checks are limited to {MAX_PUBLIC_REFERENCES} references."
    if not isinstance(candidates, list) or len(candidates) > MAX_PUBLIC_CANDIDATES:
        return f"Public demo checks are limited to {MAX_PUBLIC_CANDIDATES} candidates."
    return None


def _validate_public_suite_payload(payload: dict) -> str | None:
    provider = str(payload.get("provider") or "local_demo")
    if provider != "local_demo":
        return "Public demo suites only allow the local_demo provider."

    cases = payload.get("cases")
    if not isinstance(cases, list):
        return "Public demo suites must include a cases array."
    if len(cases) > MAX_PUBLIC_SUITE_CASES:
        return f"Public demo suites are limited to {MAX_PUBLIC_SUITE_CASES} cases."

    for case in cases:
        if not isinstance(case, dict):
            return "Public demo suite cases must be objects."
        case_provider = str(case.get("provider") or provider)
        if case_provider != "local_demo":
            return "Public demo suite cases only allow the local_demo provider."
        references = case.get("references", payload.get("references", []))
        candidates = case.get("candidates", [])
        if not isinstance(references, list) or len(references) > MAX_PUBLIC_REFERENCES:
            return f"Public demo suite cases are limited to {MAX_PUBLIC_REFERENCES} references."
        if candidates and (not isinstance(candidates, list) or len(candidates) > MAX_PUBLIC_CANDIDATES):
            return f"Public demo suite cases are limited to {MAX_PUBLIC_CANDIDATES} candidates."
        candidate_count = _public_candidate_count(case.get("candidate_count") or payload.get("candidate_count") or 3)
        if candidate_count is None:
            return "Public demo candidate_count must be a number."
        if candidate_count > MAX_PUBLIC_CANDIDATES:
            return f"Public demo generated cases are limited to {MAX_PUBLIC_CANDIDATES} candidates."
    return None


def _public_candidate_count(value: object) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _text_size(value: object) -> int:
    if isinstance(value, str):
        return len(value)
    if isinstance(value, dict):
        return sum(len(str(key)) + _text_size(item) for key, item in value.items())
    if isinstance(value, list):
        return sum(_text_size(item) for item in value)
    return len(str(value))


def _parse_limit(query: str, *, default: int) -> int:
    raw = parse_qs(query).get("limit", [str(default)])[0]
    try:
        return max(0, int(raw))
    except (TypeError, ValueError):
        return default


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Sentinel Manifold locally.")
    parser.add_argument("--host", default=os.environ.get("HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8787")))
    args = parser.parse_args()

    address = (args.host, args.port)
    httpd = ThreadingHTTPServer(address, SentinelHandler)
    print(f"Sentinel Manifold running at http://{args.host}:{args.port}")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
