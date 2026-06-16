# Post-Release Checklist

Use this checklist after publishing a public Sentinel release.

Current release checklist:
[v0.1.6 Suite Catalog](v0.1.6-suite-catalog-checklist.md).

## v0.1.6 Suite Catalog

- GitHub Release: https://github.com/Martin123132/sentinel-manifold-public/releases/tag/v0.1.6
- Tag: `v0.1.6`
- Target commit: `a1879e7c42967d2c18026fdec819d1cf38c31907`
- CI run: https://github.com/Martin123132/sentinel-manifold-public/actions/runs/27623428036
- Published: `2026-06-16T14:07:30Z`
- Live sandbox: https://sentinel-manifold-public.onrender.com/
- Suite catalog guide: `docs/suite-catalog.md`
- Catalog suites: `samples/catalog/`
- Catalog validation: `python scripts\validate-suite.py --run samples\catalog\*.json`
- Release text: `RELEASE_NOTES.md`, `CHANGELOG.md`

## Previous Release: v0.1.5 Suite Authoring Kit

- GitHub Release: https://github.com/Martin123132/sentinel-manifold-public/releases/tag/v0.1.5
- Tag: `v0.1.5`
- Target commit: `6f04cb375a7b053087d2f8dcef74cc08931cad9b`
- CI run: https://github.com/Martin123132/sentinel-manifold-public/actions/runs/27583553254
- Published: `2026-06-15T23:38:11Z`
- Live sandbox: https://sentinel-manifold-public.onrender.com/
- Suite authoring guide: `docs/suite-authoring.md`
- First custom suite: `samples/first-custom-suite.json`
- First custom walkthrough: `docs/first-custom-suite.md`
- Release text: `RELEASE_NOTES.md`, `CHANGELOG.md`

## Previous Release: v0.1.4 Trial Adoption

- GitHub Release: https://github.com/Martin123132/sentinel-manifold-public/releases/tag/v0.1.4
- Tag: `v0.1.4`
- Release target: tag `v0.1.4`
- Live sandbox: https://sentinel-manifold-public.onrender.com/
- Trial guide: `TRIAL_GUIDE.md`
- Trial adoption loop: `docs/trial-adoption.md`
- Proof-pack runner: `scripts/run-proof-pack.py`
- Release text: `RELEASE_NOTES.md`, `CHANGELOG.md`

## Previous Release: v0.1.3 Proof Candidate

- GitHub Release: https://github.com/Martin123132/sentinel-manifold-public/releases/tag/v0.1.3
- Tag: `v0.1.3`
- Target commit: `61ec52cade15e939309a22205718d273b73d6662`
- CI run: https://github.com/Martin123132/sentinel-manifold-public/actions/runs/26881961975
- Published: `2026-06-03T11:32:55Z`
- Live sandbox: https://sentinel-manifold-public.onrender.com/
- Public evidence examples: `docs/evidence-examples/`
- Conversion proof walkthrough:
  - `docs/proof-gallery/customer-operations-conversion.md`
- Launch/copy assets: `docs/launch/public-launch-copy.md`

## Previous Release: v0.1.2 Customer Proof

- GitHub Release: https://github.com/Martin123132/sentinel-manifold-public/releases/tag/v0.1.2
- Tag: `v0.1.2`
- Target commit: `9f33cbb60d81b1aec8c2a6aeecb42bbdc7150101`
- CI run: https://github.com/Martin123132/sentinel-manifold-public/actions/runs/26695933302
- Published: `2026-05-30T21:58:20Z`
- Live sandbox: https://sentinel-manifold-public.onrender.com/
- Public evidence examples: `docs/evidence-examples/`
- Customer-shaped regression docs: `docs/customer-shaped-regressions.md`

## Previous Release: v0.1.1 Adoption Proof

- GitHub Release: https://github.com/Martin123132/sentinel-manifold-public/releases/tag/v0.1.1
- Tag: `v0.1.1`
- Target commit: `da0f0a2812901b1c710012ee7248192b4b578f51`
- CI run: https://github.com/Martin123132/sentinel-manifold-public/actions/runs/26136666242
- Published: `2026-05-24T02:38:24Z`
- Live sandbox: https://sentinel-manifold-public.onrender.com/
- External demo repo: https://github.com/Martin123132/sentinel-support-assistant-demo
- Public evidence examples: `docs/evidence-examples/`

## Confirm Before Publishing Next Release

- Latest `main` is clean and points at the intended release commit.
- Latest `main` CI is green.
- `RELEASE_NOTES.md` is ready for the next release body.
- `CHANGELOG.md` has a clear `Unreleased` section plus a dated release entry.
- No provider keys, customer data, generated `out/` artifacts, or private evidence
  are included in published docs.

## Confirm After Publishing

- Release is published as latest and marked as non-draft, non-prerelease.
- Public demo smoke tests still pass:
  - `/api/health` returns `public_demo: true`
  - `/api/providers` exposes only `local_demo`
  - `/api/audits` returns `401` for unauthenticated users
  - demo suite still returns PASS with `5` cases, `5` passed, `0` failed
- README, roadmap, launch copy, and proof gallery links render on GitHub.
- Release tag points at the intended commit.

## Previous Release

### v0.1.0 Public Proof

- GitHub Release: https://github.com/Martin123132/sentinel-manifold-public/releases/tag/v0.1.0
- Tag: `v0.1.0`
- Target commit: `98ceda103c668af3899b5e526769d2ddabde70ff`
- CI run: https://github.com/Martin123132/sentinel-manifold-public/actions/runs/25643978948
