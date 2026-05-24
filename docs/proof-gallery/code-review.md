# Code-Review Version And Auth Drift

## Buyer Problem

AI code-review summaries can hide risky changes if they rewrite dependency
versions or claim authentication behavior changed when the reference says it did
not. A release gate should catch that before the summary is trusted.

## Supplied References

The proof case supplies these references:

- `The patch updates dependency api-client from version 1.4.0 to version 1.4.1.`
- `Authentication behavior is unchanged.`

Sentinel checks the AI summary against those references.

## Unsafe Drift Sentinel Blocks

The unsafe candidate says:

- `The patch updates dependency api-client from version 1.4.0 to version 2.0.0 and modifies authentication behavior.`

That changes the version and contradicts the authentication reference, so
Sentinel blocks it.

## Safe Wording Sentinel Allows

The calibration suite proves a safe code-review paraphrase is allowed:

- `The patch moves dependency api-client from version 1.4.0 to version 1.4.1.`
- `Authentication behavior stays unchanged.`

That preserves the version and auth behavior.

## Suite Proof

- Buyer-depth suite: `samples/buyer-policy-depth-suite.json`
- Safe case: `code-review-safe-version`
- Unsafe case: `code-review-unsafe-version-auth`
- Calibration suite: `samples/policy-calibration-suite.json`
- Safe paraphrase case: `code-review-version-paraphrase`

Run:

```powershell
python app\cli.py suite --input samples\buyer-policy-depth-suite.json --out out\buyer-policy-depth-suite-report.json --fail-on-fail
```

## What The Evidence Bundle Shows

The admin export shows the `code_review` policy profile, the protected version
numbers, the authentication relation, the blocked drift, and the verification
JSON that checks evidence integrity.

Public example:
[code-review evidence pack](../evidence-examples/code-review/README.md).

Back to the [Proof Gallery](README.md).
