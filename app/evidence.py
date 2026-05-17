"""Evidence pack persistence for Sentinel Manifold checks."""

from __future__ import annotations

import hashlib
import io
import json
import time
import zipfile
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "sentinel.evidence.v1"
BUNDLE_SCHEMA_VERSION = "sentinel.evidence.bundle.v1"
RUNTIME_VERIFICATION_KEYS = {"integrity", "integrity_valid", "verification"}


def canonical_json(value: Any) -> str:
    """Stable JSON representation for content hashes."""

    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_json(value: Any) -> str:
    return sha256_text(canonical_json(value))


def build_evidence_pack(payload: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    """Build a tamper-evident audit artifact for a guardrail check."""

    request = {
        "mode": payload.get("mode"),
        "policy_profile": payload.get("policy_profile"),
        "policy_name": payload.get("policy_name"),
        "policy": payload.get("policy", {}),
        "provider": payload.get("provider"),
        "model": payload.get("model"),
        "prompt": payload.get("prompt"),
        "provider_trace": payload.get("provider_trace"),
        "compat_request": payload.get("compat_request"),
        "references": payload.get("references", []),
        "candidates": payload.get("candidates", []),
    }
    body = {
        "schema_version": SCHEMA_VERSION,
        "check_id": result["check_id"],
        "created_at": result["created_at"],
        "saved_at": int(time.time()),
        "gateway_action": result["action"],
        "request": request,
        "request_hashes": {
            "references_sha256": sha256_json(request["references"]),
            "candidates_sha256": sha256_json(request["candidates"]),
            "policy_sha256": sha256_json(request["policy"]),
        },
        "result": result,
    }
    body["integrity"] = {
        "algorithm": "sha256-canonical-json",
        "digest": sha256_json(body),
    }
    return body


def save_evidence_pack(
    payload: dict[str, Any],
    result: dict[str, Any],
    evidence_dir: Path,
) -> dict[str, Any]:
    """Persist an evidence pack and return public metadata."""

    evidence_dir.mkdir(parents=True, exist_ok=True)
    pack = build_evidence_pack(payload, result)
    file_path = evidence_dir / f"{result['check_id']}.evidence.json"
    file_path.write_text(json.dumps(pack, indent=2), encoding="utf-8")
    return {
        "schema_version": SCHEMA_VERSION,
        "path": str(file_path),
        "digest": pack["integrity"]["digest"],
        "algorithm": pack["integrity"]["algorithm"],
    }


def verify_evidence_pack(file_path: Path) -> dict[str, Any]:
    """Return a verification report for a saved evidence pack."""

    pack = json.loads(file_path.read_text(encoding="utf-8"))
    supplied_integrity = pack.get("integrity", {})
    supplied_digest = supplied_integrity.get("digest")
    body = {key: value for key, value in pack.items() if key not in RUNTIME_VERIFICATION_KEYS}
    recomputed_digest = sha256_json(body)
    request = pack.get("request", {})
    supplied_hashes = pack.get("request_hashes", {})
    recomputed_hashes = {
        "references_sha256": sha256_json(request.get("references", [])),
        "candidates_sha256": sha256_json(request.get("candidates", [])),
        "policy_sha256": sha256_json(request.get("policy", {})),
    }
    request_hashes = {
        key: {
            "supplied": supplied_hashes.get(key),
            "recomputed": recomputed,
            "valid": supplied_hashes.get(key) == recomputed,
        }
        for key, recomputed in recomputed_hashes.items()
    }
    errors = []
    if pack.get("schema_version") != SCHEMA_VERSION:
        errors.append("unsupported_schema_version")
    if not supplied_digest:
        errors.append("missing_integrity_digest")
    if supplied_integrity.get("algorithm") != "sha256-canonical-json":
        errors.append("unsupported_integrity_algorithm")
    if supplied_digest != recomputed_digest:
        errors.append("integrity_digest_mismatch")
    if not all(item["valid"] for item in request_hashes.values()):
        errors.append("request_hash_mismatch")

    return {
        "path": str(file_path),
        "schema_version": pack.get("schema_version"),
        "check_id": pack.get("check_id"),
        "algorithm": supplied_integrity.get("algorithm"),
        "integrity_valid": supplied_digest == recomputed_digest,
        "supplied_digest": supplied_digest,
        "recomputed_digest": recomputed_digest,
        "request_hashes_valid": all(item["valid"] for item in request_hashes.values()),
        "request_hashes": request_hashes,
        "errors": errors,
    }


def load_evidence_pack(file_path: Path) -> dict[str, Any]:
    """Load and verify an evidence pack from disk."""

    pack = json.loads(file_path.read_text(encoding="utf-8"))
    verification = verify_evidence_pack(file_path)
    pack["integrity_valid"] = verification["integrity_valid"]
    pack["verification"] = verification
    return pack


def list_evidence_packs(evidence_dir: Path, limit: int = 25) -> list[dict[str, Any]]:
    """Return compact evidence-pack rows for the dashboard."""

    rows: list[dict[str, Any]] = []
    for file_path in _evidence_files(evidence_dir, limit):
        try:
            pack = load_evidence_pack(file_path)
        except (OSError, json.JSONDecodeError):
            continue
        result = pack.get("result", {})
        summary = result.get("summary", {})
        rows.append(
            {
                "check_id": pack.get("check_id"),
                "created_at": pack.get("created_at"),
                "path": str(file_path),
                "digest": pack.get("integrity", {}).get("digest"),
                "integrity_valid": pack.get("integrity_valid", False),
                "action": result.get("action"),
                "emitted": result.get("emitted_candidate_id") or "none",
                "risk": summary.get("highest_risk_score"),
                "blocked": summary.get("blocked_count"),
                "policy_profile": pack.get("request", {}).get("policy_profile"),
            }
        )
    return rows


def build_evidence_bundle(evidence_dir: Path, limit: int = 25) -> bytes:
    """Return a zip archive containing evidence packs, verification reports, and a manifest."""

    manifest: dict[str, Any] = {
        "schema_version": BUNDLE_SCHEMA_VERSION,
        "created_at": int(time.time()),
        "limit": limit,
        "count": 0,
        "summary_path": "summary.md",
        "reader_path": "evidence-reader.md",
        "verdict": "No evidence exported",
        "generated_files": ["summary.md", "evidence-reader.md", "manifest.json"],
        "summary": _bundle_counts([]),
        "audits": [],
    }
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in _evidence_files(evidence_dir, limit):
            try:
                raw_pack = json.loads(file_path.read_text(encoding="utf-8"))
                verification = verify_evidence_pack(file_path)
            except (OSError, json.JSONDecodeError):
                continue

            check_id = str(raw_pack.get("check_id") or file_path.stem.removesuffix(".evidence"))
            evidence_name = f"evidence/{check_id}.evidence.json"
            verification_name = f"verification/{check_id}.verification.json"
            result = raw_pack.get("result", {})
            summary = result.get("summary", {})

            archive.writestr(evidence_name, json.dumps(raw_pack, indent=2))
            archive.writestr(verification_name, json.dumps(verification, indent=2))
            manifest["audits"].append(
                {
                    "check_id": check_id,
                    "created_at": raw_pack.get("created_at"),
                    "action": result.get("action"),
                    "emitted": result.get("emitted_candidate_id") or "none",
                    "risk": summary.get("highest_risk_score"),
                    "blocked": summary.get("blocked_count"),
                    "policy_profile": raw_pack.get("request", {}).get("policy_profile"),
                    "digest": raw_pack.get("integrity", {}).get("digest"),
                    "integrity_valid": verification.get("integrity_valid", False),
                    "evidence_path": evidence_name,
                    "verification_path": verification_name,
                }
            )
        manifest["count"] = len(manifest["audits"])
        manifest["summary"] = _bundle_counts(manifest["audits"])
        manifest["verdict"] = _bundle_verdict(manifest["summary"])
        manifest["generated_files"] = _bundle_generated_files(manifest)
        archive.writestr("summary.md", _bundle_summary_markdown(manifest))
        archive.writestr("evidence-reader.md", _bundle_reader_markdown(manifest))
        archive.writestr("manifest.json", json.dumps(manifest, indent=2))
    return buffer.getvalue()


def _bundle_counts(audits: list[dict[str, Any]]) -> dict[str, Any]:
    timestamps = [audit.get("created_at") for audit in audits if isinstance(audit.get("created_at"), int)]
    policy_profiles = sorted(
        {
            str(audit.get("policy_profile"))
            for audit in audits
            if audit.get("policy_profile")
        }
    )
    return {
        "total_audits": len(audits),
        "emitted": sum(1 for audit in audits if audit.get("action") == "EMIT"),
        "blocked": sum(1 for audit in audits if audit.get("action") == "BLOCK"),
        "verified": sum(1 for audit in audits if audit.get("integrity_valid") is True),
        "failed_verification": sum(1 for audit in audits if audit.get("integrity_valid") is not True),
        "policy_profiles": policy_profiles,
        "newest_created_at": max(timestamps) if timestamps else None,
        "oldest_created_at": min(timestamps) if timestamps else None,
    }


def _bundle_verdict(summary: dict[str, Any]) -> str:
    total = int(summary.get("total_audits") or 0)
    failed_verification = int(summary.get("failed_verification") or 0)
    if total == 0:
        return "No evidence exported"
    if failed_verification > 0:
        return "Needs review"
    return "Verified release-gate bundle"


def _bundle_generated_files(manifest: dict[str, Any]) -> list[str]:
    files = ["summary.md", "evidence-reader.md", "manifest.json"]
    for audit in manifest.get("audits", []):
        evidence_path = audit.get("evidence_path")
        verification_path = audit.get("verification_path")
        if evidence_path:
            files.append(str(evidence_path))
        if verification_path:
            files.append(str(verification_path))
    return files


def _bundle_summary_markdown(manifest: dict[str, Any]) -> str:
    summary = manifest.get("summary", {})
    policy_profiles = summary.get("policy_profiles") or []
    policy_text = ", ".join(policy_profiles) if policy_profiles else "none recorded"
    verdict = manifest.get("verdict") or _bundle_verdict(summary)
    lines = [
        "# Sentinel Evidence Bundle",
        "",
        f"Executive verdict: **{verdict}**",
        "",
        "Human-readable release-gate summary for the exported evidence packs.",
        "",
        "## Proof Snapshot",
        "",
        "| Total audits | Emitted | Blocked | Verified | Failed verification | Newest check | Oldest check |",
        "| --- | --- | --- | --- | --- | --- | --- |",
        "| "
        f"{_md_cell(summary.get('total_audits', 0))} | "
        f"{_md_cell(summary.get('emitted', 0))} | "
        f"{_md_cell(summary.get('blocked', 0))} | "
        f"{_md_cell(summary.get('verified', 0))} | "
        f"{_md_cell(summary.get('failed_verification', 0))} | "
        f"{_md_cell(_format_timestamp(summary.get('newest_created_at')))} | "
        f"{_md_cell(_format_timestamp(summary.get('oldest_created_at')))} |",
        "",
        "## Bundle Summary",
        "",
        f"- Created: {_format_timestamp(manifest.get('created_at'))}",
        f"- Export limit: {manifest.get('limit')}",
        f"- Total audits: {summary.get('total_audits', 0)}",
        f"- Emitted: {summary.get('emitted', 0)}",
        f"- Blocked: {summary.get('blocked', 0)}",
        f"- Integrity verified: {summary.get('verified', 0)}",
        f"- Failed verification: {summary.get('failed_verification', 0)}",
        f"- Policy profiles: {policy_text}",
        f"- Newest check: {_format_timestamp(summary.get('newest_created_at'))}",
        f"- Oldest check: {_format_timestamp(summary.get('oldest_created_at'))}",
        "",
        "## What This Proves",
        "",
        "- Sentinel evaluated saved AI outputs against the supplied reference material and policy profile.",
        "- The bundle records which checks emitted an answer and which checks blocked unsafe candidates.",
        "- Each evidence pack has a canonical SHA-256 integrity check and request-hash verification report.",
        "",
        "## What This Does Not Prove",
        "",
        "- It does not prove external truth beyond the references supplied to Sentinel.",
        "- It does not certify a whole organization, deployment, model provider, or future AI behavior.",
        "- It does not make private customer evidence safe to share publicly.",
        "",
    ]
    audits = manifest.get("audits", [])
    if not audits:
        lines.extend(
            [
                "## Audit Rows",
                "",
                "No saved evidence packs were available for this export.",
                "",
            ]
        )
        return "\n".join(lines)

    lines.extend(
        [
            "## Audit Rows",
            "",
            "| Check | Action | Policy | Risk | Blocked | Integrity |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for audit in audits:
        integrity = "verified" if audit.get("integrity_valid") else "failed"
        lines.append(
            "| "
            f"{_md_cell(audit.get('check_id'))} | "
            f"{_md_cell(audit.get('action'))} | "
            f"{_md_cell(audit.get('policy_profile') or 'default')} | "
            f"{_md_cell(audit.get('risk'))} | "
            f"{_md_cell(audit.get('blocked'))} | "
            f"{integrity} |"
        )
    lines.append("")
    return "\n".join(lines)


def _bundle_reader_markdown(manifest: dict[str, Any]) -> str:
    summary = manifest.get("summary", {})
    audits = manifest.get("audits", [])
    policy_profiles = summary.get("policy_profiles") or []
    policy_text = ", ".join(policy_profiles) if policy_profiles else "none recorded"
    verdict = manifest.get("verdict") or _bundle_verdict(summary)
    files = manifest.get("generated_files") or []
    lines = [
        "# Sentinel Evidence Reader",
        "",
        "This file is the plain-English guide to the exported Sentinel proof bundle.",
        "",
        "## Quick Verdict",
        "",
        f"- Verdict: **{verdict}**",
        f"- Total saved checks: {summary.get('total_audits', 0)}",
        f"- Emitted checks: {summary.get('emitted', 0)}",
        f"- Blocked checks: {summary.get('blocked', 0)}",
        f"- Integrity verified: {summary.get('verified', 0)}",
        f"- Failed verification: {summary.get('failed_verification', 0)}",
        f"- Policy profiles: {policy_text}",
        "",
        "## How To Read The Bundle",
        "",
        "1. Start with `summary.md` for the release-gate result and audit table.",
        "2. Open `manifest.json` for the machine-readable index and count summary.",
        "3. Inspect `evidence/<check_id>.evidence.json` for the original request, candidates, findings, and decision.",
        "4. Inspect `verification/<check_id>.verification.json` to confirm the integrity digest and request hashes.",
        "",
        "## What Happened",
        "",
    ]
    if audits:
        lines.extend(
            [
                "Sentinel exported saved checks from the audit directory. Each check records whether the gateway emitted a supported candidate or blocked all candidates that drifted from the supplied references.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "No evidence was exported. The zip is still valid, but it only proves that the export path works and that no saved audit packs were available for this export.",
                "",
            ]
        )

    lines.extend(
        [
            "## Reference-Bound Boundary",
            "",
            "Sentinel does not claim external truth. It proves that saved outputs were checked against the references, candidates, and policy settings included in the evidence packs.",
            "",
            "## Files Included",
            "",
        ]
    )
    if files:
        lines.extend(f"- `{_md_cell(path)}`" for path in files)
    else:
        lines.append("- No files were listed in the manifest.")
    lines.append("")
    return "\n".join(lines)


def _format_timestamp(value: object) -> str:
    if not isinstance(value, int):
        return "not available"
    return time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(value))


def _md_cell(value: object) -> str:
    return str(value if value is not None else "not recorded").replace("|", "\\|")


def _evidence_files(evidence_dir: Path, limit: int) -> list[Path]:
    if not evidence_dir.exists():
        return []
    safe_limit = max(0, int(limit))
    return sorted(evidence_dir.glob("*.evidence.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:safe_limit]
