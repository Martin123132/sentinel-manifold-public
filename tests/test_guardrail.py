from pathlib import Path
from contextlib import contextmanager
import io
import json
import os
import sys
import tempfile
import threading
import urllib.error
import urllib.request
import unittest
import zipfile
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from cli import main as cli_main
import server as server_module
from auth import auth_required, is_admin_authorized, is_authorized, public_demo_enabled
from evidence import list_evidence_packs, load_evidence_pack, save_evidence_pack, verify_evidence_pack
from guardrail import extract_relations, run_guardrail
from openai_compat import run_chat_completions, run_chat_completions_stream
from policies import apply_policy_template, list_policy_templates
from providers import ProviderError, build_generation_payload, generate_candidates, list_providers
from samples import DEMO_PAYLOAD, DEMO_SUITE
from suites import run_suite


@contextmanager
def run_test_server(env: dict[str, str]):
    with tempfile.TemporaryDirectory() as tmp:
        with patch.dict(os.environ, env, clear=False), patch.object(server_module, "EVIDENCE_DIR", Path(tmp)):
            httpd = server_module.ThreadingHTTPServer(("127.0.0.1", 0), server_module.SentinelHandler)
            thread = threading.Thread(target=httpd.serve_forever, daemon=True)
            thread.start()
            try:
                yield f"http://127.0.0.1:{httpd.server_address[1]}"
            finally:
                httpd.shutdown()
                httpd.server_close()
                thread.join(timeout=5)


