# Catalog Evidence Examples

These are static, sanitized evidence examples generated from the five Suite
Catalog starter packs. They let reviewers inspect what a passing catalog gate
produces without needing admin access, provider keys, or hosted audit history.

Each pack contains:

- `summary.md`
- `evidence-reader.md`
- `manifest.json`
- `suite-report.json`
- `evidence/*.evidence.json`
- `verification/*.verification.json`

## Catalog Packs

| Catalog pack | Suite | Evidence example | Expected result |
| --- | --- | --- | --- |
| Support operations | `samples/catalog/support-operations-suite.json` | [support operations](support-operations/README.md) | `3` checks, `1` emitted, `2` blocked |
| Regulated approval | `samples/catalog/regulated-approval-suite.json` | [regulated approval](regulated-approval/README.md) | `3` checks, `1` emitted, `2` blocked |
| Research claims | `samples/catalog/research-claims-suite.json` | [research claims](research-claims/README.md) | `3` checks, `1` emitted, `2` blocked |
| Code-review release | `samples/catalog/code-review-release-suite.json` | [code-review release](code-review-release/README.md) | `3` checks, `1` emitted, `2` blocked |
| Agent tool boundary | `samples/catalog/agent-tool-boundary-suite.json` | [agent tool boundary](agent-tool-boundary/README.md) | `3` checks, `1` emitted, `2` blocked |

## What This Proves

These examples show that each catalog starter pack can run as a release gate,
produce a passing suite report, preserve evidence JSON, and verify the saved
evidence files after generation.

## What This Does Not Prove

These examples do not prove external truth, legal compliance, security
certification, or future model behavior. Sentinel is reference-bound: it checks
candidate outputs against the references supplied in the suite.
