"""Validate Sentinel suite JSON files before running them in CI."""

from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from policies import list_policy_templates  # noqa: E402
from suites import run_suite  # noqa: E402


VALID_ACTIONS = {"EMIT", "BLOCK"}
VALID_POLICY_PROFILES = {profile["id"] for profile in list_policy_templates()}


def validate_suite_payload(payload: Any, *, source: str = "<memory>") -> list[str]:
    """Return validation errors for a Sentinel suite payload."""

    errors: list[str] = []
    if not isinstance(payload, dict):
        return [f"{source}: suite must be a JSON object"]

    root_profile = payload.get("policy_profile")
    if root_profile is not None and str(root_profile) not in VALID_POLICY_PROFILES:
        errors.append(
            f"{source}: policy_profile must be one of {', '.join(sorted(VALID_POLICY_PROFILES))}"
        )

    root_references = payload.get("references")
    root_provider = payload.get("provider")
    root_prompt = payload.get("prompt")
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        errors.append(f"{source}: cases must be a non-empty list")
        return errors

    seen_case_ids: set[str] = set()
    for index, case in enumerate(cases):
        case_path = f"{source}: cases[{index}]"
        if not isinstance(case, dict):
            errors.append(f"{case_path} must be an object")
            continue

        case_id = case.get("id")
        if not _non_empty_string(case_id):
            errors.append(f"{case_path}.id must be a non-empty string")
        elif str(case_id) in seen_case_ids:
            errors.append(f"{case_path}.id duplicates another case id")
        else:
            seen_case_ids.add(str(case_id))

        case_profile = case.get("policy_profile", root_profile)
        if case_profile is not None and str(case_profile) not in VALID_POLICY_PROFILES:
            errors.append(
                f"{case_path}.policy_profile must be one of {', '.join(sorted(VALID_POLICY_PROFILES))}"
            )

        references = case.get("references", root_references)
        if not _valid_references(references):
            errors.append(f"{case_path}.references must be a non-empty string or list of strings")

        candidates = case.get("candidates")
        provider = case.get("provider", root_provider)
        prompt = case.get("prompt", root_prompt)
        has_candidates = (
            _valid_candidates(candidates, errors, case_path)
            if "candidates" in case
            else False
        )
        has_provider_path = _non_empty_string(provider) and _non_empty_string(prompt)
        if not has_candidates and not has_provider_path:
            errors.append(
                f"{case_path} must define candidates or inherit/provide both provider and prompt"
            )

        expect = case.get("expect")
        if not isinstance(expect, dict):
            errors.append(f"{case_path}.expect must be an object")
        else:
            action = expect.get("action")
            if action not in VALID_ACTIONS:
                errors.append(f"{case_path}.expect.action must be EMIT or BLOCK")

    return errors


def validate_suite_file(path: Path, *, run: bool = False) -> list[str]:
    """Load and validate one suite file."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [f"{path}: file not found"]
    except json.JSONDecodeError as exc:
        return [f"{path}: invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"]

    errors = validate_suite_payload(payload, source=_display_path(path))
    if errors or not run:
        return errors

    report = run_suite(payload, save_evidence=False)
    if report.get("status") == "PASS":
        return []

    run_errors = [f"{_display_path(path)}: suite run failed with status {report.get('status')}"]
    for case in report.get("cases", []):
        if case.get("status") != "PASS":
            joined = ", ".join(str(item) for item in case.get("errors", []))
            run_errors.append(f"{_display_path(path)}: {case.get('id')} failed: {joined}")
    return run_errors


def expand_suite_paths(patterns: list[str]) -> list[Path]:
    """Expand shell or PowerShell-style globs deterministically."""

    paths: list[Path] = []
    for pattern in patterns:
        matches = sorted(glob.glob(pattern))
        if matches:
            paths.extend(Path(match) for match in matches)
        else:
            paths.append(Path(pattern))
    return paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Sentinel suite JSON files.")
    parser.add_argument("suites", nargs="+", help="Suite JSON path or glob pattern.")
    parser.add_argument("--run", action="store_true", help="Also execute each suite without writing evidence.")
    args = parser.parse_args(argv)

    paths = expand_suite_paths(args.suites)
    failed = False
    for path in paths:
        errors = validate_suite_file(path, run=args.run)
        if errors:
            failed = True
            print(f"FAIL {_display_path(path)}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"OK {_display_path(path)}")
    return 2 if failed else 0


def _valid_references(value: Any) -> bool:
    if _non_empty_string(value):
        return True
    if not isinstance(value, list) or not value:
        return False
    return all(_non_empty_string(item) for item in value)


def _valid_candidates(value: Any, errors: list[str], case_path: str) -> bool:
    if not isinstance(value, list) or not value:
        errors.append(f"{case_path}.candidates must be a non-empty list when provided")
        return False

    seen_ids: set[str] = set()
    valid = True
    for index, candidate in enumerate(value):
        candidate_path = f"{case_path}.candidates[{index}]"
        if not isinstance(candidate, dict):
            errors.append(f"{candidate_path} must be an object")
            valid = False
            continue
        candidate_id = candidate.get("id")
        if not _non_empty_string(candidate_id):
            errors.append(f"{candidate_path}.id must be a non-empty string")
            valid = False
        elif str(candidate_id) in seen_ids:
            errors.append(f"{candidate_path}.id duplicates another candidate id")
            valid = False
        else:
            seen_ids.add(str(candidate_id))
        if not _non_empty_string(candidate.get("text")):
            errors.append(f"{candidate_path}.text must be a non-empty string")
            valid = False
    return valid


def _non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _display_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
