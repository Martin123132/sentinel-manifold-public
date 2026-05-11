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
into a copy-paste GitHub Actions release gate.

The first public release is complete: `v0.1.0 Public Proof` packages the live
demo, CI release gate, integration guide, commercial boundary, and admin evidence
export into a clear release story.

Release: https://github.com/Martin123132/sentinel-manifold-public/releases/tag/v0.1.0

> Fail releases when AI behavior regresses.

## Near-Term Milestones

1. Build an external adoption proof that shows Sentinel running as a release
   gate outside its own repo.
2. Polish the hosted dashboard's first impression around CI, evidence, and
   release-gate proof.
3. Better policy tuning for support, regulated workflows, research claims, code
   review, and agentic tools.
4. More customer-shaped regression examples beyond the starter and mixed-buyer
   suites.
5. Cleaner shareable proof language around exported evidence bundles.

## Boundaries

- The community repo stays dependency-light until the gateway story is clearer.
- Public demo mode must never expose provider keys, customer data, audit history,
  or evidence packs to unauthenticated visitors.
- Commercial use stays governed by `LICENSE` and `COMMERCIAL_USE.md`.
