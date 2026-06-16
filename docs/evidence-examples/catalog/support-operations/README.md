# Support Operations Catalog Evidence

This pack is generated from
`samples/catalog/support-operations-suite.json`.

It shows a support operations release gate that:

- emits safe refund, escalation, and cancellation-credit wording,
- blocks refund threshold drift,
- blocks escalation review removal.

Expected result: `3` checks, `1` emitted, `2` blocked.

Start with `summary.md` for the readable verdict, then inspect
`evidence-reader.md`, `manifest.json`, `suite-report.json`, and the files under
`evidence/` and `verification/`.
