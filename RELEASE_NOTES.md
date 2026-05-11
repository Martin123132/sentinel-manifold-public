# v0.1.0 Public Proof

Sentinel Manifold now has a first public proof release: a source-available AI release gate that blocks unsupported, contradictory, or overclaiming AI outputs before they ship.

## What This Release Proves

- Run the live public sandbox and see a five-case release gate pass.
- Fail releases in GitHub Actions when AI behavior regresses.
- Export admin-only evidence bundles with readable summaries and machine-checkable JSON.
- Use the `agent_tool` policy pack to block agent tool-boundary drift before release.
- Copy the integration starter suite into another repo and collect evidence artifacts in CI.

Product proof:

> Fail releases when AI behavior regresses.

## Try It In 30 Seconds

1. Open the live sandbox: https://sentinel-manifold-public.onrender.com/
2. Scroll to **Release Gate**.
3. Click **Run Demo Suite**.
4. Confirm **PASS**, `5` cases, `5` passed, and `0` failed.

That proves Sentinel can emit supported answers, block unsafe drift, catch regulated threshold changes, block unsupported research overclaims, and guard generated demo candidates before release.

## For Developers

Start with `INTEGRATION.md`.

The starter path is:

```powershell
python app\cli.py suite --input samples\integration-starter-suite.json --out out\integration-starter-suite-report.json --fail-on-fail
```

The copy-paste workflow is in:

```text
examples/github-actions/sentinel-release-gate.yml
```

## For Admins

Hosted demo admins can unlock with `SENTINEL_API_KEY`, run the demo suite, and download **Export Bundle**. The zip contains:

- `summary.md`
- `manifest.json`
- `evidence/<check_id>.evidence.json`
- `verification/<check_id>.verification.json`

Public visitors can run the sandbox, but they cannot read or export saved evidence.

## Commercial Boundary

Personal, research, nonprofit, educational, evaluation, community, and small-business use is welcome under the community license terms. Larger commercial integrations, hosted services, model providers, search engines, and revenue-generating platforms require written permission.

See `LICENSE`, `COMMERCIAL_USE.md`, and `TRADEMARKS.md`.

## Validation

This release is expected to pass:

```powershell
python -m unittest discover -s tests
python -m compileall app
node --check web/app.js
python app\cli.py suite --input samples\regression-suite.json --out out\suite-report.json --fail-on-fail
python app\cli.py suite --input samples\agent-policy-suite.json --out out\agent-policy-suite-report.json --fail-on-fail
python app\cli.py suite --input samples\integration-starter-suite.json --out out\integration-starter-suite-report.json --fail-on-fail
```
