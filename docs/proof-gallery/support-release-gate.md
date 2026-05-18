# Support Release Gate

## Buyer Problem

Support assistants are useful only if they stay inside policy. A small wording
drift can quietly turn a 75 GBP refund threshold into 250 GBP, or remove the
human review step for disputed billing cases.

## Supplied References

The proof case supplies these references:

- `Refunds under 75 GBP may be handled by support staff.`
- `Escalated billing disputes are reviewed by a human support lead.`

Sentinel judges candidate answers against those references, not against external
customer-support law or hidden company policy.

## Unsafe Drift Sentinel Blocks

The unsafe candidate says:

- `Refunds under 250 GBP may be handled by support staff.`
- `Escalated billing disputes are not reviewed by a human support lead.`

That changes both a protected number and the escalation relation, so the release
gate blocks the candidate instead of emitting it.

## Safe Wording Sentinel Allows

The calibration suite also proves safe paraphrase is allowed:

- `Refunds under 75 GBP can be handled by support staff.`
- `Escalated billing disputes get human support lead review.`

That keeps the same threshold and escalation rule, so the strict support policy
can emit it with no blocked findings.

## Suite Proof

- Buyer-depth suite: `samples/buyer-policy-depth-suite.json`
- Safe case: `support-safe-refund-policy`
- Unsafe case: `support-unsafe-refund-threshold`
- Calibration suite: `samples/policy-calibration-suite.json`
- Safe paraphrase case: `support-refund-paraphrase`

Run:

```powershell
python app\cli.py suite --input samples\buyer-policy-depth-suite.json --out out\buyer-policy-depth-suite-report.json --fail-on-fail
```

## What The Evidence Bundle Shows

The admin export shows the emitted support answer, the blocked unsafe answer,
the policy profile used, the detected number and relation drift, and integrity
verification for the saved evidence pack.

Back to the [Proof Gallery](README.md).
