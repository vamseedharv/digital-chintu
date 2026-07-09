# 01 System Architecture

Status: **Project Setup implemented** (see [docs/features/001_Project_Setup.md](../features/001_Project_Setup.md)). This
describes what's actually running today, with what's still planned called out explicitly.
See [PROJECT_STATUS.md](../../PROJECT_STATUS.md) for the current snapshot,
[ROADMAP.md](../../ROADMAP.md) for what's next, and
[DEPENDENCY_GRAPH.md](../../DEPENDENCY_GRAPH.md) for the full internal/external
dependency picture.

## Overview

```
frontend-dashboard (React + Vite, browser)
        |
        |  REST, JSON, CORS-restricted origin
        v
backend (FastAPI)
  api/v1        <- HTTP routes (router.py + endpoints/)
  core          <- config (pydantic-settings) + logging, used by every layer
  services      <- application logic (empty: no feature needs it yet)
  repositories  <- data access (empty: no feature needs it yet)
  domain        <- entities/interfaces (empty: no feature needs it yet)
  db            <- SQLAlchemy engine/session (no models yet)
        |
        v
  SQLite file (single file, no migrations yet)

frontend-mobile   -- placeholder only, framework not chosen (see its README)
plugins           -- placeholder only, plugin engine not started
WebSocket API     -- not registered yet; add under api/v1/ when a feature needs push updates
```

Both `frontend-dashboard` and `backend` also run as Docker containers, wired
together by the root `docker-compose.yml` (see [07_DEPLOYMENT.md](07_DEPLOYMENT.md)).

## Backend — Clean Architecture layering

`backend/app/` is organized so each layer only depends on the layer(s) below
it (no compiled/CI-enforced boundary yet — see "Known gaps" below):

| Layer | Path | Today |
|---|---|---|
| HTTP interface | `api/v1/` | `router.py` aggregates endpoint routers; one endpoint (`endpoints/health.py`) exists |
| Cross-cutting | `core/` | `config.py` (pydantic-settings, env-driven), `logging.py` (console + rotating file handler), `scheduler.py` (APScheduler instance, started/stopped via the app's lifespan, no jobs registered yet) |
| Application logic | `services/` | Empty — no feature has needed business logic yet |
| Data access | `repositories/` | Empty — no feature has needed persistence yet |
| Domain | `domain/` | Empty — no entities defined yet |
| Infrastructure | `db/` | `base.py` (SQLAlchemy `DeclarativeBase`), `session.py` (engine/session factory, `get_db()` FastAPI dependency) |

The app factory (`app/main.py`) wires config, logging, CORS middleware, the
`/api/v1` router, and the scheduler's start/stop (via a `lifespan` context
manager) together, and is the single entrypoint (`uvicorn app.main:app`).

## Frontend — composition

`frontend-dashboard/src/`:

- `theme/` — `ThemeProvider` + `useTheme`, class-based dark/light toggle
  persisted to `localStorage`, defaults to OS `prefers-color-scheme`.
- `api/` — `client.ts` (fetch wrapper + `ApiError`), `health.ts` (typed call),
  `useHealth.ts` (hook: loading/success/error state machine).
- `components/` — presentational components (`HealthStatus`, `ThemeToggle`)
  that receive state via props/context rather than fetching themselves.
- `App.tsx` — composes the above; the header name and document title are
  driven by the backend's `app_name` (fetched via `useHealth`), not hardcoded.

## Configuration flow

Every runtime setting is an environment variable, read once via
`pydantic-settings` (`backend/app/core/config.py`) and cached
(`@lru_cache`). Native dev reads `backend/.env`; Docker Compose passes
variables through from the repo-root `.env` (see `docker-compose.yml`). The
same mechanism is how `APP_NAME` (the assistant's display name) stays
runtime-configurable end-to-end: backend env var → `/api/v1/health` response
→ frontend header/tab title (never hardcoded on the frontend).

## Known gaps (intentional, tracked for later features)

- No WebSocket endpoint yet — the transport exists in FastAPI/Starlette but
  nothing is registered. Add under `api/v1/` when a feature needs real-time
  push (e.g. notifications, live device state).
- No database models/migrations — `db/` only has engine/session scaffolding.
  Alembic should be introduced with the *first* model, not before.
- ~~No import-boundary enforcement between layers~~ — **closed**: `import-linter`
  enforces `api -> services -> repositories -> domain` (one-way) via a
  `layers` contract in `backend/pyproject.toml`, run in CI and `make lint`.
  `core`/`db` are deliberately excluded from the ordering (cross-cutting
  infrastructure, importable by any layer).
- ~~No import-boundary enforcement on the frontend~~ — **closed**: ESLint's
  `import/no-restricted-paths` (`frontend-dashboard/eslint.config.js`) stops
  `src/api` and `src/theme` (cross-cutting, like backend's `core`/`db`) from
  importing `src/components`, `src/routes`, or `src/app` — the direction
  those UI layers already depended on by convention, now enforced in
  `make lint`.
- Plugin engine (`plugins/`) and mobile client (`frontend-mobile/`) are
  reserved paths only — see their own `README.md`. See
  [BACKLOG.md](../../BACKLOG.md) for what a plugin extension point needs
  before `010_Plugin_Framework` can start.

## Cross-platform

Both Dockerfiles use multi-arch base images (`python:3.12-slim`,
`node:22-alpine`, `nginx:alpine`), so the same `docker-compose.yml` runs
unmodified on Raspberry Pi (arm64/armv7), Linux, and Windows (Docker
Desktop). Native (non-Docker) dev is supported the same way on all three via
`scripts/setup.sh` / `scripts/setup.ps1`.
