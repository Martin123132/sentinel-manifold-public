# v0.1.2 Customer Proof

Sentinel Manifold `v0.1.2 Customer Proof` packages the proof work after
`v0.1.1 Adoption Proof`: buyer-specific evidence examples, policy tuning from
those examples, and a customer-shaped regression suite that reads more like real
release work.

## What This Release Proves

- Public reviewers can inspect multiple sanitized evidence examples without an
  admin key:
  `docs/evidence-examples/`
- Sentinel now has buyer-shaped evidence examples for regulated workflow,
  agent/tool boundaries, code review, and the support-assistant fixture.
- The policy tuning suite catches near-miss wording around approval removal,
  read-only agent boundaries, and version/auth drift while preserving safe
  paraphrases.
- The customer-shaped regression suite frames the release gate as support ops,
  regulated claims/payments, agentic CRM/email workflows, and code-review
  release notes.
- GitHub Actions uploads release-gate reports for the regression, agent,
  buyer-depth, calibration, tuning, customer-shaped, integration, and external
  adoption suites.

Product proof:

> Turn policy proof into customer-shaped release regressions buyers can inspect.

## Try It In 30 Seconds

1. Open the live sandbox: https://sentinel-manifold-public.onrender.com/
2. Scroll to **Release Gate**.
3. Click **Run Demo Suite**.
4. Confirm **PASS**, `5` cases, `5` passed, and `0` failed.

The public sandbox remains bounded. Deeper customer-shaped proof lives in local
and CI suites.

## For Developers

Run the customer-shaped proof locally:

```powershell
python app\cli.py suite --input samples\customer-shaped-regression-suite.json --out out\customer-shaped-regression-suite-report.json --fail-on-fail
```

Use the integration guide when copying Sentinel into another repo:

```text
INTEGRATION.md
```

## For Evidence Reviewers

Start with the public evidence examples:

```text
docs/evidence-examples/
```

Then read the customer-shaped regression walkthrough:

```text
docs/customer-shaped-regressions.md
```

These files are generated from public suites and do not contain customer data,
hosted-demo audit history, provider keys, or private deployment evidence.

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
python app\cli.py suite --input samples\policy-tuning-suite.json --out out\policy-tuning-suite-report.json --fail-on-fail
python app\cli.py suite --input samples\customer-shaped-regression-suite.json --out out\customer-shaped-regression-suite-report.json --fail-on-fail
python app\cli.py suite --input samples\integration-starter-suite.json --out out\integration-starter-suite-report.json --fail-on-fail
python app\cli.py suite --input examples\external-adoption\support-assistant\sentinel-suite.json --out out\external-adoption-suite-report.json --fail-on-fail
python app\cli.py suite --input samples\mixed-proof-suite.json --out out\mixed-proof-suite-report.json --fail-on-fail
```
