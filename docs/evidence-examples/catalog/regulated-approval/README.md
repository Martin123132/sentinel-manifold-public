# Regulated Approval Catalog Evidence

This pack is generated from
`samples/catalog/regulated-approval-suite.json`.

It shows a regulated workflow release gate that:

- emits safe approval, review, and data-export wording,
- blocks payment approval removal,
- blocks claims threshold drift.

Expected result: `3` checks, `1` emitted, `2` blocked.

Start with `summary.md` for the readable verdict, then inspect
`evidence-reader.md`, `manifest.json`, `suite-report.json`, and the files under
`evidence/` and `verification/`.
