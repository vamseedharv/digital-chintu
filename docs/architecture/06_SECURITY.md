# 06 Security

Status: baseline decisions made during Project Setup; no auth/secrets-management
feature exists yet (nothing today requires a user account or API key).

## Decisions made so far

- **`debug` defaults to `False`** (`backend/app/core/config.py`). An
  unconfigured deployment (no `.env` present) will not leak verbose FastAPI
  tracebacks. Local dev opts into `DEBUG=true` explicitly via
  `backend/.env.example`.
- **CORS is an explicit allow-list**, never a wildcard
  (`CORS_ORIGINS`, comma-separated). Verified by an integration test that
  asserts an unconfigured origin does *not* get an
  `Access-Control-Allow-Origin` header back.
- **Docker images run as non-root**: `backend`'s image creates and switches
  to a `chintu` user before serving traffic; only build steps run as root.
- **No secrets are committed**: `.gitignore` excludes `.env`/`.env.*`
  (keeping `!.env.example`), and every `.env.example` contains only
  non-sensitive defaults.
- **`.dockerignore`** on both services keeps `.env`, `.venv`, and
  `node_modules` out of the build context (defense in depth — even though
  `.env` was never expected there, an explicit exclusion is cheap insurance).

## Not implemented yet

- No authentication/authorization on any endpoint — everything under
  `/api/v1` is unauthenticated. Add this before any feature exposes
  sensitive data or write operations.
- No rate limiting, no HTTPS termination (expected to be handled by
  whatever reverse proxy sits in front of this in a real deployment — not
  yet documented here since no deployment guide beyond Docker Compose exists).
- No dependency-vulnerability scanning wired into CI yet.

Revisit this document as soon as the first feature introduces user accounts,
API tokens, or handles data that needs encryption at rest.
