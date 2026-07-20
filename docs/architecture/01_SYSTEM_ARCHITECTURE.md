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
| HTTP interface | `api/v1/` | `router.py` aggregates endpoint routers: `endpoints/health.py` (liveness) and `endpoints/config.py` (read-only runtime configuration) |
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
- `components/ui/` — presentational primitives (`Button`, `LinkButton`,
  `Card`, `Spinner`, `Skeleton`, `EmptyState`, `Heading`, `Text`) that take
  state via props rather than fetching themselves.
- `components/layout/` — `Sidebar` (desktop nav), `MobileNav` (drawer nav,
  focus-trapped), `NavLinks` (shared by both so they can't drift out of
  sync), `PageContainer`.
- `components/` (top level) — feature components composed from the above
  primitives, e.g. `HealthStatus`, `ThemeToggle`.
- `app/` — the composition root: `AppShell.tsx` (sidebar/drawer layout,
  skip-to-content link, header), `router.tsx` (`react-router` route table),
  `navigation.ts` (nav item list, consumed by `NavLinks`).
- `routes/` — page components rendered by the router: `HomePage`,
  `NotFoundPage` (404), `ErrorPage` (route-level error boundary).
- `main.tsx` — mounts `RouterProvider` wrapped in `ThemeProvider` and
  `<MotionConfig reducedMotion="user">`; the header name and document title
  are driven by the backend's `app_name` (fetched via `useHealth` inside
  `AppShell`), not hardcoded.

The frontend's own import direction (`app`/`routes` → `components/layout` →
`components/ui` → `api`/`theme`) is enforced the same way the backend's is —
see "Known gaps" below.

## Configuration flow

Every runtime setting is an environment variable, typed and validated by a
single `pydantic-settings` model (`Settings` in `backend/app/core/config.py`),
read once and cached process-wide (`@lru_cache def get_settings()`). Native
dev reads `backend/.env`; Docker Compose passes variables through from the
repo-root `.env` (see `docker-compose.yml`). This is "runtime configuration"
in the sense that matters here: values are resolved when the process starts
from its environment, not baked in at build time (contrast the frontend's
`VITE_*` vars, inlined at build) — there is no hot-reload or live write API
yet, that's a separate, not-yet-started feature
([008_Settings](../features/008_Settings.md)).

Settings today:

| Setting | Env var | Type | Notes |
|---|---|---|---|
| App/assistant name | `APP_NAME` | `str` | Non-blank, ≤64 chars. Never hardcoded — flows to `/api/v1/health` and `/api/v1/config`, then the frontend header/tab title. |
| Environment profile | `APP_ENV` | `Environment` enum (`development`/`testing`/`production`) | Rejects unknown values. `production` + `debug=true` together is a validation error, not just a bad default. |
| Debug mode | `DEBUG` | `bool` | Defaults `False` regardless of profile — see [06_SECURITY.md](06_SECURITY.md). |
| Wake word | `WAKE_WORD` | `str` | Non-blank, ≤64 chars. Config value only — no wake-word *detection* engine yet ([011_Wake_Word](../features/011_Wake_Word.md)). |
| Default theme | `DEFAULT_THEME` | `Theme` enum (`light`/`dark`/`system`) | The system-wide default before any per-user override; the frontend's own `ThemeProvider` persists a separate per-browser choice to `localStorage`. |
| Default language | `DEFAULT_LANGUAGE` | `str` | Validated as a BCP-47-style tag (`en`, `en-US`, `hi-IN`) — format only, no actual translation/i18n yet ([032_Multilingual](../features/032_Multilingual.md)). |
| CORS origins, log level/dir, DB URL, API prefix | see `.env.example` | — | Unchanged infrastructure settings. |

`GET /api/v1/config` exposes the non-secret subset of the above (app name,
wake word, default theme, default language, environment) — the same role
`/api/v1/health` already played for just `app_name`, generalized now that
there's more than one client-relevant setting. Both are read-only; neither
lets a client change a setting (that's still 008's gap to close, likely with
its own DB-backed override on top of these env-driven defaults).

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
