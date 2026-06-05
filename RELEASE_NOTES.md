# v0.1.4 Trial Adoption

Draft release notes for the next planned public release. This release has not
been tagged or published yet.

Current published release:
https://github.com/Martin123132/sentinel-manifold-public/releases/tag/v0.1.3

## Product Proof

`v0.1.4 Trial Adoption` packages the next step after public proof: make it easy
for a new tester to try Sentinel, run the proof suites, and report useful
feedback.

The product story stays the same:

> Fail releases when AI behavior regresses.

This release candidate focuses on adoption friction:

- first-time testers get a 10-minute trial path,
- local users can run the proof pack with one cross-platform Python command,
- GitHub issue templates capture trial reports, false positives, missed drift,
  and commercial enquiries,
- docs point trial users toward useful, sanitized feedback instead of private
  data or provider keys.

## What Is New

- `TRIAL_GUIDE.md`
- `scripts/run-proof-pack.py`
- `scripts/run-proof-pack.ps1`
- `docs/trial-feedback-template.md`
- GitHub issue templates under `.github/ISSUE_TEMPLATE/`
- `docs/launch/v0.1.4-trial-adoption-checklist.md`

## Try It

```powershell
python scripts/run-proof-pack.py
```

For the full local trial path:

```text
TRIAL_GUIDE.md
```

## Boundaries

- No API changes.
- No CLI behavior changes.
- No dashboard/runtime changes.
- No provider keys.
- No public audit history.
- Public sandbox behavior remains unchanged.

Personal, research, nonprofit, evaluation, community, and small-business use
remains welcome. Larger commercial integration remains subject to commercial
boundary terms.

See `LICENSE`, `COMMERCIAL_USE.md`, and `TRADEMARKS.md`.
