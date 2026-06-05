# Trial Adoption Loop

This page explains how to try Sentinel Manifold and turn the result into useful
feedback.

Sentinel is a reference-bound AI release gate. It checks candidate AI output
against the trusted references you provide, then emits safe supported wording or
blocks unsafe drift.

## 1. Run The Proof Pack

Start with the cross-platform proof-pack runner:

```powershell
python scripts/run-proof-pack.py
```

For the extended local proof pack:

```powershell
python scripts/run-proof-pack.py --full
```

Windows users can also run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-proof-pack.ps1
```

Expected result:

```text
All Sentinel proof suites passed.
```

## 2. Adapt One Suite

Copy the starter suite:

```powershell
copy samples\integration-starter-suite.json samples\my-first-sentinel-suite.json
```

Then change one case:

- put your trusted policy, release note, support rule, or tool boundary in
  `references`,
- put the AI output you want to test in `candidates`,
- set `expect.action` to `EMIT` for safe wording or `BLOCK` for unsafe drift.

Run your adapted suite:

```powershell
python app\cli.py suite --input samples\my-first-sentinel-suite.json --out out\my-first-sentinel-suite-report.json --fail-on-fail
```

## 3. Read The Result

Use the suite report first:

- `PASS` means Sentinel behaved as expected for every case.
- `FAIL` means at least one release-gate expectation changed.
- `EMIT` means Sentinel found a safe supported candidate.
- `BLOCK` means Sentinel rejected every candidate for that case.

Evidence packs and verification files are written under `out/audits` when
evidence saving is enabled.

## 4. Report Useful Feedback

Use [trial-feedback-template.md](trial-feedback-template.md), or open one of the
GitHub issue templates:

- trial report,
- policy false positive,
- missed unsafe drift,
- commercial or integration enquiry.

Useful feedback says:

- what kind of AI output you tested,
- which references you supplied,
- what Sentinel emitted or blocked,
- what you expected instead,
- whether the wording in the report or evidence was clear.

Please do not post secrets, customer data, provider keys, private evidence, or
hosted-demo audit history.

## 5. Commercial Boundary

Personal, research, nonprofit, educational, evaluation, community, and
small-business use is welcome under the community license terms. Larger
commercial integrations require written permission.

Read:

- [COMMERCIAL_USE.md](../COMMERCIAL_USE.md)
- [LICENSE](../LICENSE)
- [TRADEMARKS.md](../TRADEMARKS.md)

## 6. What This Proves

The trial proves Sentinel can check supplied candidate outputs against supplied
references and fail release when behavior regresses.

It does not prove external truth, legal compliance, medical correctness, or
general model safety outside the supplied references.
