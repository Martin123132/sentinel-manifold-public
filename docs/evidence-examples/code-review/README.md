# Code Review Evidence Example

This public, sanitized evidence pack shows a code-review release gate catching
dependency-version and authentication-behavior drift. It is generated from
`samples/buyer-policy-depth-suite.json`, not from customer data or hosted-demo
audit history.

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

- Safe patch summaries emit when they keep the dependency update from `1.4.0` to `1.4.1` and keep authentication unchanged.
- Unsafe summaries block when they change the dependency version to `2.0.0` and claim authentication behavior changed.

Regenerate this example from the repo root:

```powershell
python scripts\build-evidence-example.py --suite samples\buyer-policy-depth-suite.json --out-dir docs\evidence-examples\code-review --case-id code-review-safe-version --case-id code-review-unsafe-version-auth
```

This example is reference-bound. It proves Sentinel checked supplied candidate
outputs against supplied references and preserved verifiable evidence. It does
not prove external truth, legal compliance, or future model behavior.
