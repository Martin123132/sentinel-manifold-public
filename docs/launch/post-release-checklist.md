# Post-Release Checklist

Use this checklist after publishing a public Sentinel release.

## v0.1.1 Adoption Proof

- GitHub Release: https://github.com/Martin123132/sentinel-manifold-public/releases/tag/v0.1.1
- Tag: `v0.1.1`
- Target commit: `da0f0a2812901b1c710012ee7248192b4b578f51`
- CI run: https://github.com/Martin123132/sentinel-manifold-public/actions/runs/26136666242
- Published: `2026-05-24T02:38:24Z`
- Live sandbox: https://sentinel-manifold-public.onrender.com/
- External demo repo: https://github.com/Martin123132/sentinel-support-assistant-demo
- Public evidence example: `docs/evidence-examples/support-assistant/`

## Confirm Before Publishing

- Latest `main` points at the intended release commit.
- Latest `main` CI is green.
- `RELEASE_NOTES.md` contains the final `v0.1.1 Adoption Proof` GitHub Release body.
- `CHANGELOG.md` has a fresh `Unreleased` section and a dated `v0.1.1 Adoption Proof` section.
- No provider keys, customer data, generated `out/` artifacts, or private evidence are included.

## Confirm After Publishing

- Release is published as latest.
- Release is not draft and not prerelease.
- Tag `v0.1.1` points at the intended commit.
- Public demo smoke test returns `public_demo: true`.
- Public providers endpoint exposes only `local_demo`.
- Unauthenticated audit history returns `401`.
- Demo suite returns `PASS`, `5` cases, `5` passed, and `0` failed.
- README, roadmap, release notes, launch copy, external demo repo, and evidence example links render on GitHub.

## Previous Release

### v0.1.0 Public Proof

- GitHub Release: https://github.com/Martin123132/sentinel-manifold-public/releases/tag/v0.1.0
- Tag: `v0.1.0`
- Target commit: `98ceda103c668af3899b5e526769d2ddabde70ff`
- CI run: https://github.com/Martin123132/sentinel-manifold-public/actions/runs/25643978948
