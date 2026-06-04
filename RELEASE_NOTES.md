# v0.1.3 Proof Candidate

`v0.1.3 Proof Candidate` is now published and adds the conversion-focused proof path that keeps the public demo sandbox simple and keeps release evidence readable.

Current release:
https://github.com/Martin123132/sentinel-manifold-public/releases/tag/v0.1.3

Publicly released in: 2026-06-03

## Product Proof

Sentinel continues to prove the same core claim: AI behavior regressions can block a
release.

This release adds a concrete conversion-facing proof path on top of the existing buyer
suites:

- support ops, refund thresholds, escalation review, and payment approval guardrails
  are tied together in one walkthrough,
- `docs/proof-gallery/customer-operations-conversion.md` explains the buyer story,
- admins can still export evidence bundles, and
- CI continues to upload release-gate suite reports without changing runtime behavior.

The public demo remains bounded and easy to verify:

- health mode stays public sandbox,
- provider listings stay limited to `local_demo`,
- protected routes remain protected,
- demo suite still reports PASS with `5` cases, `5` passed, `0` failed.

## What's New

- New proof walkthrough: `docs/proof-gallery/customer-operations-conversion.md`.
- Release-facing documentation updates:
  - `README.md`
  - `ROADMAP.md`
  - `PRODUCT_BRIEF.md`
  - `CHANGELOG.md`
  - `docs/launch/public-launch-copy.md`
  - `docs/launch/post-release-checklist.md`
  - `docs/launch/v0.1.3-pre-release-checklist.md` retained as a historical pre-publish checklist.
- Existing suite set remains unchanged:
  `samples/customer-shaped-regression-suite.json` is now part of the
  documented conversion proof path.
- Zero changes to API, CLI, dashboard runtime behavior.

## For Developers

Run it locally:

```powershell
python app\cli.py suite --input samples\customer-shaped-regression-suite.json --out out\customer-shaped-regression-suite-report.json --fail-on-fail
```

## Commercial Boundary

Personal, research, nonprofit, evaluation, community, and small-business use
remains welcome. Larger commercial integration remains subject to commercial
boundary terms.

See `LICENSE`, `COMMERCIAL_USE.md`, and `TRADEMARKS.md`.
