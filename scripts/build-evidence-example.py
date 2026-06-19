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
        "--config",
        type=Path,
        help="JSON config listing evidence examples to build.",
    )
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
    parser.add_argument(
        "--case-id",
        action="append",
        default=[],
        help="Suite case ID to include. Repeat to build a focused example from a larger suite.",
    )
    args = parser.parse_args(argv)

    if args.config:
        config_path = _resolve_repo_path(args.config)
        config = json.loads(config_path.read_text(encoding="utf-8"))
        examples = _load_config_examples(config)
        for example in examples:
            _build_example(
                suite_path=_resolve_repo_path(Path(example["suite"])),
                out_dir=_resolve_repo_path(Path(example["out_dir"])),
                case_ids=[str(case_id) for case_id in example.get("case_ids", [])],
            )
        return 0

    _build_example(
        suite_path=_resolve_repo_path(args.suite),
        out_dir=_resolve_repo_path(args.out_dir),
        case_ids=args.case_id,
    )

    return 0


def _build_example(*, suite_path: Path, out_dir: Path, case_ids: list[str]) -> None:
    suite = json.loads(suite_path.read_text(encoding="utf-8"))
    if case_ids:
        suite = _filter_suite_cases(suite, case_ids)

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


def _load_config_examples(config: Any) -> list[dict[str, Any]]:
    if not isinstance(config, dict):
        raise SystemExit("Evidence example config must be a JSON object.")
    examples = config.get("examples")
    if not isinstance(examples, list) or not examples:
        raise SystemExit("Evidence example config must include a non-empty examples array.")
    for index, example in enumerate(examples, start=1):
        if not isinstance(example, dict):
            raise SystemExit(f"Config example {index} must be an object.")
        if not example.get("suite") or not example.get("out_dir"):
            raise SystemExit(f"Config example {index} must include suite and out_dir.")
        case_ids = example.get("case_ids", [])
        if case_ids and not isinstance(case_ids, list):
            raise SystemExit(f"Config example {index} case_ids must be an array when provided.")
    return examples


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


def _filter_suite_cases(suite: dict[str, Any], case_ids: list[str]) -> dict[str, Any]:
    requested = set(case_ids)
    cases = suite.get("cases") if isinstance(suite.get("cases"), list) else []
    filtered_cases = [
        case
        for case in cases
        if isinstance(case, dict) and str(case.get("id")) in requested
    ]
    found = {str(case.get("id")) for case in filtered_cases}
    missing = [case_id for case_id in case_ids if case_id not in found]
    if missing:
        raise SystemExit(f"Suite is missing requested case IDs: {', '.join(missing)}")
    filtered = dict(suite)
    filtered["cases"] = filtered_cases
    filtered["name"] = f"{suite.get('name', 'Sentinel suite')} evidence example"
    filtered["description"] = (
        f"Focused public evidence example built from case IDs: {', '.join(case_ids)}."
    )
    return filtered


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
