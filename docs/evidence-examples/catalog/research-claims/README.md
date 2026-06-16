# Research Claims Catalog Evidence

This pack is generated from
`samples/catalog/research-claims-suite.json`.

It shows a research claims release gate that:

- emits scoped preliminary research wording,
- blocks unsupported guarantee wording,
- blocks evidence-count drift.

Expected result: `3` checks, `1` emitted, `2` blocked.

Start with `summary.md` for the readable verdict, then inspect
`evidence-reader.md`, `manifest.json`, `suite-report.json`, and the files under
`evidence/` and `verification/`.
