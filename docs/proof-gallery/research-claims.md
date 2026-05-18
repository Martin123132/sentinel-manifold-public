# Research Claims

## Buyer Problem

Research and technical teams need to share promising results without turning
preliminary evidence into impossible guarantees. A release gate should block
claims like `100% accurate`, `never hallucinates`, or `zero risk` when the
reference only supports a bounded study result.

## Supplied References

The proof case supplies these references:

- `The study observed a 12 percent reduction in handling errors across 40 test runs.`
- `The authors describe the result as preliminary.`

Sentinel checks whether the candidate preserves that scope.

## Unsafe Drift Sentinel Blocks

The unsafe candidate says:

- `The study is 100% accurate, never hallucinates, and proves zero risk in every deployment.`

That converts a preliminary observation into high-certainty deployment claims.
Sentinel blocks the overclaim.

## Safe Wording Sentinel Allows

The calibration suite proves safe paraphrase is allowed:

- `The study observed handling errors fall by 12 percent across 40 test runs.`
- `The authors call the result preliminary.`

That keeps the observed result, test count, and preliminary status.

## Suite Proof

- Buyer-depth suite: `samples/buyer-policy-depth-suite.json`
- Safe case: `research-safe-preliminary`
- Unsafe case: `research-unsafe-overclaim`
- Calibration suite: `samples/policy-calibration-suite.json`
- Safe paraphrase case: `research-preliminary-paraphrase`

Run:

```powershell
python app\cli.py suite --input samples\buyer-policy-depth-suite.json --out out\buyer-policy-depth-suite-report.json --fail-on-fail
```

## What The Evidence Bundle Shows

The admin export shows the research policy profile, the reference wording, the
blocked overclaim, the exact findings that drove the block, and verification
JSON for the evidence pack.

Back to the [Proof Gallery](README.md).
