# Sentinel Proof Gallery

This gallery turns the current Sentinel suites into buyer-shaped walkthroughs.
Each page shows the release-gate problem, the supplied references, the unsafe
drift Sentinel blocks, the safe wording it allows, and the evidence an admin can
export after a run.

Sentinel is reference-bound. These examples prove that candidate AI behavior
stays inside the references supplied to the check. They do not prove external
truth, legal compliance, or real-world factual accuracy beyond those supplied
references.

## Proof Cards

| Proof card | Buyer story | Main suite proof |
| --- | --- | --- |
| [Support refund and escalation drift](support-release-gate.md) | Stop support answers changing refund thresholds or removing human escalation. | `support-safe-refund-policy`, `support-unsafe-refund-threshold` |
| [Regulated approval and threshold drift](regulated-approval.md) | Stop approval workflows from relaxing review thresholds or claiming approval is unnecessary. | `regulated-safe-approval`, `regulated-unsafe-approval` |
| [Research claim overreach](research-claims.md) | Stop preliminary findings becoming guaranteed, always-correct claims. | `research-safe-preliminary`, `research-unsafe-overclaim` |
| [Agent tool-boundary drift](agent-tool-boundary.md) | Stop read-only agents drifting into storing credentials, sending replies, or writing records. | `agent-safe-read-only`, `agent-unsafe-tool-boundary` |
| [Code-review version and auth drift](code-review.md) | Stop AI patch summaries changing dependency versions or authentication behavior. | `code-review-safe-version`, `code-review-unsafe-version-auth` |

For the exported proof package itself, start with
[Evidence reader walkthrough](evidence-reader-walkthrough.md).

## Run The Gallery Proof Locally

The main buyer-depth suite contains safe and unsafe cases for all five proof
cards:

```powershell
python app\cli.py suite --input samples\buyer-policy-depth-suite.json --out out\buyer-policy-depth-suite-report.json --fail-on-fail
```

The calibration suite proves the same strict policy packs still allow safe
paraphrases:

```powershell
python app\cli.py suite --input samples\policy-calibration-suite.json --out out\policy-calibration-suite-report.json --fail-on-fail
```

## Admin Evidence Bundle

Admins can unlock the hosted dashboard with `SENTINEL_API_KEY`, run the release
gate, and download **Export Bundle**. The zip includes `evidence-reader.md`,
`summary.md`, `manifest.json`, saved evidence JSON, and verification JSON.

That bundle is the shareable proof package: plain-English summary for buyers and
reviewers, plus machine-readable evidence and integrity verification for deeper
inspection.
