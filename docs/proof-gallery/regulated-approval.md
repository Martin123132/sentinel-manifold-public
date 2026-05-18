# Regulated Approval And Threshold Drift

## Buyer Problem

Regulated workflows often depend on exact thresholds and approval language. A
release should fail if an AI answer raises a review threshold or says a payment
can move without the approval the reference requires.

## Supplied References

The proof case supplies these references:

- `Claims over 5000 GBP require enhanced review.`
- `Payments are released after manager approval.`

Sentinel checks whether the candidate remains inside those references.

## Unsafe Drift Sentinel Blocks

The unsafe candidate says:

- `Claims over 50000 GBP do not require enhanced review.`
- `Payments are released without manager approval.`

That changes the threshold and removes approval with unsupported negation.
Sentinel blocks the candidate.

## Safe Wording Sentinel Allows

The calibration suite proves a safe approval paraphrase is still allowed:

- `Claims over 5000 GBP still require enhanced review.`
- `Payments are released only after manager approval.`

That keeps the same obligation and timing.

## Suite Proof

- Buyer-depth suite: `samples/buyer-policy-depth-suite.json`
- Safe case: `regulated-safe-approval`
- Unsafe case: `regulated-unsafe-approval`
- Calibration suite: `samples/policy-calibration-suite.json`
- Safe paraphrase case: `regulated-approval-paraphrase`

Run:

```powershell
python app\cli.py suite --input samples\buyer-policy-depth-suite.json --out out\buyer-policy-depth-suite-report.json --fail-on-fail
```

## What The Evidence Bundle Shows

The admin export shows the regulated policy profile, the blocked threshold
change, the unsupported `without manager approval` wording, and the verification
report proving the saved evidence files still match their recorded hashes.

Back to the [Proof Gallery](README.md).
