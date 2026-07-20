# Dependency Graph

Two things, both verified against the actual code (grepped, not assumed) as
of 2026-07-09: internal module dependencies (what's enforced by
`import-linter`) and external package dependencies (what's installed).

## Internal — backend (`backend/app/`)

```
app.main
  -> app.api.v1.router
  -> app.core.config
  -> app.core.logging
  -> app.core.scheduler

app.api.v1.router
  -> app.api.v1.endpoints.health
  -> app.api.v1.endpoints.config

app.api.v1.endpoints.health
  -> app.core.config

app.api.v1.endpoints.config
  -> app.core.config

app.db.session
  -> app.core.config

app.core.logging
  -> app.core.config

app.core.scheduler
  -> (no internal imports — apscheduler only)

app.domain, app.services, app.repositories
  -> (empty — no imports yet)
```

**Enforced direction**: `api -> services -> repositories -> domain`, one-way,
via `import-linter` (`backend/pyproject.toml`'s `[tool.importlinter]`), run
in CI and `make lint`. `core` and `db` are deliberately excluded from that
ordering — cross-cutting infrastructure, importable by any layer. Verified
this contract actually fails on a real violation (tested, then reverted) —
see `docs/architecture/01_SYSTEM_ARCHITECTURE.md`.

## Internal — frontend (`frontend-dashboard/src/`)

```
App.tsx
  -> api/useHealth (hook)
  -> components/HealthStatus
  -> components/ThemeToggle

components/HealthStatus
  -> api/useHealth (type only: HealthState)

components/ThemeToggle
  -> theme/useTheme

theme/ThemeProvider
  -> theme/ThemeContext

theme/useTheme
  -> theme/ThemeContext

api/useHealth
  -> api/health

api/health
  -> api/client
```

**Enforced direction**: ESLint's `import/no-restricted-paths`
(`frontend-dashboard/eslint.config.js`) mirrors the backend's `import-linter`
— `src/api` and `src/theme` (cross-cutting infrastructure, like backend's
`core`/`db`) cannot import from `src/components`, `src/routes`, or `src/app`,
run in `make lint`. Requires the `import/resolver` `node` setting with
`.ts`/`.tsx` extensions explicitly listed — without it the rule silently
never fires, since the default resolver can't resolve TS imports at all.

## External — backend (`backend/pyproject.toml`)

| Package | Version constraint | Purpose |
|---|---|---|
| fastapi | `>=0.115,<1.0` | Web framework |
| uvicorn[standard] | `>=0.32,<1.0` | ASGI server |
| pydantic | `>=2.9,<3.0` | Data validation (FastAPI dependency) |
| pydantic-settings | `>=2.5,<3.0` | Env-var-driven config (`core/config.py`) |
| sqlalchemy | `>=2.0,<3.0` | ORM / DB engine (`db/`) |
| apscheduler | `>=3.10,<4.0` | Background job scheduler (`core/scheduler.py`), no jobs yet |

Dev-only (`[project.optional-dependencies].dev`):

| Package | Purpose |
|---|---|
| pytest, pytest-cov | Test runner + coverage |
| httpx | Required by FastAPI's `TestClient` |
| ruff | Linting |
| black | Formatting |
| mypy | Strict type-checking |
| import-linter | Architecture-boundary enforcement (see above) |

## External — frontend (`frontend-dashboard/package.json`)

| Package | Purpose |
|---|---|
| react, react-dom | UI framework |
| framer-motion | Animation (health card, theme toggle transitions) |

Dev-only:

| Package | Purpose |
|---|---|
| vite, @vitejs/plugin-react | Build/dev server |
| typescript | Type-checking |
| tailwindcss, @tailwindcss/vite | Styling |
| eslint, @eslint/js, typescript-eslint, eslint-plugin-react-hooks, eslint-plugin-react-refresh, eslint-plugin-import, eslint-config-prettier | Linting |
| prettier | Formatting |
| vitest, @vitest/coverage-v8, jsdom | Unit/integration testing |
| @testing-library/react, @testing-library/jest-dom, @testing-library/user-event | Component testing utilities |

## External — E2E (`tests/package.json`)

| Package | Purpose |
|---|---|
| @playwright/test | Browser-driven E2E testing, spans both services |

## Cross-package dependency (deliberately absent)

`frontend-dashboard` and `backend` share **no code** today — `shared/` is
reserved for this but empty. The only coupling is the REST contract itself
(`GET /api/v1/health`'s JSON shape, hand-copied into
`frontend-dashboard/src/api/health.ts`'s `HealthResponse` interface). See
[BACKLOG.md](BACKLOG.md) for when to revisit this (OpenAPI-generated client,
once a second client exists).

## Not yet covered

No dependency-vulnerability scanning (`pip-audit`, `npm audit` in CI, or
similar) exists yet — see [BACKLOG.md](BACKLOG.md).
