# Sentinel Evidence Reader

This file is the plain-English guide to the exported Sentinel proof bundle.

## Quick Verdict

- Verdict: **Verified release-gate bundle**
- Total saved checks: 3
- Emitted checks: 1
- Blocked checks: 2
- Integrity verified: 3
- Failed verification: 0
- Policy profiles: support

## How To Read The Bundle

1. Start with `summary.md` for the release-gate result and audit table.
2. Open `manifest.json` for the machine-readable index and count summary.
3. Inspect `evidence/<check_id>.evidence.json` for the original request, candidates, findings, and decision.
4. Inspect `verification/<check_id>.verification.json` to confirm the integrity digest and request hashes.

## What Happened

Sentinel exported saved checks from the audit directory. Each check records whether the gateway emitted a supported candidate or blocked all candidates that drifted from the supplied references.

## Reference-Bound Boundary

Sentinel does not claim external truth. It proves that saved outputs were checked against the references, candidates, and policy settings included in the evidence packs.

## Files Included

- `summary.md`
- `evidence-reader.md`
- `manifest.json`
- `evidence/sm-a6cd324501.evidence.json`
- `verification/sm-a6cd324501.verification.json`
- `evidence/sm-5f81b07240.evidence.json`
- `verification/sm-5f81b07240.verification.json`
- `evidence/sm-e46e41b1b0.evidence.json`
- `verification/sm-e46e41b1b0.verification.json`
