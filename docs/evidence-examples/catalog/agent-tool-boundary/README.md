# Agent Tool-Boundary Catalog Evidence

This pack is generated from
`samples/catalog/agent-tool-boundary-suite.json`.

It shows an agent tool-boundary release gate that:

- emits safe read, draft, approval, and read-only CRM wording,
- blocks reminder sending without approval,
- blocks CRM write/delete drift.

Expected result: `3` checks, `1` emitted, `2` blocked.

Start with `summary.md` for the readable verdict, then inspect
`evidence-reader.md`, `manifest.json`, `suite-report.json`, and the files under
`evidence/` and `verification/`.
