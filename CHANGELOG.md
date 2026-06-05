# Changelog

All notable public-proof changes for Sentinel Manifold are tracked here.

## Unreleased

### Added

- Add `TRIAL_GUIDE.md` as a 10-minute adoption path for first-time testers.
- Add `scripts/run-proof-pack.py` to run the public proof suites with one
  cross-platform command.
- Keep `scripts/run-proof-pack.ps1` as a Windows-friendly wrapper.
- Add `docs/trial-adoption.md` to explain the trial loop from proof-pack run to
  useful feedback.
- Add unit tests for the proof-pack runner suite list and file coverage.
- Add trial feedback docs and GitHub issue templates for trial reports, false
  positives, missed drift, and commercial enquiries.
- Prepare `v0.1.4 Trial Adoption` release notes and checklist as the next
  release candidate.

### Changed

- Tighten post-`v0.1.3` release hygiene: release chronology, checklist status,
  and public-facing proof wording.
- Move the next milestone from proof publication to trial adoption and feedback.

## v0.1.3 Proof Candidate - 2026-06-03

### Added

- Added conversion-focused proof walkthrough:
  `docs/proof-gallery/customer-operations-conversion.md`.
- Aligned `README`, `ROADMAP`, `PRODUCT_BRIEF`, and `RELEASE_NOTES` to a
  published `v0.1.3` milestone.
- Added `docs/launch/public-launch-copy.md` and `docs/launch/post-release-checklist`
  follow-through updates for release publication and proof continuity.
- Added `docs/launch/v0.1.3-pre-release-checklist.md` as the historical pre-release
  verification artifact for this milestone.

### Changed

- Kept API, CLI, and dashboard behavior unchanged.
- Kept public sandbox boundaries unchanged (`local_demo` only, protected routes).
- Kept evidence export admin-only and strengthened release-story clarity for buyers.

## v0.1.2 Customer Proof - 2026-05-30

### Changed

- Publish `v0.1.2 Customer Proof` as the customer-shaped proof release after
  `v0.1.1 Adoption Proof`.
- Point README, roadmap, launch copy, and checklist materials at the live
  `v0.1.2` GitHub Release.
- Add public evidence examples for regulated workflow, agent/tool boundaries,
  and code-review release gates.
- Extend the evidence example builder so docs examples can be rebuilt from
  selected case IDs in public suites.
- Add a ten-case policy tuning suite for near-miss regulated, agent/tool, and
  code-review wording.
- Run the policy tuning suite in CI and upload its release-gate report.
- Strengthen deterministic approval-removal and agent/tool action detection for
  common buyer wording.
- Add a twelve-case customer-shaped regression suite for support operations,
  regulated claims/payments, agentic CRM/email workflows, and code-review
  release notes.
- Run the customer-shaped regression suite in CI and upload its release-gate
  report.

## v0.1.1 Adoption Proof - 2026-05-20

### Added

- Add a public support-assistant evidence example with readable summary,
  manifest, suite report, evidence JSON, and verification JSON.
- Add a helper script to rebuild the sanitized evidence example from the public
  support-assistant suite.
- Add a standalone external adoption demo repo link for
  `Martin123132/sentinel-support-assistant-demo`.
- Add a proof gallery with buyer-shaped walkthroughs for support, regulated
  workflow, research, agent/tool, and code-review release gates.
- Add an evidence-reader walkthrough that explains `evidence-reader.md`,
  `summary.md`, `manifest.json`, evidence JSON, and verification JSON together.
- Link the proof gallery from the README and demo proof docs.
- Add `evidence-reader.md` to admin evidence export bundles for
  buyer-readable proof walkthroughs.
- Add executive verdict, generated file list, and reader path fields to evidence
  bundle manifests.
- Expand `summary.md` with proof snapshot and reference-bound "what this proves"
  / "what this does not prove" language.
- Add a ten-case policy calibration suite to prove strict buyer policies allow
  safe paraphrases without overblocking.
- Add a ten-case buyer policy depth suite for support, regulated workflow,
  research, code review, and agent/tool boundary release gates.
- Strengthen deterministic policy checks for more tool/code action verbs,
  approval-removal wording, and high-certainty overclaims.
- Polish the hosted dashboard first screen around release-gate proof, CI
  artifacts, public sandbox limits, and admin evidence export.
- Add a support-assistant external adoption fixture with a five-case release
  gate and copy-paste workflow.

### Changed

- Mark the true external adoption proof as complete in roadmap and product docs.
- Move GitHub Actions workflow and public workflow snippets to Node 24-ready
  action majors.
- Run the buyer policy depth, policy calibration, and external adoption suites
  in CI and upload their reports as release-gate artifacts.
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
