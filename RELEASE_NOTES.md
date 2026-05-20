# v0.1.1 Adoption Proof

Sentinel Manifold `v0.1.1 Adoption Proof` packages the post-`v0.1.0` trust work:
the release gate now has a standalone external adoption demo repo, a public
evidence example, deeper buyer policy suites, a proof gallery, and clearer
admin evidence exports.

## What This Release Proves

- Sentinel can run as a copied release gate in another app-shaped repo:
  https://github.com/Martin123132/sentinel-support-assistant-demo
- Public reviewers can inspect a sanitized evidence bundle without admin access:
  `docs/evidence-examples/support-assistant/`
- Buyer-shaped proof now covers support, regulated workflow, research claims,
  code review, and agent/tool boundaries.
- Strict policies are calibrated against safe paraphrases so the gate checks
  overblocking as well as unsafe emissions.
- Admin evidence bundles include `summary.md`, `evidence-reader.md`,
  `manifest.json`, evidence JSON, and verification JSON.
- GitHub Actions release-gate workflows use Node 24-ready action majors.

Product proof:

> Show Sentinel working in another repo, with readable evidence people can inspect.

## Try It In 30 Seconds

1. Open the live sandbox: https://sentinel-manifold-public.onrender.com/
2. Scroll to **Release Gate**.
3. Click **Run Demo Suite**.
4. Confirm **PASS**, `5` cases, `5` passed, and `0` failed.

## For Developers

Start with `INTEGRATION.md`, then inspect the standalone support-assistant demo:

```text
https://github.com/Martin123132/sentinel-support-assistant-demo
```

The starter path is still:

```powershell
python app\cli.py suite --input samples\integration-starter-suite.json --out out\integration-starter-suite-report.json --fail-on-fail
```

## For Evidence Reviewers

Open the public support-assistant evidence example:

```text
docs/evidence-examples/support-assistant/
```

It contains a buyer-readable summary, evidence reader, manifest, suite report,
five evidence packs, and five verification reports.

## Commercial Boundary

Personal, research, nonprofit, educational, evaluation, community, and
small-business use is welcome under the community license terms. Larger
commercial integrations, hosted services, model providers, search engines, and
revenue-generating platforms require written permission.

See `LICENSE`, `COMMERCIAL_USE.md`, and `TRADEMARKS.md`.

## Validation

This release is expected to pass:

```powershell
python -m unittest discover -s tests
python -m compileall app
python -m py_compile scripts\build-evidence-example.py
node --check web/app.js
python app\cli.py suite --input samples\regression-suite.json --out out\suite-report.json --fail-on-fail
python app\cli.py suite --input samples\agent-policy-suite.json --out out\agent-policy-suite-report.json --fail-on-fail
python app\cli.py suite --input samples\buyer-policy-depth-suite.json --out out\buyer-policy-depth-suite-report.json --fail-on-fail
python app\cli.py suite --input samples\policy-calibration-suite.json --out out\policy-calibration-suite-report.json --fail-on-fail
python app\cli.py suite --input samples\integration-starter-suite.json --out out\integration-starter-suite-report.json --fail-on-fail
python app\cli.py suite --input examples\external-adoption\support-assistant\sentinel-suite.json --out out\external-adoption-suite-report.json --fail-on-fail
python app\cli.py suite --input samples\mixed-proof-suite.json --out out\mixed-proof-suite-report.json --fail-on-fail
```
