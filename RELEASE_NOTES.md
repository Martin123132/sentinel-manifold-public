# v0.1.5 Suite Authoring Kit

Draft release notes for the next candidate. Do not publish this tag yet.

Sentinel Manifold `v0.1.5 Suite Authoring Kit` focuses on the next adoption
friction point: helping a trial user write their first release-gate suite and
see one worked example from policy text to CI report.

## Product Proof

The product story stays the same:

> Fail releases when AI behavior regresses.

This candidate adds the authoring path around that proof:

- copy a runnable template,
- validate the suite shape,
- run it locally,
- inspect a worked custom-suite walkthrough,
- move the same suite into CI when it behaves as expected.

## What Is New

- `docs/suite-authoring.md`
- `scripts/validate-suite.py`
- `samples/templates/support-suite-template.json`
- `samples/templates/regulated-suite-template.json`
- `samples/templates/research-suite-template.json`
- `samples/templates/code-review-suite-template.json`
- `samples/templates/agent-tool-suite-template.json`
- `docs/first-custom-suite.md`
- `samples/first-custom-suite.json`
- validator and template tests
- CI validation for all suite templates and the first custom suite
- `docs/launch/v0.1.5-suite-authoring-checklist.md`

## Try It

```powershell
copy samples\templates\support-suite-template.json samples\my-suite.json
python scripts\validate-suite.py --run samples\my-suite.json
python app\cli.py suite --input samples\my-suite.json --out out\my-suite-report.json --fail-on-fail
```

For the full authoring path and the worked example:

```text
docs/suite-authoring.md
docs/first-custom-suite.md
```

## Boundaries

- No API changes.
- No CLI behavior changes.
- No dashboard/runtime changes.
- No provider keys.
- No public audit history.
- Public sandbox behavior remains unchanged.

Personal, research, nonprofit, evaluation, community, and small-business use
remains welcome. Larger commercial integration remains subject to commercial
boundary terms.

See `LICENSE`, `COMMERCIAL_USE.md`, and `TRADEMARKS.md`.
