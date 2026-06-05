# Sentinel Trial Guide

Use this guide when you want to try Sentinel Manifold as a release gate in about
10 minutes.

Sentinel is reference-bound: it checks candidate AI output against the trusted
references you provide. It does not claim external truth.

## 1. Clone And Run The Proof Pack

```powershell
git clone https://github.com/Martin123132/sentinel-manifold-public.git
cd sentinel-manifold-public
powershell -ExecutionPolicy Bypass -File .\scripts\run-proof-pack.ps1
```

The script runs the public proof suites and writes reports under `out/`.

Expected result:

```text
All Sentinel proof suites passed.
```

## 2. What PASS Means

`PASS` means the suite behaved exactly as expected:

- safe reference-aligned wording emitted,
- unsafe drift blocked,
- overclaims blocked,
- agent/tool boundaries held,
- release-gate reports were written for inspection.

`PASS` does not mean Sentinel checked the real world. It means Sentinel checked
the candidates against the supplied references and policy profile.

## 3. What BLOCK Means

`BLOCK` means Sentinel found no candidate safe enough to emit for that case.
That is the behavior you want when a release changes an answer beyond the
trusted reference material.

Common reasons:

- a number changed,
- a required approval or review step disappeared,
- a read-only agent became a write/delete/send agent,
- a preliminary claim became a guarantee,
- a dependency or authentication summary drifted.

## 4. Adapt One Case To Your Own Project

Start from the integration starter suite:

```powershell
copy samples\integration-starter-suite.json samples\my-first-sentinel-suite.json
```

Then edit one case:

- replace `references` with your policy, release note, support rule, or tool
  boundary,
- replace `candidates` with the AI output you want to test,
- keep the `expect` block simple: `EMIT` for safe wording, `BLOCK` for unsafe
  drift.

Run it:

```powershell
python app\cli.py suite --input samples\my-first-sentinel-suite.json --out out\my-first-sentinel-suite-report.json --fail-on-fail
```

## 5. Copy Into Another Repo

For GitHub Actions adoption, start with:

- [INTEGRATION.md](INTEGRATION.md)
- [examples/github-actions/sentinel-release-gate.yml](examples/github-actions/sentinel-release-gate.yml)
- [examples/external-adoption/support-assistant/README.md](examples/external-adoption/support-assistant/README.md)

## 6. Share Useful Feedback

Helpful trial feedback includes:

- what kind of AI output you tested,
- which suite or case you changed,
- whether Sentinel emitted or blocked,
- whether the result matched your expectation,
- any wording that felt confusing in the report or evidence.

Use [docs/trial-feedback-template.md](docs/trial-feedback-template.md), or open
one of the GitHub issue templates.

## 7. Commercial Boundary

Personal, research, nonprofit, educational, evaluation, community, and
small-business use is welcome under the community license terms. Larger
commercial integrations require written permission. See
[COMMERCIAL_USE.md](COMMERCIAL_USE.md).
