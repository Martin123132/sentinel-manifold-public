# Suite Catalog

The Suite Catalog gives new Sentinel users ready-made starter packs. Copy the
closest suite, replace the references with your policy or release notes, then
run the validator before putting it in CI.

These packs are still reference-bound. They prove candidate output against the
references supplied in the suite, not against external truth.

## Catalog Packs

| Buyer shape | Suite | Evidence example | What it catches |
| --- | --- | --- | --- |
| Support operations | `samples/catalog/support-operations-suite.json` | [support operations](evidence-examples/catalog/support-operations/README.md) | refund threshold drift and escalation review removal |
| Regulated approval | `samples/catalog/regulated-approval-suite.json` | [regulated approval](evidence-examples/catalog/regulated-approval/README.md) | approval removal and claims threshold drift |
| Research claims | `samples/catalog/research-claims-suite.json` | [research claims](evidence-examples/catalog/research-claims/README.md) | unsupported guarantees and evidence-count drift |
| Code review | `samples/catalog/code-review-release-suite.json` | [code-review release](evidence-examples/catalog/code-review-release/README.md) | dependency version drift and production-data write drift |
| Agent tool boundary | `samples/catalog/agent-tool-boundary-suite.json` | [agent tool boundary](evidence-examples/catalog/agent-tool-boundary/README.md) | sending without approval and CRM write/delete drift |

## Try One Pack

```powershell
python scripts\validate-suite.py --run samples\catalog\support-operations-suite.json
python app\cli.py suite --input samples\catalog\support-operations-suite.json --out out\catalog-support-operations-suite-report.json --fail-on-fail
```

Expected result:

```text
PASS, 3 cases, 3 passed, 0 failed
```

## How To Choose

Choose `support-operations-suite.json` when the first risk is customer-facing
policy drift: refunds, escalations, credits, response boundaries.

Choose `regulated-approval-suite.json` when the first risk is process drift:
approval, review, identity verification, release thresholds.

Choose `research-claims-suite.json` when the first risk is claim strength:
preliminary findings becoming guarantees, changed percentages, or changed
evidence counts.

Choose `code-review-release-suite.json` when the first risk is release-note
drift: dependency versions, authentication behavior, migration summaries, or
production-data behavior.

Choose `agent-tool-boundary-suite.json` when the first risk is agent action
drift: read-only becoming write/delete/send, draft-only becoming sending, or
approval-required action becoming unapproved action.

## What CI Produces

The main CI release gate validates every catalog suite and writes catalog
reports:

```text
out/catalog-support-operations-suite-report.json
out/catalog-regulated-approval-suite-report.json
out/catalog-research-claims-suite-report.json
out/catalog-code-review-release-suite-report.json
out/catalog-agent-tool-boundary-suite-report.json
```

Those reports are uploaded in the `sentinel-release-gate` artifact alongside the
existing proof reports and evidence packs.

For static public proof, each catalog pack also has a checked-in evidence
example under [docs/evidence-examples/catalog/](evidence-examples/catalog/README.md).
Those examples show the suite report, readable summary, manifest, evidence JSON,
and verification JSON for the passing catalog gate.

To rebuild all catalog evidence examples:

```powershell
python scripts\build-evidence-example.py --config docs\evidence-examples\catalog\catalog-examples.json
```

## Next Step After Copying

After a catalog pack passes, replace one reference and one candidate with your
own wording. Keep the expected action obvious:

- use `EMIT` for safe, supported wording,
- use `BLOCK` for the unsafe drift you want CI to catch.

Then run:

```powershell
python scripts\validate-suite.py --run samples\your-suite.json
python app\cli.py suite --input samples\your-suite.json --out out\your-suite-report.json --fail-on-fail
```
