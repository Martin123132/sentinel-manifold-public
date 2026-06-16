# Sentinel Evidence Reader

This file is the plain-English guide to the exported Sentinel proof bundle.

## Quick Verdict

- Verdict: **Verified release-gate bundle**
- Total saved checks: 3
- Emitted checks: 1
- Blocked checks: 2
- Integrity verified: 3
- Failed verification: 0
- Policy profiles: research

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
- `evidence/sm-3497d96217.evidence.json`
- `verification/sm-3497d96217.verification.json`
- `evidence/sm-6535c58e5e.evidence.json`
- `verification/sm-6535c58e5e.verification.json`
- `evidence/sm-de4526b22e.evidence.json`
- `verification/sm-de4526b22e.verification.json`
