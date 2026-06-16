# v0.1.6 Suite Catalog

Draft release notes for the next milestone. Do not publish this tag yet.

Sentinel Manifold `v0.1.6 Suite Catalog` packages the next adoption layer after
the Suite Authoring Kit: ready-made buyer starter packs for common first use
cases.

## Product Proof

The product story stays the same:

> Fail releases when AI behavior regresses.

This release candidate makes that proof easier to adapt:

- choose the closest buyer starter pack,
- validate it with the suite validator,
- replace references and candidates with your own wording,
- run it locally and in CI,
- collect catalog suite reports as release-gate artifacts.

## What Is New

- `docs/suite-catalog.md`
- `samples/catalog/support-operations-suite.json`
- `samples/catalog/regulated-approval-suite.json`
- `samples/catalog/research-claims-suite.json`
- `samples/catalog/code-review-release-suite.json`
- `samples/catalog/agent-tool-boundary-suite.json`
- catalog suite validation in CI
- catalog suite reports in the `sentinel-release-gate` artifact
- tests proving every catalog pack validates and passes

## Try It

```powershell
python scripts\validate-suite.py --run samples\catalog\support-operations-suite.json
python app\cli.py suite --input samples\catalog\support-operations-suite.json --out out\catalog-support-operations-suite-report.json --fail-on-fail
```

For the full catalog:

```text
docs/suite-catalog.md
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
