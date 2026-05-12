# Support Assistant Adoption Proof

This fixture shows how another team could copy Sentinel into a product repo and
use it as a CI release gate.

Scenario: a customer-support assistant is about to ship. The team has trusted
policy references for refunds, escalation, quality claims, and agent tool
limits. Sentinel runs those references against candidate AI outputs and fails the
release if the assistant drifts from policy.

Run the fixture from the Sentinel repo root:

```powershell
python app\cli.py suite --input examples\external-adoption\support-assistant\sentinel-suite.json --out out\external-adoption-suite-report.json --fail-on-fail
```

Expected result:

- `PASS`
- `5` cases
- `5` passed
- `0` failed

The companion `sentinel-release-gate.yml` file shows the GitHub Actions job a
separate repo would use after vendoring Sentinel's `app/`, `tests/`, and this
suite.

Product proof:

> A support-assistant repo can fail release when AI behavior drifts from policy.