def request_json(
    base_url: str,
    path: str,
    *,
    method: str = "GET",
    payload: dict | None = None,
    headers: dict[str, str] | None = None,
) -> tuple[int, dict]:
    request_headers = dict(headers or {})
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        request_headers["Content-Type"] = "application/json"
    request = urllib.request.Request(f"{base_url}{path}", data=data, headers=request_headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            body = response.read().decode("utf-8")
            return response.status, json.loads(body or "{}")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        return exc.code, json.loads(body or "{}")


def request_bytes(
    base_url: str,
    path: str,
    *,
    headers: dict[str, str] | None = None,
) -> tuple[int, bytes, object]:
    request = urllib.request.Request(f"{base_url}{path}", headers=dict(headers or {}), method="GET")
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, response.read(), response.headers
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(), exc.headers


class GuardrailTests(unittest.TestCase):
    def test_auth_is_disabled_without_api_key(self):
        with patch.dict(os.environ, {"SENTINEL_API_KEY": ""}):
            self.assertFalse(auth_required())
            self.assertTrue(is_authorized({}))

    def test_auth_accepts_bearer_and_x_api_key(self):
        with patch.dict(os.environ, {"SENTINEL_API_KEY": "secret"}):
            self.assertTrue(auth_required())
            self.assertTrue(is_admin_authorized({"Authorization": "Bearer secret"}))
            self.assertTrue(is_authorized({"Authorization": "Bearer secret"}))
            self.assertTrue(is_authorized({"X-API-Key": "secret"}))
            self.assertFalse(is_authorized({"Authorization": "Bearer wrong"}))

    def test_public_demo_flag_reads_truthy_values(self):
        with patch.dict(os.environ, {"SENTINEL_PUBLIC_DEMO": "true"}):
            self.assertTrue(public_demo_enabled())
        with patch.dict(os.environ, {"SENTINEL_PUBLIC_DEMO": "0"}):
            self.assertFalse(public_demo_enabled())

    def test_default_local_server_keeps_dev_routes_open(self):
        env = {"SENTINEL_API_KEY": "", "SENTINEL_PUBLIC_DEMO": ""}
        with run_test_server(env) as base_url:
            status, payload = request_json(base_url, "/api/providers")

        self.assertEqual(status, 200)
        self.assertGreaterEqual(len(payload["providers"]), 5)

    def test_private_hosted_server_requires_api_key(self):
        env = {"SENTINEL_API_KEY": "secret", "SENTINEL_PUBLIC_DEMO": ""}
        with run_test_server(env) as base_url:
            unauth_status, _ = request_json(base_url, "/api/providers")
            auth_status, payload = request_json(
                base_url,
                "/api/providers",
                headers={"Authorization": "Bearer secret"},
            )

        self.assertEqual(unauth_status, 401)
        self.assertEqual(auth_status, 200)
        self.assertGreaterEqual(len(payload["providers"]), 5)

    def test_policy_catalog_exposes_agent_tool_profile_api(self):
        env = {"SENTINEL_API_KEY": "", "SENTINEL_PUBLIC_DEMO": ""}
        with run_test_server(env) as base_url:
            status, payload = request_json(base_url, "/api/policies")

        self.assertEqual(status, 200)
        self.assertIn("agent_tool", {policy["id"] for policy in payload["policies"]})

    def test_public_demo_permits_only_sandbox_routes(self):
        env = {"SENTINEL_API_KEY": "secret", "SENTINEL_PUBLIC_DEMO": "true"}
        with run_test_server(env) as base_url:
            health_status, health = request_json(base_url, "/api/health")
            providers_status, providers = request_json(base_url, "/api/providers")
            demo_status, _ = request_json(base_url, "/api/demo")
            check_status, check = request_json(base_url, "/api/check", method="POST", payload=DEMO_PAYLOAD)
            suite_status, demo_suite = request_json(base_url, "/api/demo-suite")
            report_status, report = request_json(base_url, "/api/suite", method="POST", payload=demo_suite)
            audits_status, _ = request_json(base_url, "/api/audits")
            export_status, _ = request_json(base_url, "/api/audits/export")
            generate_status, _ = request_json(
                base_url,
                "/api/generate-check",
                method="POST",
                payload={"provider": "local_demo", "references": ["Earth orbits the Sun."]},
            )
            chat_status, _ = request_json(
                base_url,
                "/v1/chat/completions",
                method="POST",
                payload={"model": "sentinel-local-demo", "messages": []},
            )

        self.assertEqual(health_status, 200)
        self.assertTrue(health["public_demo"])
        self.assertEqual(providers_status, 200)
        self.assertEqual([provider["id"] for provider in providers["providers"]], ["local_demo"])
        self.assertEqual(demo_status, 200)
        self.assertEqual(check_status, 200)
        self.assertEqual(check["evidence"], {"saved": False, "reason": "public_demo"})
        self.assertEqual(suite_status, 200)
        self.assertEqual(report_status, 200)
        self.assertEqual(report["status"], "PASS")
        self.assertTrue(all(case["evidence"] is None for case in report["cases"]))
        self.assertEqual(audits_status, 401)
        self.assertEqual(export_status, 401)
        self.assertEqual(generate_status, 401)
        self.assertEqual(chat_status, 401)

    def test_public_demo_admin_key_unlocks_private_routes(self):
        env = {"SENTINEL_API_KEY": "secret", "SENTINEL_PUBLIC_DEMO": "true"}
        headers = {"Authorization": "Bearer secret"}
        with run_test_server(env) as base_url:
            providers_status, providers = request_json(base_url, "/api/providers", headers=headers)
            audits_status, audits = request_json(base_url, "/api/audits", headers=headers)

        self.assertEqual(providers_status, 200)
        self.assertGreaterEqual(len(providers["providers"]), 5)
        self.assertEqual(audits_status, 200)
        self.assertIn("audits", audits)

    def test_public_demo_admin_can_export_evidence_bundle(self):
        env = {"SENTINEL_API_KEY": "secret", "SENTINEL_PUBLIC_DEMO": "true"}
        headers = {"Authorization": "Bearer secret"}
        with run_test_server(env) as base_url:
            _, demo_suite = request_json(base_url, "/api/demo-suite")
            report_status, report = request_json(base_url, "/api/suite", method="POST", payload=demo_suite, headers=headers)
            bundle_status, bundle, bundle_headers = request_bytes(
                base_url,
                "/api/audits/export?limit=25",
                headers=headers,
            )
            first_check_id = report["cases"][0]["check_id"]
            pack_status, pack = request_json(base_url, f"/api/audits/{first_check_id}", headers=headers)

        self.assertEqual(report_status, 200)
        self.assertEqual(report["status"], "PASS")
        self.assertTrue(all(case["evidence"] for case in report["cases"]))
        self.assertEqual(bundle_status, 200)
        self.assertIn("application/zip", bundle_headers.get("Content-Type"))
        with zipfile.ZipFile(io.BytesIO(bundle)) as archive:
            names = set(archive.namelist())
            manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
            summary_md = archive.read("summary.md").decode("utf-8")

        self.assertEqual(manifest["schema_version"], "sentinel.evidence.bundle.v1")
        self.assertEqual(manifest["count"], report["summary"]["case_count"])
        self.assertEqual(manifest["summary"]["total_audits"], report["summary"]["case_count"])
        self.assertEqual(manifest["summary"]["emitted"], sum(1 for case in report["cases"] if case["action"] == "EMIT"))
        self.assertEqual(manifest["summary"]["blocked"], sum(1 for case in report["cases"] if case["action"] == "BLOCK"))
        self.assertEqual(manifest["summary"]["verified"], report["summary"]["case_count"])
        self.assertEqual(manifest["summary"]["failed_verification"], 0)
        self.assertEqual(set(manifest["summary"]["policy_profiles"]), {"regulated", "research", "support"})
        self.assertIn("summary.md", names)
        self.assertIn("Sentinel Evidence Bundle", summary_md)
        self.assertIn("Total audits: 5", summary_md)
        self.assertTrue(all(f"evidence/{case['check_id']}.evidence.json" in names for case in report["cases"]))
        self.assertTrue(all(f"verification/{case['check_id']}.verification.json" in names for case in report["cases"]))
        self.assertEqual(pack_status, 200)
        self.assertTrue(pack["integrity_valid"])

    def test_admin_evidence_bundle_empty_manifest(self):
        env = {"SENTINEL_API_KEY": "secret", "SENTINEL_PUBLIC_DEMO": "true"}
        headers = {"X-API-Key": "secret"}
        with run_test_server(env) as base_url:
            status, bundle, bundle_headers = request_bytes(base_url, "/api/audits/export", headers=headers)

        self.assertEqual(status, 200)
        self.assertIn("application/zip", bundle_headers.get("Content-Type"))
        with zipfile.ZipFile(io.BytesIO(bundle)) as archive:
            self.assertEqual(set(archive.namelist()), {"manifest.json", "summary.md"})
            manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
            summary_md = archive.read("summary.md").decode("utf-8")

        self.assertEqual(manifest["count"], 0)
        self.assertEqual(manifest["summary"]["total_audits"], 0)
        self.assertEqual(manifest["summary"]["emitted"], 0)
        self.assertEqual(manifest["summary"]["blocked"], 0)
        self.assertEqual(manifest["summary"]["verified"], 0)
        self.assertEqual(manifest["summary"]["failed_verification"], 0)
        self.assertEqual(manifest["summary"]["policy_profiles"], [])
        self.assertEqual(manifest["audits"], [])
        self.assertIn("No saved evidence packs were available", summary_md)

    def test_public_demo_rejects_hosted_provider_suite(self):
        env = {"SENTINEL_API_KEY": "secret", "SENTINEL_PUBLIC_DEMO": "true"}
        suite = {"provider": "openai", "cases": [{"references": ["Earth orbits the Sun."], "candidate_count": 1}]}
        with run_test_server(env) as base_url:
            status, payload = request_json(base_url, "/api/suite", method="POST", payload=suite)

        self.assertEqual(status, 400)
        self.assertEqual(payload["error"], "public_demo_limit")

    def test_supported_candidate_emits(self):
        result = run_guardrail(
            {
                "references": ["The capital of France is Paris."],
                "candidates": [
                    {"id": "bad", "label": "Bad", "text": "The capital of France is London."},
                    {"id": "good", "label": "Good", "text": "The capital of France is Paris."},
                ],
            }
        )

        self.assertEqual(result["action"], "EMIT")
        self.assertEqual(result["emitted_candidate_id"], "good")

    def test_all_bad_blocks(self):
        result = run_guardrail(
            {
                "references": ["Earth orbits the Sun."],
                "candidates": [
                    {"id": "a", "label": "A", "text": "The Sun orbits Earth."},
                    {"id": "b", "label": "B", "text": "Earth does not orbit the Sun."},
                ],
            }
        )

        self.assertEqual(result["action"], "BLOCK")

    def test_relation_extraction_keeps_direction(self):
        relations = [relation.key() for relation in extract_relations("The Sun orbits Earth.")]
        self.assertIn(("sun", "orbit", "earth"), relations)

    def test_agent_tool_relation_extraction_recognizes_tool_verbs(self):
        relations = [
            relation.key()
            for relation in extract_relations(
                "The calendar agent reads calendar events. The support agent deletes CRM records."
            )
        ]

        self.assertIn(("calendar agent", "read", "calendar events"), relations)
        self.assertIn(("support agent", "delete", "crm records"), relations)

    def test_result_is_json_serializable(self):
        result = run_guardrail(
            {
                "references": ["Water boils at 100 degrees Celsius at sea level."],
                "candidates": [{"id": "a", "label": "A", "text": "Water boils at 90 degrees Celsius."}],
            }
        )
        self.assertIn("reference_model", result)
        self.assertEqual(result["candidates"][0]["verdict"], "CONTRADICTION")

    def test_strict_overclaim_is_not_emit_safe(self):
        result = run_guardrail(
            {
                "references": [
                    "General relativity describes gravity as the curvature of spacetime caused by mass and energy."
                ],
                "candidates": [
                    {
                        "id": "a",
                        "label": "A",
                        "text": "General relativity fully solves gravity and proves there is no connection between gravity, mass, and energy.",
                    }
                ],
            }
        )
        self.assertEqual(result["action"], "BLOCK")
        self.assertFalse(result["candidates"][0]["safe_to_emit"])

    def test_policy_template_is_applied(self):
        payload = apply_policy_template({"policy_profile": "code_review"})
        self.assertEqual(payload["mode"], "balanced")
        self.assertFalse(payload["policy"]["overclaim_guards"])
        self.assertGreaterEqual(len(list_policy_templates()), 5)

    def test_agent_tool_policy_template_is_strict(self):
        payload = apply_policy_template({"policy_profile": "agent_tool"})

        self.assertEqual(payload["mode"], "strict")
        self.assertEqual(payload["policy_profile"], "agent_tool")
        self.assertEqual(payload["policy_name"], "Agent Tool Boundary")
        self.assertTrue(all(payload["policy"].values()))

    def test_agent_tool_policy_blocks_tool_boundary_drift(self):
        result = run_guardrail(
            {
                "policy_profile": "agent_tool",
                "references": [
                    "The calendar agent reads calendar events.",
                    "The calendar agent requires user approval.",
                ],
                "candidates": [
                    {
                        "id": "safe",
                        "label": "Safe",
                        "text": "The calendar agent reads calendar events. The calendar agent requires user approval.",
                    },
                    {
                        "id": "unsafe",
                        "label": "Unsafe",
                        "text": "The calendar agent stores customer credentials.",
                    },
                ],
            }
        )

        self.assertEqual(result["action"], "EMIT")
        self.assertEqual(result["emitted_candidate_id"], "safe")
        unsafe = next(candidate for candidate in result["candidates"] if candidate["id"] == "unsafe")
        self.assertFalse(unsafe["safe_to_emit"])
        self.assertIn("known_participant_unsupported_relation", {finding["code"] for finding in unsafe["findings"]})

    def test_agent_policy_suite_passes(self):
        suite = json.loads((ROOT / "samples" / "agent-policy-suite.json").read_text(encoding="utf-8"))
        report = run_suite(suite, save_evidence=False)

        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["summary"]["case_count"], 5)
        self.assertEqual(report["summary"]["failed"], 0)

    def test_integration_starter_suite_passes(self):
        suite = json.loads((ROOT / "samples" / "integration-starter-suite.json").read_text(encoding="utf-8"))
        report = run_suite(suite, save_evidence=False)

        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["summary"]["case_count"], 4)
        self.assertEqual(report["summary"]["failed"], 0)

    def test_external_adoption_suite_passes(self):
        suite = json.loads(
            (
                ROOT
                / "examples"
                / "external-adoption"
                / "support-assistant"
                / "sentinel-suite.json"
            ).read_text(encoding="utf-8")
        )
        report = run_suite(suite, save_evidence=False)

        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["summary"]["case_count"], 5)
        self.assertEqual(report["summary"]["failed"], 0)

    def test_evidence_pack_round_trip_verifies_integrity(self):
        payload = {
            "policy_profile": "support",
            "references": ["Earth orbits the Sun."],
            "candidates": [{"id": "a", "label": "A", "text": "Earth orbits the Sun."}],
        }
        result = run_guardrail(payload)
        with tempfile.TemporaryDirectory() as tmp:
            metadata = save_evidence_pack(apply_policy_template(payload), result, Path(tmp))
            pack = load_evidence_pack(Path(metadata["path"]))
            rows = list_evidence_packs(Path(tmp))

        self.assertTrue(pack["integrity_valid"])
        self.assertTrue(pack["verification"]["request_hashes_valid"])
        self.assertEqual(pack["check_id"], result["check_id"])
        self.assertEqual(rows[0]["check_id"], result["check_id"])

    def test_evidence_verification_reports_tampering(self):
        payload = {
            "policy_profile": "support",
            "references": ["Earth orbits the Sun."],
            "candidates": [{"id": "a", "label": "A", "text": "Earth orbits the Sun."}],
        }
        result = run_guardrail(payload)
        with tempfile.TemporaryDirectory() as tmp:
            metadata = save_evidence_pack(apply_policy_template(payload), result, Path(tmp))
            path = Path(metadata["path"])
            pack = json.loads(path.read_text(encoding="utf-8"))
            pack["request"]["references"].append("Tampered reference.")
            path.write_text(json.dumps(pack), encoding="utf-8")
            report = verify_evidence_pack(path)

        self.assertFalse(report["integrity_valid"])
        self.assertFalse(report["request_hashes_valid"])
        self.assertIn("integrity_digest_mismatch", report["errors"])
        self.assertIn("request_hash_mismatch", report["errors"])
        self.assertFalse(report["request_hashes"]["references_sha256"]["valid"])

    def test_cli_verify_evidence_strict_fails_on_tamper(self):
        payload = {
            "policy_profile": "support",
            "references": ["Earth orbits the Sun."],
            "candidates": [{"id": "a", "label": "A", "text": "Earth orbits the Sun."}],
        }
        result = run_guardrail(payload)
        with tempfile.TemporaryDirectory() as tmp:
            metadata = save_evidence_pack(apply_policy_template(payload), result, Path(tmp))
            path = Path(metadata["path"])
            with patch("sys.stdout", new_callable=io.StringIO):
                self.assertEqual(cli_main(["verify-evidence", "--input", str(path), "--strict"]), 0)
            pack = json.loads(path.read_text(encoding="utf-8"))
            pack["result"]["action"] = "BLOCK"
            path.write_text(json.dumps(pack), encoding="utf-8")
            with patch("sys.stdout", new_callable=io.StringIO):
                exit_code = cli_main(["verify-evidence", "--input", str(path), "--strict"])

        self.assertEqual(exit_code, 2)

    def test_cli_demo_writes_result_and_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "result.json"
            audits = Path(tmp) / "audits"
            exit_code = cli_main(["check", "--demo", "--out", str(out), "--evidence-dir", str(audits)])

            self.assertEqual(exit_code, 0)
            self.assertTrue(out.exists())
            self.assertTrue(any(audits.glob("*.evidence.json")))

    def test_local_provider_generation_can_be_guarded(self):
        payload = {
            "provider": "local_demo",
            "prompt": "Answer using the references.",
            "references": [
                "Earth orbits the Sun.",
                "Water boils at 100 degrees Celsius at sea level.",
            ],
        }
        generated = generate_candidates(payload)
        guardrail_payload = build_generation_payload(payload, generated)
        result = run_guardrail(guardrail_payload)

        self.assertEqual(generated["provider"], "local_demo")
        self.assertEqual(result["action"], "EMIT")
        self.assertGreaterEqual(len(result["candidates"]), 2)
        self.assertGreaterEqual(len(list_providers()), 3)

    def test_provider_catalog_includes_commercial_adapters(self):
        providers = {provider["id"]: provider for provider in list_providers()}

        self.assertIn("anthropic", providers)
        self.assertIn("ANTHROPIC_API_KEY", providers["anthropic"]["requires"])
        self.assertIn("gemini", providers)
        self.assertIn("GEMINI_API_KEY", providers["gemini"]["requires"])

    def test_anthropic_requires_api_key(self):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": ""}):
            with self.assertRaises(ProviderError):
                generate_candidates({"provider": "anthropic", "references": ["Earth orbits the Sun."]})

    def test_gemini_requires_api_key(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
            with self.assertRaises(ProviderError):
                generate_candidates({"provider": "gemini", "references": ["Earth orbits the Sun."]})

    def test_anthropic_provider_builds_messages_request(self):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "anthropic-key"}):
            with patch("providers._post_json") as post_json:
                post_json.return_value = {"content": [{"type": "text", "text": "Earth orbits the Sun."}]}
                generated = generate_candidates(
                    {
                        "provider": "anthropic",
                        "model": "claude-3-5-haiku-20241022",
                        "prompt": "Answer from references.",
                        "references": ["Earth orbits the Sun."],
                        "candidate_count": 1,
                    }
                )

        url, body = post_json.call_args.args
        headers = post_json.call_args.kwargs["headers"]

        self.assertEqual(url, "https://api.anthropic.com/v1/messages")
        self.assertEqual(body["model"], "claude-3-5-haiku-20241022")
        self.assertEqual(body["max_tokens"], 1024)
        self.assertIn("References:", body["messages"][0]["content"])
        self.assertEqual(headers["x-api-key"], "anthropic-key")
        self.assertEqual(headers["anthropic-version"], "2023-06-01")
        self.assertEqual(generated["provider"], "anthropic")
        self.assertEqual(generated["candidates"][0]["text"], "Earth orbits the Sun.")

    def test_gemini_provider_builds_generate_content_request(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "gemini-key"}):
            with patch("providers._post_json") as post_json:
                post_json.return_value = {
                    "candidates": [
                        {"content": {"parts": [{"text": "Earth orbits the Sun."}]}},
                        {"content": {"parts": [{"text": "The Sun is a star."}]}},
                    ]
                }
                generated = generate_candidates(
                    {
                        "provider": "gemini",
                        "model": "gemini-2.5-flash",
                        "prompt": "Answer from references.",
                        "references": ["Earth orbits the Sun.", "The Sun is a star."],
                        "candidate_count": 2,
                    }
                )

        url, body = post_json.call_args.args
        headers = post_json.call_args.kwargs["headers"]

        self.assertEqual(
            url,
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
        )
        self.assertEqual(body["generationConfig"]["candidateCount"], 2)
        self.assertIn("References:", body["contents"][0]["parts"][0]["text"])
        self.assertEqual(headers["x-goog-api-key"], "gemini-key")
        self.assertEqual(generated["provider"], "gemini")
        self.assertEqual(len(generated["candidates"]), 2)

    def test_cli_generate_check_writes_provider_trace(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "generate-result.json"
            audits = Path(tmp) / "audits"
            exit_code = cli_main(["generate-check", "--demo", "--out", str(out), "--evidence-dir", str(audits)])
            result = json.loads(out.read_text(encoding="utf-8"))

            self.assertEqual(exit_code, 0)
            self.assertEqual(result["provider"], "local_demo")
            self.assertIn("provider_trace", result)

    def test_openai_compatible_response_shape(self):
        payload = {
            "model": "sentinel-local-demo",
            "messages": [
                {
                    "role": "system",
                    "content": "References:\n- Earth orbits the Sun.\n- The Sun is a star.",
                },
                {"role": "user", "content": "Answer from references."},
            ],
            "sentinel": {
                "provider": "local_demo",
                "provider_model": "sentinel-demo-v1",
                "policy_profile": "support",
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            response = run_chat_completions(payload, Path(tmp))

        self.assertEqual(response["object"], "chat.completion")
        self.assertEqual(response["choices"][0]["message"]["role"], "assistant")
        self.assertIn(response["choices"][0]["finish_reason"], {"stop", "content_filter"})
        self.assertIn("sentinel", response)
        self.assertIn("evidence", response["sentinel"])

    def test_openai_compatible_stream_chunks_include_sentinel_metadata(self):
        payload = {
            "model": "sentinel-local-demo",
            "stream": True,
            "messages": [
                {
                    "role": "system",
                    "content": "References:\n- Earth orbits the Sun.\n- The Sun is a star.",
                },
                {"role": "user", "content": "Answer from references."},
            ],
            "sentinel": {
                "provider": "local_demo",
                "provider_model": "sentinel-demo-v1",
                "policy_profile": "support",
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            chunks = run_chat_completions_stream(payload, Path(tmp))

        self.assertGreaterEqual(len(chunks), 3)
        self.assertEqual(chunks[-1], "data: [DONE]\n\n")
        first = json.loads(chunks[0].removeprefix("data: "))
        final = json.loads(chunks[-2].removeprefix("data: "))

        self.assertEqual(first["object"], "chat.completion.chunk")
        self.assertEqual(first["choices"][0]["delta"], {"role": "assistant"})
        self.assertIn(final["choices"][0]["finish_reason"], {"stop", "content_filter"})
        self.assertIn("sentinel", final)
        self.assertIn("evidence", final["sentinel"])

    def test_cli_chat_completions_writes_openai_response(self):
        payload = {
            "model": "sentinel-local-demo",
            "messages": [
                {"role": "system", "content": "References:\n- Earth orbits the Sun."},
                {"role": "user", "content": "Answer from references."},
            ],
            "sentinel": {"provider": "local_demo"},
        }
        with tempfile.TemporaryDirectory() as tmp:
            request_path = Path(tmp) / "request.json"
            out = Path(tmp) / "response.json"
            request_path.write_text(json.dumps(payload), encoding="utf-8")
            exit_code = cli_main(["chat-completions", "--input", str(request_path), "--out", str(out)])
            response = json.loads(out.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0)
        self.assertEqual(response["object"], "chat.completion")

    def test_cli_chat_completions_writes_stream_response(self):
        payload = {
            "model": "sentinel-local-demo",
            "stream": True,
            "messages": [
                {"role": "system", "content": "References:\n- Earth orbits the Sun."},
                {"role": "user", "content": "Answer from references."},
            ],
            "sentinel": {"provider": "local_demo"},
        }
        with tempfile.TemporaryDirectory() as tmp:
            request_path = Path(tmp) / "request.json"
            out = Path(tmp) / "response.sse"
            request_path.write_text(json.dumps(payload), encoding="utf-8")
            exit_code = cli_main(["chat-completions", "--input", str(request_path), "--out", str(out)])
            response = out.read_text(encoding="utf-8")

        self.assertEqual(exit_code, 0)
        self.assertIn("data: {", response)
        self.assertTrue(response.endswith("data: [DONE]\n\n"))

    def test_regression_suite_passes_and_writes_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = run_suite(DEMO_SUITE, Path(tmp))

        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["summary"]["case_count"], 5)
        self.assertEqual(report["summary"]["failed"], 0)
        self.assertTrue(all(case["evidence"] for case in report["cases"]))

    def test_regression_suite_reports_expectation_failure(self):
        suite = {
            "name": "Failing expectation",
            "cases": [
                {
                    "id": "wrong-expectation",
                    "references": ["Earth orbits the Sun."],
                    "candidates": [{"id": "safe", "label": "Safe", "text": "Earth orbits the Sun."}],
                    "expect": {"action": "BLOCK"},
                }
            ],
        }
        report = run_suite(suite, save_evidence=False)

        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["summary"]["failed"], 1)
        self.assertIn("expected_action:BLOCK:got:EMIT", report["cases"][0]["errors"])

    def test_empty_regression_suite_fails_closed(self):
        report = run_suite({"name": "Empty suite"}, save_evidence=False)

        self.assertEqual(report["status"], "FAIL")
        self.assertIn("suite_has_no_cases", report["errors"])

    def test_cli_suite_fail_on_fail_exits_two(self):
        suite = {
            "name": "Failing CLI expectation",
            "cases": [
                {
                    "references": ["The capital of France is Paris."],
                    "candidates": [{"id": "safe", "label": "Safe", "text": "The capital of France is Paris."}],
                    "expect": {"action": "BLOCK"},
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            request_path = Path(tmp) / "suite.json"
            request_path.write_text(json.dumps(suite), encoding="utf-8")
            with patch("sys.stdout", new_callable=io.StringIO):
                exit_code = cli_main(["suite", "--input", str(request_path), "--fail-on-fail"])

        self.assertEqual(exit_code, 2)


if __name__ == "__main__":
    unittest.main()
