# Public Launch Copy

Use these snippets once `v0.1.6 Suite Catalog` is published.

Release:

https://github.com/Martin123132/sentinel-manifold-public/releases/tag/v0.1.6

Live demo:

https://sentinel-manifold-public.onrender.com/

## Short Post

Sentinel Manifold `v0.1.6 Suite Catalog` is live.

It is a source-available AI release gate that now has ready-made buyer starter
packs: support operations, regulated approval, research claims, code review, and
agent/tool boundary suites.

Suite catalog:

https://github.com/Martin123132/sentinel-manifold-public/blob/main/docs/suite-catalog.md

## Slightly Longer Post

Sentinel Manifold `v0.1.6 Suite Catalog` is live. It keeps the bounded demo
sandbox, admin-only evidence export, and CI release-gate artifact story while
making it easier for new testers to choose a buyer-shaped starter pack and
adapt it to their own references.

The product story is still simple:

> Fail releases when AI behavior regresses.

What is new in this release pack:

- suite catalog guide,
- support operations starter suite,
- regulated approval starter suite,
- research claims starter suite,
- code-review release starter suite,
- agent/tool boundary starter suite,
- catalog suite report artifacts in CI.

Repo:

https://github.com/Martin123132/sentinel-manifold-public

Live sandbox:

https://sentinel-manifold-public.onrender.com/

## Community-Friendly Note

Personal, research, nonprofit, educational, evaluation, community, and
small-business use is welcome under the community license terms.

Larger commercial integrations need written permission. The idea is simple:
people can learn from it and use it fairly, while large platforms that benefit
commercially have to talk to the maintainer first.

## One-Line Pitch

Sentinel Manifold is an AI release gate that blocks unsupported, contradictory,
or overclaiming outputs before they ship, with evidence reviewers can inspect.

## Proof Line

Run the public demo suite, then run `python scripts/run-proof-pack.py` locally
to see the proof pack PASS. Then run
`python scripts/validate-suite.py --run samples/catalog/*.json` to see all
buyer starter packs PASS too.
