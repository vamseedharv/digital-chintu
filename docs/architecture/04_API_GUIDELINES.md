# 04 API Guidelines

Status: **one endpoint implemented** — conventions below are what that endpoint follows;
apply the same conventions as new endpoints are added.

## REST

- All routes are mounted under a versioned prefix, `/api/v1` (configurable via
  `API_V1_PREFIX`, but there's no reason to change it — it exists so a future
  `/api/v2` can be introduced without breaking `/v1` clients).
- Endpoint modules live in `backend/app/api/v1/endpoints/`, one file per
  resource, aggregated by `backend/app/api/v1/router.py`.
- Responses are plain JSON with `snake_case` keys (matches Python/Pydantic
  convention; see `docs/architecture/02_REPOSITORY_STRUCTURE.md` for the
  naming-consistency note about the frontend consuming this as-is).
- The current health endpoint (`GET /api/v1/health`) returns a bare
  `dict[str, str]` rather than a Pydantic `response_model`. That's fine for
  one endpoint with no real schema to document; the first endpoint with
  actual request/response validation needs should use a `response_model` so
  FastAPI's generated OpenAPI schema (`/openapi.json`) stays accurate (see
  [BACKLOG.md](../../BACKLOG.md)).
- CORS is restrictive by default (`CORS_ORIGINS`, comma-separated allow-list
  — no wildcard), configured in `backend/app/main.py`.

## WebSocket

Not implemented yet. When a feature needs real-time push (see
`docs/SDS/02_Backend/022_WebSockets.md`), register it alongside the REST
routes under `api/v1/` rather than as a separate top-level concern.

## Versioning

Only `v1` exists. Breaking changes to a shipped endpoint should go in a new
`v2` module rather than mutating `v1` in place, once there are real clients
depending on it (not a concern yet, at this stage).
