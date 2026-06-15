# Public Roadmap

Sentinel Manifold's public goal is simple: make AI safety behavior visible,
testable, and auditable before risky outputs reach users.

## Current Proof

Sentinel can run a regression suite in CI and fail a release when model, prompt,
provider, or policy changes start emitting unsupported answers. The public demo
now covers support, regulated workflow, research-claim, and generated-candidate
proof cases, with a deeper mixed-buyer suite available for local CI. Admins can
also export a compliance-style evidence bundle from the hosted demo without
making saved evidence public; the bundle now includes both machine-readable JSON
and a plain-English release-gate summary. The first deeper policy pack covers AI
agent tool-boundary drift before release. The integration kit turns that proof
into a copy-paste GitHub Actions release gate, and the support-assistant fixture
now has a standalone public demo repo showing the same release-gate pattern
outside Sentinel itself. The buyer policy depth suite now adds ten deeper support, regulated, research, code review,
and agent/tool cases for local and CI proof. The policy calibration suite adds
ten safe-paraphrase cases so strict profiles prove they do not overblock
legitimate buyer wording. Admin evidence exports now include a buyer-readable
evidence reader, executive verdict, and reference-bound proof language alongside
the machine-readable JSON. The proof gallery now turns those suites and evidence
exports into buyer-shaped walkthroughs for support, regulated workflow,
research, agent/tool, and code-review release gates. Public evidence examples
now give reviewers sanitized proof bundles for support-assistant, regulated
workflow, agent/tool, and code-review stories without admin access. The policy
tuning suite turns those examples into near-miss CI checks for regulated
approval wording, read-only agent boundaries, and code-review version/auth
summaries. The customer-shaped regression suite now frames that proof as support
operations, regulated claims/payments, agentic CRM/email workflows, and
code-review release notes. The trial adoption pack now gives first-time testers
a 10-minute guide, a cross-platform one-command proof-pack runner, feedback
templates, issue forms for reporting false positives or missed drift, and test
coverage for the proof-pack runner's suite list. The latest release adds a
Suite Authoring Kit: runnable templates, a dependency-free validator, and a
plain-English authoring guide so trial users can create their own release-gate
cases. A first custom suite walkthrough now shows the same pattern end to end
for a fake subscription-support copilot.

The first public release is complete: `v0.1.0 Public Proof` packages the live
demo, CI release gate, integration guide, commercial boundary, and admin evidence
export into a clear release story. The second public release is also live:
`v0.1.1 Adoption Proof` packages the external demo repo, public evidence
example, proof gallery, buyer-depth suites, calibration suite, admin evidence
reader, and Node 24-ready CI.

The third public release is now live: `v0.1.2 Customer Proof` packages public
buyer evidence examples, policy tuning, and customer-shaped regression stories.

The fourth public release is now live: `v0.1.3 Proof Candidate`, with a
conversion-focused proof walkthrough for support-to-regulated handoff checks.

The fifth public release is now live: `v0.1.4 Trial Adoption`, with a
10-minute trial guide, cross-platform proof-pack runner, trial feedback loop,
issue templates, and runner test coverage.

The sixth public release is now live: `v0.1.5 Suite Authoring Kit`, with
runnable suite templates, a suite validator, a worked first custom suite, and CI
validation for authoring examples.

The hosted dashboard now presents that proof in the first screen: public sandbox
status, release link, CI artifact cue, and demo-suite PASS target.

Current release: https://github.com/Martin123132/sentinel-manifold-public/releases/tag/v0.1.5

Previous releases:

- https://github.com/Martin123132/sentinel-manifold-public/releases/tag/v0.1.4
- https://github.com/Martin123132/sentinel-manifold-public/releases/tag/v0.1.3
- https://github.com/Martin123132/sentinel-manifold-public/releases/tag/v0.1.2
- https://github.com/Martin123132/sentinel-manifold-public/releases/tag/v0.1.1
- https://github.com/Martin123132/sentinel-manifold-public/releases/tag/v0.1.0

> Fail releases when AI behavior regresses.

## Near-Term Milestones

1. Build a Suite Catalog with more buyer starter packs for common first use
   cases.
2. Use the Suite Authoring Kit with trial users and improve confusing template
   or validator wording.
3. Use trial reports to tune buyer-specific false positives and false negatives.

## Boundaries

- The community repo stays dependency-light until the gateway story is clearer.
- Public demo mode must never expose provider keys, customer data, audit history,
  or evidence packs to unauthenticated visitors.
- Commercial use stays governed by `LICENSE` and `COMMERCIAL_USE.md`.
