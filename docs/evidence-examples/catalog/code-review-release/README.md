# Code-Review Release Catalog Evidence

This pack is generated from
`samples/catalog/code-review-release-suite.json`.

It shows a code-review release gate that:

- emits a safe dependency, authentication, and migration summary,
- blocks dependency version drift,
- blocks production-data write drift.

Expected result: `3` checks, `1` emitted, `2` blocked.

Start with `summary.md` for the readable verdict, then inspect
`evidence-reader.md`, `manifest.json`, `suite-report.json`, and the files under
`evidence/` and `verification/`.
