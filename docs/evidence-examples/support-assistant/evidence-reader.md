# Sentinel Evidence Reader

This file is the plain-English guide to the exported Sentinel proof bundle.

## Quick Verdict

- Verdict: **Verified release-gate bundle**
- Total saved checks: 5
- Emitted checks: 1
- Blocked checks: 4
- Integrity verified: 5
- Failed verification: 0
- Policy profiles: agent_tool, regulated, research, support

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
- `evidence/sm-98de758dd0.evidence.json`
- `verification/sm-98de758dd0.verification.json`
- `evidence/sm-05c8a59cad.evidence.json`
- `verification/sm-05c8a59cad.verification.json`
- `evidence/sm-79948d87b7.evidence.json`
- `verification/sm-79948d87b7.verification.json`
- `evidence/sm-079e95ba84.evidence.json`
- `verification/sm-079e95ba84.verification.json`
- `evidence/sm-5711317ed4.evidence.json`
- `verification/sm-5711317ed4.verification.json`
