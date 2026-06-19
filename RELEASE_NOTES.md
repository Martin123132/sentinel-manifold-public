# v0.1.7 Catalog Evidence

Live release:
https://github.com/Martin123132/sentinel-manifold-public/releases/tag/v0.1.7

Sentinel Manifold `v0.1.7 Catalog Evidence` packages the proof layer after the
Suite Catalog: every buyer starter pack now has a static, inspectable evidence
example.

## Product Proof

The product story stays the same:

> Fail releases when AI behavior regresses.

This release makes that proof easier to trust:

- choose the closest buyer starter pack,
- inspect a checked-in evidence example for that pack,
- see the readable summary, manifest, suite report, evidence JSON, and
  verification JSON,
- then replace references and candidates with your own wording,
- run the same gate locally and in CI.

## What Is New

- `docs/evidence-examples/catalog/README.md`
- static evidence examples for all five Suite Catalog starter packs
- catalog pack README pages with buyer-shaped proof summaries
- `summary.md`, `evidence-reader.md`, `manifest.json`, `suite-report.json`,
  evidence JSON, and verification JSON for each catalog pack
- Suite Catalog links from each starter pack to its evidence example
- tests proving every catalog evidence pack is complete and integrity-verified

## Try It

```powershell
python scripts\validate-suite.py --run samples\catalog\*.json
python scripts\run-proof-pack.py --full
```

For the evidence examples:

```text
docs/evidence-examples/catalog/README.md
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
