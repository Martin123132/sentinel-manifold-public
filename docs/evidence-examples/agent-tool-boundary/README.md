# Agent Tool Boundary Evidence Example

This public, sanitized evidence pack shows an agent release gate catching
tool-boundary drift. It is generated from `samples/agent-policy-suite.json`, not
from customer data or hosted-demo audit history.

Start here:

- [summary.md](summary.md) gives the executive verdict and audit table.
- [evidence-reader.md](evidence-reader.md) explains how to inspect the bundle.
- [manifest.json](manifest.json) is the machine-readable file index and count summary.
- [suite-report.json](suite-report.json) is the release-gate suite result.
- [evidence/](evidence/) contains the saved evidence packs.
- [verification/](verification/) contains integrity verification reports.

Expected result:

- `Verified release-gate bundle`
- `5` saved checks
- `1` emitted check
- `4` blocked checks
- `5` verified evidence packs
- `0` failed verification checks

What it proves:

- Safe read-only agent behavior emits when it stays inside supplied references.
- Drift into credential storage, email sending, CRM writes/deletes, and unapproved payment release blocks.

Regenerate this example from the repo root:

```powershell
python scripts\build-evidence-example.py --suite samples\agent-policy-suite.json --out-dir docs\evidence-examples\agent-tool-boundary --case-id agent-read-only-safe --case-id calendar-credentials-block --case-id email-draft-send-block --case-id ticket-crm-write-delete-block --case-id payment-unapproved-release-block
```

This example is reference-bound. It proves Sentinel checked supplied candidate
outputs against supplied references and preserved verifiable evidence. It does
not prove external truth, legal compliance, or future model behavior.
