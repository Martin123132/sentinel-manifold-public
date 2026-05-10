"""Regression-suite runner for Sentinel Manifold guardrail checks."""

from __future__ import annotations

import time
from copy import deepcopy
from pathlib import Path
from typing import Any

from evidence import save_evidence_pack, sha256_json
from guardrail import run_guardrail
from policies import apply_policy_template
from providers import build_generation_payload, generate_candidates


def run_suite(
    payload: dict[str, Any],
    evidence_dir: Path | None = None,
    *,
    save_evidence: bool = True,
) -> dict[str, Any]:
    """Run a batch of guardrail cases and return a release-gate report."""

    started_at = time.time()
    cases = payload.get("cases") if isinstance(payload.get("cases"), list) else []
    suite_errors = [] if cases else ["suite_has_no_cases"]
    case_results = [
        _run_case(payload, case, index, evidence_dir=evidence_dir, save_evidence=save_evidence)
        for index, case in enumerate(cases)
    ]
    passed = sum(1 for item in case_results if item["passed"])
    failed = len(case_results) - passed
    emit_count = sum(1 for item in case_results if item.get("action") == "EMIT")
    block_count = sum(1 for item in case_results if item.get("action") == "BLOCK")

    return {
        "suite_id": _suite_id(payload),
        "name": str(payload.get("name") or "Sentinel regression suite"),
        "description": str(payload.get("description") or ""),
        "created_at": int(started_at),
        "duration_ms": int((time.time() - started_at) * 1000),
        "status": "PASS" if failed == 0 and not suite_errors else "FAIL",
        "errors": suite_errors,
        "summary": {
            "case_count": len(case_results),
            "passed": passed,
            "failed": failed,
            "emit_count": emit_count,
            "block_count": block_count,
        },
        "cases": case_results,
    }


def _run_case(
    suite_payload: dict[str, Any],
    case: Any,
    index: int,
    *,
    evidence_dir: Path | None,
    save_evidence: bool,
) -> dict[str, Any]:
    if not isinstance(case, dict):
        return _error_case(index, "invalid_case", "Suite case must be an object.")

    case_id = str(case.get("id") or f"case-{index + 1}")
    name = str(case.get("name") or case_id)
    try:
        guardrail_payload = _case_payload(suite_payload, case)
        if not guardrail_payload.get("candidates"):
            generated = generate_candidates(guardrail_payload)
            guardrail_payload = build_generation_payload(guardrail_payload, generated)
        guardrail_payload = apply_policy_template(guardrail_payload)
        result = run_guardrail(guardrail_payload)
        if guardrail_payload.get("provider_trace"):
            result["provider_trace"] = guardrail_payload["provider_trace"]
            result["provider"] = guardrail_payload.get("provider")
            result["model"] = guardrail_payload.get("model")
        if save_evidence and evidence_dir is not None:
            result["evidence"] = save_evidence_pack(guardrail_payload, result, evidence_dir)

        errors = _expectation_errors(result, _expectations(case))
        summary = result.get("summary", {})
        return {
            "id": case_id,
            "name": name,
            "passed": not errors,
            "status": "PASS" if not errors else "FAIL",
            "errors": errors,
            "check_id": result.get("check_id"),
            "action": result.get("action"),
            "emitted_candidate_id": result.get("emitted_candidate_id"),
            "highest_risk_score": summary.get("highest_risk_score"),
            "blocked_count": summary.get("blocked_count"),
            "candidate_count": summary.get("candidate_count"),
            "policy_profile": guardrail_payload.get("policy_profile"),
            "evidence": result.get("evidence"),
        }
    except Exception as exc:  # pragma: no cover - defensive suite isolation
        return _error_case(index, case_id, str(exc), name=name)


def _case_payload(suite_payload: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "mode": suite_payload.get("mode"),
        "policy_profile": suite_payload.get("policy_profile"),
        "policy": deepcopy(suite_payload.get("policy", {})),
        "provider": suite_payload.get("provider"),
        "model": suite_payload.get("model"),
        "prompt": suite_payload.get("prompt"),
        "references": suite_payload.get("references", []),
        "candidate_count": suite_payload.get("candidate_count"),
    }
    for key in (
        "mode",
        "policy_profile",
        "policy",
        "provider",
        "model",
        "prompt",
        "references",
        "candidate_count",
        "candidates",
    ):
        if key in case:
            payload[key] = deepcopy(case[key])
    return {key: value for key, value in payload.items() if value is not None}


def _expectations(case: dict[str, Any]) -> dict[str, Any]:
    expect = case.get("expect") if isinstance(case.get("expect"), dict) else {}
    legacy = {
        "action": case.get("expected_action"),
        "emitted_candidate_id": case.get("expected_emitted_candidate_id"),
    }
    return {key: value for key, value in {**legacy, **expect}.items() if value is not None}


def _expectation_errors(result: dict[str, Any], expect: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    summary = result.get("summary", {})
    expected_action = expect.get("action")
    if expected_action and result.get("action") != expected_action:
        errors.append(f"expected_action:{expected_action}:got:{result.get('action')}")

    expected_emitted = expect.get("emitted_candidate_id")
    if expected_emitted and result.get("emitted_candidate_id") != expected_emitted:
        errors.append(f"expected_emitted:{expected_emitted}:got:{result.get('emitted_candidate_id')}")

    if "blocked_count" in expect and summary.get("blocked_count") != expect["blocked_count"]:
        errors.append(f"expected_blocked_count:{expect['blocked_count']}:got:{summary.get('blocked_count')}")

    if "min_blocked_count" in expect and summary.get("blocked_count", 0) < int(expect["min_blocked_count"]):
        errors.append(f"expected_min_blocked_count:{expect['min_blocked_count']}:got:{summary.get('blocked_count')}")

    if "max_highest_risk_score" in expect:
        actual = summary.get("highest_risk_score")
        if actual is not None and actual > int(expect["max_highest_risk_score"]):
            errors.append(f"expected_max_risk:{expect['max_highest_risk_score']}:got:{actual}")

    if "candidate_count" in expect and summary.get("candidate_count") != expect["candidate_count"]:
        errors.append(f"expected_candidate_count:{expect['candidate_count']}:got:{summary.get('candidate_count')}")

    return errors


def _error_case(index: int, case_id: str, message: str, *, name: str | None = None) -> dict[str, Any]:
    return {
        "id": case_id,
        "name": name or case_id or f"case-{index + 1}",
        "passed": False,
        "status": "ERROR",
        "errors": [message],
        "check_id": None,
        "action": None,
        "emitted_candidate_id": None,
        "highest_risk_score": None,
        "blocked_count": None,
        "candidate_count": None,
        "policy_profile": None,
        "evidence": None,
    }


def _suite_id(payload: dict[str, Any]) -> str:
    stable = {
        "name": payload.get("name"),
        "description": payload.get("description"),
        "cases": payload.get("cases", []),
    }
    return f"sms-{sha256_json(stable)[:10]}"
