# Public Launch Copy

Use these snippets once `v0.1.7 Catalog Evidence` is published.

Release:

https://github.com/Martin123132/sentinel-manifold-public/releases/tag/v0.1.7

Live demo:

https://sentinel-manifold-public.onrender.com/

## Short Post

Sentinel Manifold `v0.1.7 Catalog Evidence` is live.

It is a source-available AI release gate that now has inspectable public
evidence examples for every Suite Catalog starter pack.

Catalog evidence:

https://github.com/Martin123132/sentinel-manifold-public/blob/main/docs/evidence-examples/catalog/README.md

## Slightly Longer Post

Sentinel Manifold `v0.1.7 Catalog Evidence` is live. It keeps the bounded demo
sandbox, admin-only evidence export, and CI release-gate artifact story while
making every Suite Catalog starter pack easier to inspect before a team adapts
it to their own references.

The product story is still simple:

> Fail releases when AI behavior regresses.

What is new in this release pack:

- catalog evidence index,
- support operations evidence example,
- regulated approval evidence example,
- research claims evidence example,
- code-review release evidence example,
- agent/tool boundary evidence example,
- tests proving each catalog evidence pack is complete and verified.

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
`python scripts/validate-suite.py --run samples/catalog/*.json` and inspect
`docs/evidence-examples/catalog/` to see what the passing catalog evidence looks
like.
