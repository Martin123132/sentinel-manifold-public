# Demo Proof: Release Gate

Sentinel Manifold is easiest to understand as a release gate for AI behavior.
The live public sandbox lets anyone run the bundled regression suite without
provider keys, customer data, or admin access.

Live sandbox: https://sentinel-manifold-public.onrender.com/

## What To Click

1. Open the live sandbox.
2. Scroll to **Release Gate**.
3. Click **Run Demo Suite**.
4. Confirm the suite reports **PASS** with `5` cases, `5` passed, and `0` failed.

## Public Sandbox vs Admin Evidence

The public sandbox is deliberately bounded: visitors can run demo checks and
the five-case release gate, but they cannot read audit history, download single
evidence packs, or export saved evidence.

Admins can unlock the dashboard with `SENTINEL_API_KEY`, run the same suite, and
download **Export Bundle**. The bundle is a zip containing:

- `summary.md`
- `manifest.json`
- `evidence/<check_id>.evidence.json`
- `verification/<check_id>.verification.json`

`summary.md` gives a plain-English release-gate overview, while `manifest.json`
keeps the machine-readable counts and file index. That turns the demo into a
small compliance-style proof pack without exposing private evidence to
unauthenticated visitors.

## What The Five Public Cases Prove

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

### 3. Regulated threshold and negation drift

The suite gives Sentinel a safe regulated answer and an unsafe answer that
changes a review threshold and adds unsupported negation.

Proof point: regulated workflows can fail a release when numbers, review rules,
or customer-impacting claims drift from the supplied source material.

### 4. Research overclaim blocks

The suite gives Sentinel a preliminary research finding, then checks an unsafe
candidate that turns it into guaranteed, always-correct deployment language.

Proof point: research and technical teams can block stronger-than-supported
claims before they are published or shipped.

### 5. Generated candidates still guard

The suite asks the built-in `local_demo` provider to generate candidates, then
runs those candidates through the same guardrail path.

Proof point: Sentinel can sit between generation and release, not only inspect
manually pasted answers.

## Deeper Local Proof

The public demo stays capped at five cases to keep the sandbox bounded. For a
broader local proof, run:

```powershell
python app\cli.py suite --input samples\mixed-proof-suite.json --out out\mixed-proof-suite-report.json --fail-on-fail
```

That suite adds agent/tool-boundary and code-review drift examples.

## Why It Matters

The product story is simple: fail releases when AI behavior regresses.

Teams can put Sentinel in CI, run a suite before shipping prompt, model, policy,
or provider changes, and keep exportable evidence that shows exactly what
changed.

Personal, research, nonprofit, evaluation, community, and small-business use is
welcome under the community license. Large commercial integrations require
permission. See `COMMERCIAL_USE.md`.
