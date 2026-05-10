# Security

Sentinel Manifold is local-first by default. Hosted deployments should set `SENTINEL_API_KEY`.

Public demo deployments may also set `SENTINEL_PUBLIC_DEMO=true` to expose only
a bounded sandbox while keeping admin routes protected.

## API Authentication

When `SENTINEL_API_KEY` is unset, auth is disabled for local development.

When `SENTINEL_API_KEY` is set, protected routes require one of:

```text
Authorization: Bearer <SENTINEL_API_KEY>
X-API-Key: <SENTINEL_API_KEY>
```

Public route:

```text
GET /api/health
```

Additional unauthenticated routes when `SENTINEL_PUBLIC_DEMO=true`:

```text
GET  /api/demo
GET  /api/demo-suite
GET  /api/policies
GET  /api/providers
POST /api/check
POST /api/suite
```

Public demo responses use the local demo provider only and do not persist
evidence packs for unauthenticated requests.

Protected routes:

```text
GET  /api/demo
GET  /api/policies
GET  /api/providers
GET  /api/audits
GET  /api/audits/{check_id}
GET  /api/audits/{check_id}/verify
POST /api/check
POST /api/generate-check
POST /api/suite
POST /v1/chat/completions
```

## Evidence Packs

Evidence packs are written under `out/audits` and are excluded from Git by `.gitignore`.

Do not commit evidence packs from real customer traffic. They may contain prompts, references, model outputs, and policy data.

## Provider Keys

`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, and `GEMINI_API_KEY` are only needed when using their matching hosted provider adapters. Keep provider credentials server-side.

The dashboard stores the Sentinel API key in browser `sessionStorage` so a refresh keeps the local session unlocked without persisting the key permanently.
