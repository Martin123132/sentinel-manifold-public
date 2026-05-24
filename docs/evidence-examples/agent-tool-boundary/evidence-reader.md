# Sentinel Evidence Reader

This file is the plain-English guide to the exported Sentinel proof bundle.

## Quick Verdict

- Verdict: **Verified release-gate bundle**
- Total saved checks: 5
- Emitted checks: 1
- Blocked checks: 4
- Integrity verified: 5
- Failed verification: 0
- Policy profiles: agent_tool

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
- `evidence/sm-6a858235c2.evidence.json`
- `verification/sm-6a858235c2.verification.json`
- `evidence/sm-a6d3f951ca.evidence.json`
- `verification/sm-a6d3f951ca.verification.json`
- `evidence/sm-da305a68b9.evidence.json`
- `verification/sm-da305a68b9.verification.json`
- `evidence/sm-9a8d8ed911.evidence.json`
- `verification/sm-9a8d8ed911.verification.json`
- `evidence/sm-9da03c8cdd.evidence.json`
- `verification/sm-9da03c8cdd.verification.json`
