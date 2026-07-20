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
  services      <- application logic (settings; otherwise empty)
  repositories  <- data access (settings; otherwise empty)
  domain        <- entities/interfaces (settings; otherwise empty)
  db            <- SQLAlchemy engine/session/models
        |
        v
  SQLite file, migrated with Alembic (backend/alembic/)

frontend-mobile   -- placeholder only, framework not chosen (see its README)
plugins           -- extension point implemented (core/plugins.py); no real plugin dropped in yet
WebSocket API     -- not registered yet; add under api/v1/ when a feature needs push updates
```

Both `frontend-dashboard` and `backend` also run as Docker containers, wired
together by the root `docker-compose.yml` (see [07_DEPLOYMENT.md](07_DEPLOYMENT.md)).

## Backend — Clean Architecture layering

`backend/app/` is organized so each layer only depends on the layer(s) below
it (no compiled/CI-enforced boundary yet — see "Known gaps" below):

| Layer | Path | Today |
|---|---|---|
| HTTP interface | `api/v1/` | `router.py` aggregates endpoint routers: `health.py` (liveness), `config.py` (read-only runtime configuration), `settings.py` (read/write settings), `plugins.py` (plugin introspection), `wake_word.py` (wake-word status + push-to-talk trigger). `deps.py` holds shared dependency providers (`get_settings_service`). |
| Cross-cutting | `core/` | `config.py` (pydantic-settings, env-driven), `logging.py` (console + rotating file handler), `scheduler.py` (APScheduler instance, started/stopped via the app's lifespan, no jobs registered yet), `plugins.py` (discovery, `Plugin` contract, dynamic router registration — see [05_PLUGIN_SDK.md](05_PLUGIN_SDK.md)), `voice/` (`011_Wake_Word`: `events.py`/`audio.py`/`engine.py`/`runtime.py` — an opt-in OpenWakeWord integration that always degrades gracefully; see [docs/features/011_Wake_Word.md](../features/011_Wake_Word.md)), `validation.py` (small validators shared across Pydantic models) |
| Application logic | `services/` | `settings_service.py` — resolves each managed setting's effective value (DB override or env default) and validates new values (`008_Settings`) |
| Data access | `repositories/` | `settings_repository.py` — plain key/value reads and writes against the `settings` table |
| Domain | `domain/` | `settings.py` — `SettingKey` (`app_name`, `default_theme`, `onboarding_complete`, `wake_word_enabled`), `EffectiveSettings` |
| Infrastructure | `db/` | `base.py` (SQLAlchemy `DeclarativeBase`), `session.py` (engine/session factory, `get_db()` FastAPI dependency), `models.py` (`SettingModel`) |

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
- `components/dashboard/` — `WidgetCard` (shared tile shell) and the
  widgets built on it (`GreetingWidget`, `ClockWidget`,
  `PlaceholderWidget`) for the Dashboard route.
- `app/` — the composition root: `AppShell.tsx` (sidebar/drawer layout,
  skip-to-content link, header), `router.tsx` (`react-router` route table),
  `navigation.ts` (nav item list, consumed by `NavLinks`).
- `routes/` — page components rendered by the router: `DashboardPage` (the
  widget-hosting home screen — see [09_UI_DESIGN_SYSTEM.md](09_UI_DESIGN_SYSTEM.md)),
  `SettingsPage`, `OnboardingPage` (`009_Assistant_Onboarding` — a full-screen
  wizard, a sibling of `AppShell` in the route tree rather than one of its
  children, so it renders without sidebar/nav chrome), `NotFoundPage` (404),
  `ErrorPage` (route-level error boundary).
- `main.tsx` — mounts `RouterProvider` wrapped in `ThemeProvider` and
  `<MotionConfig reducedMotion="user">`; the header name and document title
  are driven by the backend's `app_name` (fetched via `useHealth` inside
  `AppShell`), not hardcoded.

`AppShell` also gates every route it wraps: it fetches settings
(`useSettings`) and redirects to `/onboarding` whenever `onboarding_complete`
is `false`, once that fetch actually resolves (never mid-loading, never on a
fetch error — see `app/AppShell.tsx`). `/onboarding` itself is never gated,
so it stays reachable after completion too (a "Run setup again" link on the
Settings page points there) — not a one-time irreversible flow.

The frontend's own import direction (`app`/`routes` → `components/layout` →
`components/ui` → `api`/`theme`) is enforced the same way the backend's is —
see "Known gaps" below.

## Configuration flow

Every runtime setting starts as an environment variable, typed and
validated by a single `pydantic-settings` model (`Settings` in
`backend/app/core/config.py`), read once and cached process-wide
(`@lru_cache def get_settings()`). Native dev reads `backend/.env`; Docker
Compose passes variables through from the repo-root `.env` (see
`docker-compose.yml`). Values are resolved when the process starts from its
environment, not baked in at build time (contrast the frontend's `VITE_*`
vars, inlined at build).

Three of these (`app_name`, `default_theme`, and now `wake_word`) also have
a DB-backed override layer on top (`008_Settings`, see
[03_DATABASE_DESIGN.md](03_DATABASE_DESIGN.md)): `app/services/settings_service.py`
resolves the *effective* value — the override if one exists, else the env
default — and every endpoint that reports these values
(`/health`, `/config`, `/settings`) reads through that same resolution, so
they can't disagree with each other. `PATCH /api/v1/settings` is the write
path; there's still no hot-reload of the underlying env vars themselves,
only of the settings this override layer manages.

Settings today:

| Setting | Env var | Type | Notes |
|---|---|---|---|
| App/assistant name | `APP_NAME` | `str` | Non-blank, ≤64 chars. Never hardcoded — flows to `/api/v1/health` and `/api/v1/config`, then the frontend header/tab title. **Now writable at runtime** via `PATCH /api/v1/settings` (env var is just the default before any override). |
| Environment profile | `APP_ENV` | `Environment` enum (`development`/`testing`/`production`) | Rejects unknown values. `production` + `debug=true` together is a validation error, not just a bad default. |
| Debug mode | `DEBUG` | `bool` | Defaults `False` regardless of profile — see [06_SECURITY.md](06_SECURITY.md). |
| Wake phrase | `WAKE_WORD` | `str \| None` | Optional exact-phrase pin. Left unset (default), the *effective* value reported by `/config`/`/settings` is derived as `"Hey {app_name}"` instead — see [011_Wake_Word](../features/011_Wake_Word.md). Decoupled from *which acoustic model* listens (`WAKE_WORD_MODEL`, env-only — OpenWakeWord's pretrained models don't include arbitrary names). |
| Default theme | `DEFAULT_THEME` | `Theme` enum (`light`/`dark`/`system`) | The system-wide default before any per-user override. **Now writable at runtime** via `PATCH /api/v1/settings` — but the frontend's `ThemeProvider` doesn't consume it yet (only `localStorage`/OS preference), a known gap tracked in [BACKLOG.md](../../BACKLOG.md). |
| Default language | `DEFAULT_LANGUAGE` | `str` | Validated as a BCP-47-style tag (`en`, `en-US`, `hi-IN`) — format only, no actual translation/i18n yet ([032_Multilingual](../features/032_Multilingual.md)). Env-only; not managed by 008_Settings. |
| Wake-word model, sensitivity, pre-roll, audio device | `WAKE_WORD_MODEL`, `WAKE_WORD_SENSITIVITY`, `WAKE_WORD_PREROLL_SECONDS`, `VOICE_AUDIO_DEVICE` | see `.env.example` | Deployment-level knobs for `011_Wake_Word`'s opt-in detection engine — env-only, same tier as `PLUGINS_DIR`. |
| CORS origins, log level/dir, DB URL, API prefix | see `.env.example` | — | Unchanged infrastructure settings. |

`GET /api/v1/config` exposes the non-secret subset of the above (app name,
wake word, default theme, default language, environment) — the same role
`/api/v1/health` already played for just `app_name`, generalized now that
there's more than one client-relevant setting. `app_name`, `default_theme`,
and `wake_word` reflect any DB-backed override; `default_language` is still
purely env-driven. `GET`/`PATCH /api/v1/settings` (`008_Settings`) is the
dedicated read/write surface for the managed settings — see
[03_DATABASE_DESIGN.md](03_DATABASE_DESIGN.md).

The settings domain also manages two keys with no env-var counterpart at
all: `onboarding_complete` (`009_Assistant_Onboarding`), a bool defaulting
to `false` until explicitly set, and `wake_word_enabled`
(`011_Wake_Word`), a bool defaulting to `true` gating the wake-word
runtime's always-on listening (read once at startup, not hot-reloaded —
see `docs/features/011_Wake_Word.md`). Neither is in the table above
because there's no "env-driven default" concept for either, only the DB
override. `GET /api/v1/config`/`GET /api/v1/health` don't expose either
(only `GET /api/v1/settings` does); `onboarding_complete` is read purely by
`AppShell`'s onboarding-redirect gate.

## Known gaps (intentional, tracked for later features)

- No WebSocket endpoint yet — the transport exists in FastAPI/Starlette but
  nothing is registered. Add under `api/v1/` when a feature needs real-time
  push (e.g. notifications, live device state).
- ~~No database models/migrations~~ — **closed**: `008_Settings` introduced
  the first model (`SettingModel`, `db/models.py`) and Alembic together
  (`backend/alembic/`) — see [03_DATABASE_DESIGN.md](03_DATABASE_DESIGN.md)
  for why this happened ahead of the originally-planned Phase 4.
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
- Plugin engine — **closed**: `backend/app/core/plugins.py` provides
  discovery, the `Plugin` contract, and dynamic router registration (see
  [05_PLUGIN_SDK.md](05_PLUGIN_SDK.md)); `plugins/` itself still has no
  real plugin dropped into it.
- Mobile client (`frontend-mobile/`) is a reserved path only — see its own
  `README.md`.

## Cross-platform

Both Dockerfiles use multi-arch base images (`python:3.12-slim`,
`node:22-alpine`, `nginx:alpine`), so the same `docker-compose.yml` runs
unmodified on Raspberry Pi (arm64/armv7), Linux, and Windows (Docker
Desktop). Native (non-Docker) dev is supported the same way on all three via
`scripts/setup.sh` / `scripts/setup.ps1`.
