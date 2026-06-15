# Public Launch Copy

Use these snippets for the live `v0.1.5 Suite Authoring Kit` release.

Release:

https://github.com/Martin123132/sentinel-manifold-public/releases/tag/v0.1.5

Live demo:

https://sentinel-manifold-public.onrender.com/

## Short Post

Sentinel Manifold `v0.1.5 Suite Authoring Kit` is live.

It is a source-available AI release gate that now has a clearer suite-writing
path: runnable templates, a validator, and a worked first custom suite that
goes from policy text to CI report.

Authoring guide:

https://github.com/Martin123132/sentinel-manifold-public/blob/main/docs/suite-authoring.md

## Slightly Longer Post

Sentinel Manifold `v0.1.5 Suite Authoring Kit` is live. It keeps the bounded demo
sandbox, admin-only evidence export, and CI release-gate artifact story while
making it easier for new testers to write their own release-gate suites.

The product story is still simple:

> Fail releases when AI behavior regresses.

What is new in this release pack:

- suite authoring guide,
- five runnable suite templates,
- dependency-free suite validator,
- first custom suite walkthrough,
- CI validation for authoring examples,
- first custom suite report artifact.

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
to see the proof pack PASS. Then copy a template and run
`python scripts/validate-suite.py --run samples/first-custom-suite.json` to see
the authoring path PASS too.
