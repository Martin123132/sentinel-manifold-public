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
        archive.writestr("manifest.json", json.dumps(manifest, indent=2))
    return buffer.getvalue()


def _evidence_files(evidence_dir: Path, limit: int) -> list[Path]:
    if not evidence_dir.exists():
        return []
    safe_limit = max(0, int(limit))
    return sorted(evidence_dir.glob("*.evidence.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:safe_limit]
