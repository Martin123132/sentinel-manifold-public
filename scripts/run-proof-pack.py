#!/usr/bin/env python3
"""Run Sentinel's public proof-pack suites with a concise PASS table."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


DEFAULT_SUITES = [
    {
        "name": "Regression",
        "input": "samples/regression-suite.json",
        "output": "suite-report.json",
    },
    {
        "name": "Customer-shaped",
        "input": "samples/customer-shaped-regression-suite.json",
        "output": "customer-shaped-regression-suite-report.json",
    },
    {
        "name": "Policy calibration",
        "input": "samples/policy-calibration-suite.json",
        "output": "policy-calibration-suite-report.json",
    },
    {
        "name": "Integration starter",
        "input": "samples/integration-starter-suite.json",
        "output": "integration-starter-suite-report.json",
    },
    {
        "name": "Mixed proof",
        "input": "samples/mixed-proof-suite.json",
        "output": "mixed-proof-suite-report.json",
    },
]


FULL_SUITES = [
    {
        "name": "Agent policy",
        "input": "samples/agent-policy-suite.json",
        "output": "agent-policy-suite-report.json",
    },
    {
        "name": "Buyer policy depth",
        "input": "samples/buyer-policy-depth-suite.json",
        "output": "buyer-policy-depth-suite-report.json",
    },
    {
        "name": "Policy tuning",
        "input": "samples/policy-tuning-suite.json",
        "output": "policy-tuning-suite-report.json",
    },
    {
        "name": "External adoption",
        "input": "examples/external-adoption/support-assistant/sentinel-suite.json",
        "output": "external-adoption-suite-report.json",
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Sentinel proof-pack suites and print a short PASS table."
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run the extended local proof pack as well as the default trial pack.",
    )
    parser.add_argument(
        "--out-dir",
        default="out",
        help="Directory for suite reports. Defaults to out.",
    )
    parser.add_argument(
        "--python",
        default=sys.executable,
        help="Python executable used to run app/cli.py. Defaults to this interpreter.",
    )
    return parser.parse_args()


def resolve_out_dir(repo_root: Path, out_dir: str) -> Path:
    path = Path(out_dir)
    if not path.is_absolute():
        path = repo_root / path
    path.mkdir(parents=True, exist_ok=True)
    return path


def run_suite(repo_root: Path, out_dir: Path, python_cmd: str, suite: dict[str, str]) -> dict[str, object]:
    input_path = repo_root / suite["input"]
    output_path = out_dir / suite["output"]
    print(f"Running {suite['name']}...")

    command = [
        python_cmd,
        str(repo_root / "app" / "cli.py"),
        "suite",
        "--input",
        str(input_path),
        "--out",
        str(output_path),
        "--fail-on-fail",
    ]
    completed = subprocess.run(command, cwd=repo_root)
    if completed.returncode != 0:
        raise RuntimeError(f"Suite failed: {suite['name']} ({suite['input']})")

    report = json.loads(output_path.read_text(encoding="utf-8"))
    summary = report.get("summary", {})
    return {
        "Suite": suite["name"],
        "Status": report.get("status", "UNKNOWN"),
        "Cases": summary.get("case_count", 0),
        "Passed": summary.get("passed", 0),
        "Failed": summary.get("failed", 0),
        "Report": str(output_path.relative_to(repo_root)),
    }


def print_table(rows: list[dict[str, object]]) -> None:
    columns = ["Suite", "Status", "Cases", "Passed", "Failed", "Report"]
    widths = {
        column: max(len(column), *(len(str(row[column])) for row in rows))
        for column in columns
    }

    print()
    print("  ".join(column.ljust(widths[column]) for column in columns))
    print("  ".join("-" * widths[column] for column in columns))
    for row in rows:
        print("  ".join(str(row[column]).ljust(widths[column]) for column in columns))


def display_path(path: Path, repo_root: Path) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    out_dir = resolve_out_dir(repo_root, args.out_dir)
    suites = DEFAULT_SUITES + (FULL_SUITES if args.full else [])

    try:
        rows = [run_suite(repo_root, out_dir, args.python, suite) for suite in suites]
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print_table(rows)
    print("All Sentinel proof suites passed.")
    print(f"Reports are in {display_path(out_dir, repo_root)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
