# Contributing

Sentinel Manifold is dependency-light by design. Before opening a pull request, run the same checks used by CI:

```powershell
python -m unittest discover -s tests
python -m compileall app
node --check web\app.js
python app\cli.py suite --input samples\regression-suite.json --out out\suite-report.json --fail-on-fail
powershell -ExecutionPolicy Bypass -File .\scripts\docker-smoke.ps1 -RunSuite
powershell -ExecutionPolicy Bypass -File .\scripts\docker-smoke.ps1 -RunSuite -PublicDemo -HostPort 8789
```

Provider adapter tests mock outbound HTTP calls, so live provider API keys are not required for the test suite.

The Docker smoke script builds the image, runs the container with `SENTINEL_API_KEY`, checks `/api/health`, verifies unauthenticated API calls return 401, verifies bearer-authenticated provider discovery, optionally runs the demo regression suite, and removes the container. With `-PublicDemo`, it also verifies the unauthenticated sandbox provider list, audit-route lockout, and non-persistent suite evidence behavior.

## Contribution Rules

By contributing, you certify that you have the right to submit the work under
the repository license and that you agree for it to be distributed under
the Sentinel Manifold Community License in `LICENSE`.

Use a Developer Certificate of Origin style sign-off on commits when practical:

```text
Signed-off-by: Your Name <you@example.com>
```

Do not include secrets, real customer prompts, private evidence packs, provider
API keys, private deployment files, hardware designs, unreleased research notes,
or third-party code that cannot be distributed under the repository license in
pull requests.

The code license does not grant rights to Sentinel Manifold names, logos, marks,
or product identity. See `TRADEMARKS.md`.

If Docker Desktop is installed but stuck in `starting`, check Docker Desktop for first-run prompts. If it reports that WSL needs an update, run `wsl --update` from an elevated PowerShell. On older Windows WSL installs where `wsl --update` is unavailable, run `wsl --install --no-distribution --web-download`, restart Windows if prompted, then reopen Docker Desktop.
