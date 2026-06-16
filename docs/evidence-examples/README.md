# Public Evidence Examples

These are static, sanitized Sentinel proof packs. They are generated from public
demo suites in this repo, not from hosted-demo audit history, customer data, or
private deployments.

Each example contains:

- `summary.md`
- `evidence-reader.md`
- `manifest.json`
- `suite-report.json`
- `evidence/*.evidence.json`
- `verification/*.verification.json`

## Examples

| Example | What it proves | Expected bundle result |
| --- | --- | --- |
| [Support assistant](support-assistant/README.md) | A support assistant release gate can block refund, escalation, agent/tool, regulated, and research drift. | `5` checks, `1` emitted, `4` blocked |
| [Regulated workflow](regulated-workflow/README.md) | Approval and threshold wording cannot quietly relax from the supplied references. | `2` checks, `1` emitted, `1` blocked |
| [Agent tool boundary](agent-tool-boundary/README.md) | Read-only or approval-bound agents cannot drift into storing credentials, sending, writing, deleting, or unapproved release. | `5` checks, `1` emitted, `4` blocked |
| [Code review](code-review/README.md) | AI patch summaries cannot change dependency versions or authentication behavior. | `2` checks, `1` emitted, `1` blocked |
| [Catalog starter packs](catalog/README.md) | Every Suite Catalog starter pack has an inspectable passing evidence example. | `5` packs, `15` checks, `5` emitted, `10` blocked |

## Reference Boundary

These examples prove Sentinel checked supplied candidates against supplied
references and preserved verifiable evidence. They do not prove external truth,
legal compliance, security certification, or future model behavior.

## Policy Tuning

The public examples now feed `samples/policy-tuning-suite.json`. That suite
adds near-miss checks for approval-removal wording, read-only agent drift, and
code-review version/auth summaries so CI can catch subtle regressions as the
policy packs improve.
