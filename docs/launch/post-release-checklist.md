# Post-Release Checklist

Use this checklist after publishing a public Sentinel release.

## v0.1.0 Public Proof

- GitHub Release: https://github.com/Martin123132/sentinel-manifold-public/releases/tag/v0.1.0
- Tag: `v0.1.0`
- Target commit: `98ceda103c668af3899b5e526769d2ddabde70ff`
- CI run: https://github.com/Martin123132/sentinel-manifold-public/actions/runs/25643978948
- Live sandbox: https://sentinel-manifold-public.onrender.com/

## Confirmed

- Release is published as latest.
- Release is not draft and not prerelease.
- Latest `main` CI passed for the release commit.
- Public demo smoke test returned `public_demo: true`.
- Public providers endpoint exposed only `local_demo`.
- Unauthenticated audit history returned `401`.
- Demo suite returned `PASS`, `5` cases, `5` passed, and `0` failed.
- README and roadmap now describe `v0.1.0 Public Proof` as live.

## Next Milestone

Build an external adoption proof that shows Sentinel running as a release gate
outside its own repo.
