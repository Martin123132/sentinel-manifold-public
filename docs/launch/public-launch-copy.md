# Public Launch Copy

Use these snippets when announcing the `v0.1.0 Public Proof` release.

## Short Post

Sentinel Manifold `v0.1.0 Public Proof` is live.

It is a source-available AI release gate: supply trusted references, run candidate AI outputs through Sentinel, and fail the release when behavior regresses.

Try the public sandbox:

https://sentinel-manifold-public.onrender.com/

Click **Run Demo Suite** and look for **PASS**, `5` cases, `5` passed, `0` failed.

## Slightly Longer Post

I have launched Sentinel Manifold `v0.1.0 Public Proof`.

The product story is simple: fail releases when AI behavior regresses.

Sentinel checks AI outputs against supplied reference material, emits the safest supported answer, or blocks the whole candidate pool when every option drifts. The public sandbox includes proof cases for customer support, regulated thresholds, research overclaims, generated candidates, and release-gate behavior.

Developers can copy the GitHub Actions release gate into another repo. Admins can export a zip proof bundle with readable summaries and machine-checkable evidence.

Live demo:

https://sentinel-manifold-public.onrender.com/

Repo:

https://github.com/Martin123132/sentinel-manifold-public

## Community-Friendly Note

Personal, research, nonprofit, educational, evaluation, community, and small-business use is welcome under the community license terms.

Larger commercial integrations need written permission. The idea is simple: people can learn from it and use it fairly, while large platforms that benefit commercially have to talk to the maintainer first.

## One-Line Pitch

Sentinel Manifold is an AI release gate that blocks unsupported, contradictory, or overclaiming outputs before they ship.

## Proof Line

Run the five-case public demo suite: supported answers emit, unsafe drift blocks, regulated threshold changes fail, research overclaims fail, and generated candidates still pass through the guardrail.
