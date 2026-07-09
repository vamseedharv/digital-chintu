# 02 Repository Structure

Status: **implemented** (see [docs/features/001_Project_Setup.md](../features/001_Project_Setup.md)).

## Layout

```
backend/               FastAPI backend
  app/
    main.py             app factory (entrypoint: app.main:app)
    api/v1/              routers + endpoints
    core/                config.py, logging.py
    domain/               empty — framework-independent entities (future)
    services/             empty — application logic (future)
    repositories/          empty — data access (future)
    db/                    SQLAlchemy engine/session, declarative base
  tests/
    unit/                 isolated tests of one module
    integration/           tests of the wired-up app via TestClient
  pyproject.toml         deps + tool config (ruff, black, mypy, pytest)
  Dockerfile, .dockerignore, .env.example, README.md

frontend-dashboard/    React + TypeScript + Vite + Tailwind web dashboard
  src/
    api/                  fetch client + typed calls + hooks
    components/            presentational UI components
    theme/                 dark/light ThemeProvider + useTheme
    __tests__/
      unit/                 one hook/component/module in isolation
      integration/           the composed App tree
  package.json, vite.config.ts, eslint.config.js, tsconfig*.json
  Dockerfile, .dockerignore, nginx.conf, .env.example, README.md

frontend-mobile/       placeholder — Android/iOS framework not yet chosen
shared/                placeholder — shared client types, populated once needed
plugins/               placeholder — plugin engine/implementations, not started
docker/                Docker workflow docs (Dockerfiles live per-service)
scripts/               cross-platform dev bootstrap (setup.sh, setup.ps1)
tests/                 cross-cutting Playwright E2E suite (spans both services)
docs/                  specifications (Foundation, SDS, features, architecture, guides — this tree)

Makefile               common tasks: setup, backend-dev, frontend-dev, lint, format, test, docker-up/down
docker-compose.yml     runs backend + frontend-dashboard together
.env.example           root-level: docker-compose config only
.github/workflows/     CI (backend on Linux+Windows, frontend on Linux)
```

## Why each package boundary exists

- **`backend/` vs `frontend-dashboard/` vs `frontend-mobile/`**: independent
  deployables with independent toolchains (pip vs npm), each with its own
  `Dockerfile` and lockfile. Nothing shared between them yet — that's what
  `shared/` is reserved for.
- **`domain/` / `services/` / `repositories/` / `db/`** inside `backend/app/`:
  Clean Architecture layers, kept as separate empty packages (rather than
  added later) so the first real feature has an unambiguous, pre-agreed
  place to land instead of prompting a restructuring decision mid-feature.
- **`tests/unit/` vs `tests/integration/`** (both backend and frontend): unit
  tests isolate one module (mock/monkeypatch its dependencies); integration
  tests exercise the real app wiring (`TestClient(create_app())`, or the full
  composed React tree) without mocking internals. The root-level `tests/`
  folder is a third, broader tier — Playwright E2E across both services —
  intentionally not merged into either package so it's clear it spans them.
- **`docker/`**: holds only documentation. Each service's own `Dockerfile`
  stays next to that service's source so its build context is minimal (see
  [07_DEPLOYMENT.md](07_DEPLOYMENT.md)) and each service's `.dockerignore`
  travels with it.

## Naming conventions in use today

| | Convention | Example |
|---|---|---|
| Python modules/files | `snake_case` | `app/core/config.py` |
| Python packages | `snake_case`, no plural | `app/api/`, `app/db/` |
| TypeScript files (components) | `PascalCase.tsx` | `HealthStatus.tsx` |
| TypeScript files (non-component) | `camelCase.ts` | `client.ts`, `useHealth.ts` |
| React hooks | `use` prefix | `useHealth`, `useTheme` |
| Top-level directories | `kebab-case` | `frontend-dashboard/`, `frontend-mobile/` |
| Env vars | `SCREAMING_SNAKE_CASE` | `APP_NAME`, `CORS_ORIGINS` |
| Config fields (Python) | `snake_case`, matches env var lowercased | `app_name` ↔ `APP_NAME` |

One current inconsistency to be aware of: the backend's JSON responses use
`snake_case` keys (e.g. `app_name`) and the frontend's hand-written TypeScript
interfaces copy that verbatim, rather than transforming to `camelCase`. This
is fine at today's scale (one endpoint) — see
[08_TESTING_STRATEGY.md](08_TESTING_STRATEGY.md) and
`docs/architecture/04_API_GUIDELINES.md` if introducing an OpenAPI-generated
client later, which would be the natural point to reconsider it.
