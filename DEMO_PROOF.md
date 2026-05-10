# Demo Proof: Release Gate

Sentinel Manifold is easiest to understand as a release gate for AI behavior.
The live public sandbox lets anyone run the bundled regression suite without
provider keys, customer data, or admin access.

Live sandbox: https://sentinel-manifold-public.onrender.com/

## What To Click

1. Open the live sandbox.
2. Scroll to **Release Gate**.
3. Click **Run Demo Suite**.
4. Confirm the suite reports **PASS** with `3` cases, `3` passed, and `0` failed.

## What The Three Cases Prove

### 1. Emit the supported answer

The suite gives Sentinel a safe answer and a drifting answer. Sentinel emits the
answer that stays inside the supplied references and blocks the unsafe drift.

Proof point: the gateway can choose the safest supported answer instead of just
accepting the first model output.

### 2. Block unsafe drift

The suite gives Sentinel only unsafe candidates: one changes a relation and one
changes a protected number. Sentinel blocks the pool.

Proof point: when every candidate is unsafe, the gateway can fail closed instead
of shipping a bad answer.

### 3. Generated candidates still guard

The suite asks the built-in `local_demo` provider to generate candidates, then
runs those candidates through the same guardrail path.

Proof point: Sentinel can sit between generation and release, not only inspect
manually pasted answers.

## Why It Matters

The product story is simple: fail releases when AI behavior regresses.

Teams can put Sentinel in CI, run a suite before shipping prompt, model, policy,
or provider changes, and keep evidence that shows exactly what changed.

Personal, research, nonprofit, evaluation, community, and small-business use is
welcome under the community license. Large commercial integrations require
permission. See `COMMERCIAL_USE.md`.
