# Changelog

All notable public-proof changes for Sentinel Manifold are tracked here.

## Unreleased

- Add a ten-case policy calibration suite to prove strict buyer policies allow
  safe paraphrases without overblocking.
- Run the policy calibration suite in CI and upload
  `out/policy-calibration-suite-report.json`.
- Add a ten-case buyer policy depth suite for support, regulated workflow,
  research, code review, and agent/tool boundary release gates.
- Strengthen deterministic policy checks for more tool/code action verbs,
  approval-removal wording, and high-certainty overclaims.
- Run the buyer policy depth suite in CI and upload
  `out/buyer-policy-depth-suite-report.json`.
- Polish the hosted dashboard first screen around release-gate proof, CI
  artifacts, public sandbox limits, and admin evidence export.
- Add a support-assistant external adoption fixture with a five-case release
  gate and copy-paste workflow.
- Run the external adoption suite in CI and upload
  `out/external-adoption-suite-report.json`.
- Clean up post-release docs now that `v0.1.0 Public Proof` is live.
- Prepare the next adoption milestone: proving Sentinel as a release gate outside
  its own repo.
- Keep public demo, admin evidence export, and CI release-gate artifacts stable.

## v0.1.0 Public Proof - 2026-05-11

### Added

- Public sandbox demo with a bounded five-case release-gate suite.
- CI release gate that runs Sentinel suites and uploads suite reports plus evidence artifacts.
- Admin-only evidence bundle export with `summary.md`, `manifest.json`, evidence packs, and verification reports.
- Mixed buyer proof cases for support, regulated workflows, research claims, generated candidates, agent/tool boundaries, and code-review drift.
- `agent_tool` policy profile for blocking tool-boundary drift before release.
- Integration kit with a starter suite, copy-paste GitHub Actions workflow, and adoption guide.
- Source-available community license boundary, commercial-use terms, trademark notice, and contribution guidance.

### Product Proof

- Sentinel can fail releases when AI behavior regresses.
- Public users can run safe sandbox checks without provider keys or customer data.
- Admins can export a readable and machine-checkable proof bundle from saved evidence.
- Developers can copy the release gate into another repo and collect CI artifacts.

### Boundaries

- Sentinel is not an external fact checker. It regulates AI outputs against references supplied by the caller.
- Public demo mode does not expose audit history, evidence packs, provider generation, chat completions, provider keys, or customer data to unauthenticated visitors.
- Larger commercial integrations require written permission under the community license terms.
