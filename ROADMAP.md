# Public Roadmap

Sentinel Manifold's public goal is simple: make AI safety behavior visible,
testable, and auditable before risky outputs reach users.

## Current Proof

Sentinel can run a regression suite in CI and fail a release when model, prompt,
provider, or policy changes start emitting unsupported answers.

> Fail releases when AI behavior regresses.

## Near-Term Milestones

1. Better policy packs for support, regulated workflows, research claims, code
   review, and agentic tools.
2. More regression-suite examples that demonstrate realistic failure modes such
   as unsupported overclaims, changed numbers, negated facts, and relation drift.
3. Admin-only hosted demo evidence export so release/compliance reviewers can
   download proof without exposing public visitor data.

## Boundaries

- The community repo stays dependency-light until the gateway story is clearer.
- Public demo mode must never expose provider keys, customer data, audit history,
  or evidence packs to unauthenticated visitors.
- Commercial use stays governed by `LICENSE` and `COMMERCIAL_USE.md`.
