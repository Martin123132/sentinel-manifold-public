# Public Launch Copy

Use these snippets for the live `v0.1.4 Trial Adoption` release.

Release:

https://github.com/Martin123132/sentinel-manifold-public/releases/tag/v0.1.4

Live demo:

https://sentinel-manifold-public.onrender.com/

## Short Post

Sentinel Manifold `v0.1.4 Trial Adoption` is live.

It is a source-available AI release gate that now has a clearer first-trial
path: a 10-minute guide, cross-platform proof-pack runner, feedback loop, and
issue templates for reporting false positives or missed unsafe drift.

Trial guide:

https://github.com/Martin123132/sentinel-manifold-public/blob/main/TRIAL_GUIDE.md

## Slightly Longer Post

Sentinel Manifold `v0.1.4 Trial Adoption` is live. It keeps the bounded demo
sandbox, admin-only evidence export, and CI release-gate artifact story while
making it easier for new testers to run the proof pack and report useful
feedback.

The product story is still simple:

> Fail releases when AI behavior regresses.

What is new in this release pack:

- 10-minute trial guide,
- cross-platform proof-pack runner,
- Windows-friendly wrapper,
- trial adoption loop documentation,
- feedback and GitHub issue templates,
- runner tests so the trial suite list stays stable.

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
to see the proof pack PASS before adapting one suite to your own project.
