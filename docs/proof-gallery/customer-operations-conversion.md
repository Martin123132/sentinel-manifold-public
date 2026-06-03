# Customer Operations Conversion Guard

## Buyer Problem

Support teams often combine customer operations and compliance rules in the same
release path: refunds must stay within an explicit cap, escalated billing issues
must be reviewed, and regulated payment actions must keep manager approval checks.
Small wording changes can quietly remove those protections.

## Supplied References

The proof case uses the customer-shaped regression suite references:

- `Refunds under 75 GBP may be handled by support staff.`
- `Escalated billing disputes are reviewed by a human support lead.`
- `Claims over 5000 GBP require enhanced review.`
- `Payments require manager approval before release.`

Sentinel judges candidates against these references, not against outside policy
documents.

## Unsafe Drift Sentinel Blocks

The blocked cases show three real release drifts:

- Threshold drift: `support-ops-refund-threshold-drift` changes refund limits
  from 75 GBP to 250 GBP.
- Escalation drift: `support-ops-escalation-removal` removes required human review
  for escalated billing disputes.
- Approval drift: `regulated-claims-approval-removal` drops the manager approval
  requirement for payment release.

That combination is common in real customer operations: support speed pressure and
regulated workflow pressure combine into a single risky release path.

## Safe Wording Sentinel Allows

The suite's safe reference-aligned candidate remains strict while avoiding
over-specific wording:

- `Refunds under 75 GBP may be handled by support staff.`
- `Escalated billing disputes are reviewed by a human support lead.`
- `Claims over 5000 GBP require enhanced review.`
- `Payments require manager approval before release.`

If these references and policy profiles stay intact, Sentinel can emit this
candidate as the supported output.

## Suite Proof

- Suite: `samples/customer-shaped-regression-suite.json`
- Safe case: `support-ops-safe-refund-escalation`
- Blocked cases:
  - `support-ops-refund-threshold-drift`
  - `support-ops-escalation-removal`
  - `regulated-claims-approval-removal`

Run locally:

```powershell
python app\cli.py suite --input samples\customer-shaped-regression-suite.json --out out\customer-shaped-regression-suite-report.json --fail-on-fail
```

## What the Bundle Shows

In admin mode, an exported proof bundle shows:

- which policy profiles were evaluated,
- why threshold, escalation, and approval drifts were treated as unsafe,
- evidence and verification files for each blocked case,
- the executive release-gate verdict and integrity status in `manifest.json`.

This makes the customer-shaped support-to-regulatory handoff story clear to
reviewers.

Back to the [Proof Gallery](README.md).
