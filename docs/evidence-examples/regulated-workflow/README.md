# Regulated Workflow Evidence Example

This public, sanitized evidence pack shows a regulated release gate catching
approval and threshold drift. It is generated from `samples/buyer-policy-depth-suite.json`,
not from customer data or hosted-demo audit history.

Start here:

- [summary.md](summary.md) gives the executive verdict and audit table.
- [evidence-reader.md](evidence-reader.md) explains how to inspect the bundle.
- [manifest.json](manifest.json) is the machine-readable file index and count summary.
- [suite-report.json](suite-report.json) is the release-gate suite result.
- [evidence/](evidence/) contains the saved evidence packs.
- [verification/](verification/) contains integrity verification reports.

Expected result:

- `Verified release-gate bundle`
- `2` saved checks
- `1` emitted check
- `1` blocked check
- `2` verified evidence packs
- `0` failed verification checks

What it proves:

- Safe wording that preserves the `5000 GBP` review threshold and manager approval emits.
- Unsafe wording that changes the threshold to `50000 GBP` and says payments release without approval blocks.

Regenerate this example from the repo root:

```powershell
python scripts\build-evidence-example.py --suite samples\buyer-policy-depth-suite.json --out-dir docs\evidence-examples\regulated-workflow --case-id regulated-safe-approval --case-id regulated-unsafe-approval
```

This example is reference-bound. It proves Sentinel checked supplied candidate
outputs against supplied references and preserved verifiable evidence. It does
not prove external truth, legal compliance, or future model behavior.
