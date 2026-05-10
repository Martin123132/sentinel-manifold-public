# Deployment

Sentinel Manifold runs as a single Python web service with no required package dependencies.

## Local Production-Style Run

```powershell
$env:SENTINEL_API_KEY="dev-secret"
$env:SENTINEL_PUBLIC_DEMO="false"
$env:HOST="127.0.0.1"
$env:PORT="8787"
python app\server.py
```

Healthcheck:

```powershell
Invoke-RestMethod http://127.0.0.1:8787/api/health
```

Authenticated check:

```powershell
$headers = @{ Authorization = "Bearer dev-secret" }
Invoke-RestMethod http://127.0.0.1:8787/api/providers -Headers $headers
```

## Docker

```powershell
docker build -t sentinel-manifold .
docker run --rm -p 8787:8787 -e SENTINEL_API_KEY=dev-secret sentinel-manifold
```

Open:

```text
http://127.0.0.1:8787
```

Enter `dev-secret` in the dashboard API key field.

## Public Demo Run

Use public demo mode for a hosted sandbox that visitors can try without an API
key:

```powershell
$env:SENTINEL_PUBLIC_DEMO="true"
$env:SENTINEL_API_KEY="admin-secret"
$env:HOST="0.0.0.0"
$env:PORT="8787"
python app\server.py
```

Unauthenticated visitors can run only bounded local demo checks and the bundled
release suite. Audit history, evidence pack downloads, hosted provider
generation, and `/v1/chat/completions` remain protected by `SENTINEL_API_KEY`.

Do not set provider credentials such as `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`,
or `GEMINI_API_KEY` on a public demo unless the deployment is otherwise locked
down for admin-only use.

## Render Blueprint

The repo includes `render.yaml` for a Git-backed Render Blueprint. The community
blueprint defaults to public sandbox mode:

```text
SENTINEL_PUBLIC_DEMO=true
```

1. Push the repo to GitHub.
2. In Render, create a new Blueprint from the repository.
3. Render will generate `SENTINEL_API_KEY`.
4. Open the deployed app to confirm unauthenticated visitors see the public sandbox.
5. Keep the generated `SENTINEL_API_KEY` for admin-only checks.

Do not store real customer data or provider secrets in the public demo service.

The healthcheck path is public:

```text
/api/health
```

Protected routes require `Authorization: Bearer <SENTINEL_API_KEY>` or `X-API-Key`.

Optional provider credentials such as `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, and `GEMINI_API_KEY` should be added as Render secret environment variables when those adapters are enabled.
