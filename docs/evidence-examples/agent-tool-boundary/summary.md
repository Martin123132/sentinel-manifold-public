# Sentinel Evidence Bundle

Executive verdict: **Verified release-gate bundle**

Human-readable release-gate summary for the exported evidence packs.

## Proof Snapshot

| Total audits | Emitted | Blocked | Verified | Failed verification | Newest check | Oldest check |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | 1 | 4 | 5 | 0 | 2026-05-24 03:06:39 UTC | 2026-05-24 03:06:39 UTC |

## Bundle Summary

- Created: 2026-05-24 03:06:40 UTC
- Export limit: 5
- Total audits: 5
- Emitted: 1
- Blocked: 4
- Integrity verified: 5
- Failed verification: 0
- Policy profiles: agent_tool
- Newest check: 2026-05-24 03:06:39 UTC
- Oldest check: 2026-05-24 03:06:39 UTC

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
| sm-6a858235c2 | BLOCK | agent_tool | 80 | 1 | verified |
| sm-a6d3f951ca | BLOCK | agent_tool | 48 | 2 | verified |
| sm-da305a68b9 | BLOCK | agent_tool | 48 | 1 | verified |
| sm-9a8d8ed911 | BLOCK | agent_tool | 49 | 1 | verified |
| sm-9da03c8cdd | EMIT | agent_tool | 49 | 1 | verified |
