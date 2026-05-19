"""Build a public, sanitized Sentinel evidence example from a suite."""

from __future__ import annotations

import argparse
import io
import json
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "app"
sys.path.insert(0, str(APP_DIR))

from evidence import build_evidence_bundle  # noqa: E402
from suites import run_suite  # noqa: E402


GENERATED_FILES = ("summary.md", "evidence-reader.md", "manifest.json", "suite-report.json")
GENERATED_DIRS = ("evidence", "verification")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a sanitized public evidence example.")
    parser.add_argument(
        "--suite",
        type=Path,
        default=Path("examples") / "external-adoption" / "support-assistant" / "sentinel-suite.json",
        help="Suite JSON file to run.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("docs") / "evidence-examples" / "support-assistant",
        help="Directory that will receive generated evidence example files.",
    )
    args = parser.parse_args(argv)

    suite_path = _resolve_repo_path(args.suite)
    out_dir = _resolve_repo_path(args.out_dir)
    suite = json.loads(suite_path.read_text(encoding="utf-8"))

    with tempfile.TemporaryDirectory() as tmp:
        evidence_dir = Path(tmp) / "audits"
        report = run_suite(suite, evidence_dir)
        if report["status"] != "PASS":
            raise SystemExit(f"Suite must pass before publishing evidence example: {report['status']}")

        _sanitize_report_paths(report)
        _reset_generated_files(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "suite-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

        bundle = build_evidence_bundle(evidence_dir, limit=int(report["summary"]["case_count"]))
        _extract_sanitized_bundle(bundle, out_dir)

    return 0


def _resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def _reset_generated_files(out_dir: Path) -> None:
    for rel_path in GENERATED_FILES:
        path = out_dir / rel_path
        if path.exists():
            path.unlink()
    for rel_path in GENERATED_DIRS:
        path = out_dir / rel_path
        if path.exists():
            shutil.rmtree(path)


def _sanitize_report_paths(report: dict[str, Any]) -> None:
    for case in report.get("cases", []):
        if not isinstance(case, dict):
            continue
        evidence = case.get("evidence")
        check_id = case.get("check_id")
        if isinstance(evidence, dict) and check_id:
            evidence["path"] = f"evidence/{check_id}.evidence.json"


def _extract_sanitized_bundle(bundle: bytes, out_dir: Path) -> None:
    with zipfile.ZipFile(io.BytesIO(bundle)) as archive:
        for item in archive.infolist():
            if item.is_dir():
                continue
            rel_path = Path(item.filename)
            target = out_dir / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            raw = archive.read(item.filename)
            if item.filename.endswith(".json"):
                body = json.loads(raw.decode("utf-8"))
                if item.filename.startswith("verification/"):
                    _sanitize_verification_path(body)
                target.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
            else:
                target.write_text(raw.decode("utf-8").rstrip() + "\n", encoding="utf-8")


def _sanitize_verification_path(body: dict[str, Any]) -> None:
    check_id = body.get("check_id")
    if check_id:
        body["path"] = f"evidence/{check_id}.evidence.json"


if __name__ == "__main__":
    raise SystemExit(main())
