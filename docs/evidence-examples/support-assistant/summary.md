# Sentinel Evidence Bundle

Executive verdict: **Verified release-gate bundle**

Human-readable release-gate summary for the exported evidence packs.

## Proof Snapshot

| Total audits | Emitted | Blocked | Verified | Failed verification | Newest check | Oldest check |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | 1 | 4 | 5 | 0 | 2026-05-19 21:03:00 UTC | 2026-05-19 21:03:00 UTC |

## Bundle Summary

- Created: 2026-05-19 21:03:00 UTC
- Export limit: 5
- Total audits: 5
- Emitted: 1
- Blocked: 4
- Integrity verified: 5
- Failed verification: 0
- Policy profiles: agent_tool, regulated, research, support
- Newest check: 2026-05-19 21:03:00 UTC
- Oldest check: 2026-05-19 21:03:00 UTC

## What This Proves

- Sentinel evaluated saved AI outputs against the supplied reference material and policy profile.
- The bundle records which checks emitted an answer and which checks blocked unsafe candidates.
- Each evidence pack has a canonical SHA-256 integrity check and request-hash verification report.

## What This Does Not Prove

- It does not prove external truth beyond the references supplied to Sentinel.
- It does not certify a whole organization, deployment, model provider, or future AI behavior.
- It does not make private customer evidence safe to share publicly.

## Audit Rows

| Check | Action | Policy | Risk | Blocked | Integrity |
| --- | --- | --- | --- | --- | --- |
| sm-98de758dd0 | BLOCK | research | 39 | 1 | verified |
| sm-05c8a59cad | BLOCK | agent_tool | 50 | 1 | verified |
| sm-79948d87b7 | BLOCK | support | 68 | 1 | verified |
| sm-079e95ba84 | BLOCK | regulated | 73 | 1 | verified |
| sm-5711317ed4 | EMIT | support | 72 | 1 | verified |
