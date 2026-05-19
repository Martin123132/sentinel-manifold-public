# Evidence Reader Walkthrough

Admin evidence exports are designed for two audiences at once: humans who need
to understand the release-gate result quickly, and technical reviewers who want
the raw JSON and integrity checks.

Open the public
[support-assistant evidence example](../evidence-examples/support-assistant/README.md)
to inspect a complete sanitized bundle in the repo.

## Files In The Bundle

| File | What to read it for |
| --- | --- |
| `evidence-reader.md` | Start here. It explains the bundle, verdict, emitted vs blocked checks, policy profiles, integrity status, and where the raw files live. |
| `summary.md` | Executive verdict, proof snapshot, what the bundle proves, what it does not prove, and a compact audit table. |
| `manifest.json` | Machine-readable counts, verdict, policy profiles seen, newest and oldest checks, generated file list, and evidence paths. |
| `evidence/<check_id>.evidence.json` | The full saved check: references, candidates, selected output or block decision, findings, policy, provider, model, timestamps, and hashes. |
| `verification/<check_id>.verification.json` | Integrity verification for the evidence pack, including whether the saved digest and request hashes still match. |

## How To Read It

1. Open `evidence-reader.md` for the plain-English explanation.
2. Check `summary.md` for the executive verdict:
   - `Verified release-gate bundle` means exported evidence verified cleanly.
   - `Needs review` means at least one exported item failed verification.
   - `No evidence exported` means the bundle was valid but empty.
3. Open `manifest.json` if you need counts, policy profiles, file paths, or an
   automated way to parse the bundle.
4. Inspect individual files under `evidence/` when a blocked or emitted case
   needs detailed review.
5. Inspect matching files under `verification/` when you need to prove the saved
   evidence was not changed after export.

## What The Bundle Proves

The bundle proves that Sentinel evaluated saved candidate outputs against the
references supplied to those checks, made an emit or block decision, and exported
evidence that can be verified against recorded hashes.

## What It Does Not Prove

The bundle does not prove external facts, legal compliance, model quality in all
future situations, or correctness against references that were not supplied to
the check.

## How Admins Create It

1. Deploy or run Sentinel with `SENTINEL_API_KEY` set.
2. Unlock the dashboard with the admin key.
3. Run the demo suite or another saved suite.
4. Click **Export Bundle**.

Public sandbox visitors can run bounded demo checks, but they cannot read audit
history or export saved evidence.

Back to the [Proof Gallery](README.md).
