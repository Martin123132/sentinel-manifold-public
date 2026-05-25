# Customer-Shaped Regression Pack

This pack turns Sentinel's policy proof into examples that look more like real
buyer release checks. It is still reference-bound: Sentinel checks supplied AI
outputs against supplied references, not external truth.

Run it locally:

```powershell
python app\cli.py suite --input samples\customer-shaped-regression-suite.json --out out\customer-shaped-regression-suite-report.json --fail-on-fail
```

## What It Covers

| Buyer story | Safe case | Blocked regressions |
| --- | --- | --- |
| Support operations | `support-ops-safe-refund-escalation` | `support-ops-refund-threshold-drift`, `support-ops-escalation-removal` |
| Regulated claims/payments | `regulated-claims-safe-approval-review` | `regulated-claims-approval-removal`, `regulated-claims-threshold-drift` |
| Agentic CRM/email workflows | `agentic-crm-safe-read-draft` | `agentic-crm-edit-delete-drift`, `agentic-email-send-without-approval` |
| Code-review release notes | `code-review-release-safe-dependency-auth` | `code-review-release-major-version-drift`, `code-review-release-auth-behavior-drift` |

## Product Proof

The suite proves four release-gate stories:

- Support releases fail if refund thresholds or escalation rules drift.
- Regulated releases fail if approval or review requirements are weakened.
- Agent releases fail if read-only or draft-only boundaries turn into writes,
  deletes, sends, or unapproved actions.
- Code-review release notes fail if version or authentication behavior claims
  drift from the supplied patch notes.

The public demo stays short and bounded. This deeper pack is for local and CI
proof, where teams can collect `out/customer-shaped-regression-suite-report.json`
as a release-gate artifact.
