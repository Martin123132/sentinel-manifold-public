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
shows the same release-gate pattern in an app-shaped adoption example. The buyer
policy depth suite now adds ten deeper support, regulated, research, code review,
and agent/tool cases for local and CI proof. The policy calibration suite adds
ten safe-paraphrase cases so strict profiles prove they do not overblock
legitimate buyer wording. Admin evidence exports now include a buyer-readable
evidence reader, executive verdict, and reference-bound proof language alongside
the machine-readable JSON.

The first public release is complete: `v0.1.0 Public Proof` packages the live
demo, CI release gate, integration guide, commercial boundary, and admin evidence
export into a clear release story.

The hosted dashboard now presents that proof in the first screen: public sandbox
status, release link, CI artifact cue, and demo-suite PASS target.

Release: https://github.com/Martin123132/sentinel-manifold-public/releases/tag/v0.1.0

> Fail releases when AI behavior regresses.

## Near-Term Milestones

1. More customer-shaped regression examples beyond the starter, mixed-buyer,
   support-assistant, buyer-depth, and calibration suites.
2. Tune buyer-specific false positives and false negatives from real trial use.
3. Turn the in-repo adoption fixture into a true separate demo repo when the
   GitHub setup is worth the extra ceremony.
4. Add more customer-shaped exported evidence examples for sales and compliance walkthroughs.

## Boundaries

- The community repo stays dependency-light until the gateway story is clearer.
- Public demo mode must never expose provider keys, customer data, audit history,
  or evidence packs to unauthenticated visitors.
- Commercial use stays governed by `LICENSE` and `COMMERCIAL_USE.md`.
