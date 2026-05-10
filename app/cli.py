"""Command-line interface for Sentinel Manifold checks."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from evidence import save_evidence_pack, verify_evidence_pack
from guardrail import run_guardrail
from openai_compat import run_chat_completions, run_chat_completions_stream
from policies import apply_policy_template, list_policy_templates
from providers import build_generation_payload, generate_candidates, list_providers
from samples import DEMO_PAYLOAD, DEMO_SUITE
from suites import run_suite


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Sentinel Manifold guardrail checks.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser("check", help="Run one guardrail check from JSON.")
    check_parser.add_argument("--input", type=Path, help="JSON payload file with references and candidates.")
    check_parser.add_argument("--demo", action="store_true", help="Use the bundled demo payload.")
    check_parser.add_argument("--policy-profile", default=None, help="Policy profile id to apply.")
    check_parser.add_argument("--out", type=Path, help="Write result JSON to this path.")
    check_parser.add_argument("--evidence-dir", type=Path, default=Path("out") / "audits")
    check_parser.add_argument("--fail-on-block", action="store_true", help="Exit 2 when the action is BLOCK.")

    generate_parser = subparsers.add_parser("generate-check", help="Generate candidates, then guard them.")
    generate_parser.add_argument("--input", type=Path, help="JSON payload file with prompt and references.")
    generate_parser.add_argument("--demo", action="store_true", help="Use the bundled demo payload.")
    generate_parser.add_argument("--prompt", default=None, help="Prompt to send to the provider.")
    generate_parser.add_argument(
        "--provider",
        default=None,
        help="Provider id: local_demo, ollama, openai, anthropic, or gemini.",
    )
    generate_parser.add_argument("--model", default=None, help="Provider model name.")
    generate_parser.add_argument("--policy-profile", default=None, help="Policy profile id to apply.")
    generate_parser.add_argument("--out", type=Path, help="Write result JSON to this path.")
    generate_parser.add_argument("--evidence-dir", type=Path, default=Path("out") / "audits")
    generate_parser.add_argument("--fail-on-block", action="store_true", help="Exit 2 when the action is BLOCK.")

    proxy_parser = subparsers.add_parser("chat-completions", help="Run an OpenAI-compatible request locally.")
    proxy_parser.add_argument("--input", type=Path, required=True, help="OpenAI-compatible request JSON.")
    proxy_parser.add_argument("--out", type=Path, help="Write response JSON to this path.")
    proxy_parser.add_argument("--evidence-dir", type=Path, default=Path("out") / "audits")

    verify_parser = subparsers.add_parser("verify-evidence", help="Verify a saved evidence pack.")
    verify_parser.add_argument("--input", type=Path, required=True, help="Evidence pack JSON file.")
    verify_parser.add_argument("--strict", action="store_true", help="Exit 2 when verification fails.")

    suite_parser = subparsers.add_parser("suite", help="Run a regression suite of guardrail cases.")
    suite_parser.add_argument("--input", type=Path, help="Suite JSON with a cases array.")
    suite_parser.add_argument("--demo", action="store_true", help="Use the bundled regression suite.")
    suite_parser.add_argument("--out", type=Path, help="Write suite report JSON to this path.")
    suite_parser.add_argument("--evidence-dir", type=Path, default=Path("out") / "audits")
    suite_parser.add_argument("--fail-on-fail", action="store_true", help="Exit 2 when any suite case fails.")

    subparsers.add_parser("policies", help="List available policy profiles.")
    subparsers.add_parser("providers", help="List available generation providers.")

    args = parser.parse_args(argv)

    if args.command == "policies":
        print(json.dumps({"policies": list_policy_templates()}, indent=2))
        return 0
    if args.command == "providers":
        print(json.dumps({"providers": list_providers()}, indent=2))
        return 0
    if args.command == "chat-completions":
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        if payload.get("stream") is True:
            output = "".join(run_chat_completions_stream(payload, args.evidence_dir))
        else:
            result = run_chat_completions(payload, args.evidence_dir)
            output = json.dumps(result, indent=2)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(output, encoding="utf-8")
        else:
            print(output, end="" if payload.get("stream") is True else "\n")
        return 0
    if args.command == "verify-evidence":
        report = verify_evidence_pack(args.input)
        print(json.dumps(report, indent=2))
        if args.strict and (not report["integrity_valid"] or not report["request_hashes_valid"]):
            return 2
        return 0
    if args.command == "suite":
        payload = _load_suite_payload(args)
        report = run_suite(payload, args.evidence_dir)
        output = json.dumps(report, indent=2)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(output, encoding="utf-8")
        else:
            print(output)
        if args.fail_on_fail and report["status"] != "PASS":
            return 2
        return 0

    payload = _load_payload(args)
    if args.policy_profile:
        payload["policy_profile"] = args.policy_profile
    if getattr(args, "prompt", None):
        payload["prompt"] = args.prompt
    if getattr(args, "provider", None):
        payload["provider"] = args.provider
    if getattr(args, "model", None):
        payload["model"] = args.model
    if args.command == "generate-check":
        generated = generate_candidates(payload)
        payload = build_generation_payload(payload, generated)
    payload = apply_policy_template(payload)
    result = run_guardrail(payload)
    if payload.get("provider_trace"):
        result["provider_trace"] = payload["provider_trace"]
        result["provider"] = payload.get("provider")
        result["model"] = payload.get("model")
    evidence = save_evidence_pack(payload, result, args.evidence_dir)
    result["evidence"] = evidence

    output = json.dumps(result, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
    else:
        print(output)

    if args.fail_on_block and result["action"] == "BLOCK":
        return 2
    return 0


def _load_payload(args: argparse.Namespace) -> dict:
    if args.demo:
        return dict(DEMO_PAYLOAD)
    if not args.input:
        raise SystemExit("--input or --demo is required for check")
    return json.loads(args.input.read_text(encoding="utf-8"))


def _load_suite_payload(args: argparse.Namespace) -> dict:
    if args.demo:
        return dict(DEMO_SUITE)
    if not args.input:
        raise SystemExit("--input or --demo is required for suite")
    return json.loads(args.input.read_text(encoding="utf-8"))


if __name__ == "__main__":
    sys.exit(main())
