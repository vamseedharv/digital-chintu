# 001 Project Setup

## Status: Done

## Objective

Establish the monorepo scaffolding, backend and frontend skeletons, Docker,
CI, and developer tooling that every later feature builds on — with no
feature-specific business logic (no reminders, voice, AI, plugins, media
integrations).

## Scope

- Monorepo directory structure per
  [docs/architecture/02_REPOSITORY_STRUCTURE.md](../architecture/02_REPOSITORY_STRUCTURE.md).
- Backend: FastAPI app factory, Clean Architecture layer folders, environment
  config, structured logging, one health-check endpoint.
- Frontend: React + TypeScript + Vite + Tailwind dashboard, dark/light theme,
  a view that calls the backend's health check.
- Docker: per-service Dockerfiles + a root `docker-compose.yml`.
- CI: GitHub Actions running lint/type-check/tests for both packages.
- Developer tooling: `Makefile`, cross-platform bootstrap scripts.
- Test suites: unit + integration (both packages) + a Playwright E2E smoke suite.

## Deliverables (all done)

- [x] Backend skeleton (`backend/app/{api,core,domain,services,repositories,db}`)
- [x] Frontend skeleton (`frontend-dashboard/src/{api,components,theme}`)
- [x] `frontend-mobile/`, `shared/`, `plugins/` reserved as documented placeholders
- [x] Docker (`backend/Dockerfile`, `frontend-dashboard/Dockerfile`, root `docker-compose.yml`)
- [x] Environment configuration (`.env.example` at root + per-package, `pydantic-settings`)
- [x] Structured logging (console + rotating file handler)
- [x] Linting + formatting (Ruff, Black, mypy strict / ESLint, Prettier, tsc strict)
- [x] GitHub Actions CI (`.github/workflows/ci.yml`)
- [x] Unit tests (`backend/tests/unit/`, `frontend-dashboard/src/__tests__/unit/`)
- [x] Integration tests (`backend/tests/integration/`, `frontend-dashboard/src/__tests__/integration/`)
- [x] E2E smoke tests (`tests/e2e/`, Playwright)
- [x] Manual QA — see checklist below
- [x] Documentation (`README.md`, per-package `README.md`s, `docs/architecture/`, `docs/guides/`)
- [x] `CHANGELOG.md`, `LICENSE` (MIT)

Explicitly **not** part of this feature (do not add here): database models,
business logic, WebSocket events, real Settings-UI integration beyond the
env-var-driven config that already exists, voice, AI routing, plugins.

## Acceptance Criteria

- [x] Works on Raspberry Pi, Linux, Windows, and Docker — both Dockerfiles use
  multi-arch base images; native dev verified on Windows this session
  (Linux/RPi native dev uses the identical `scripts/setup.sh` path, untested
  on physical hardware as part of this feature).
- [x] Dark and light themes supported — class-based toggle, persisted,
  defaults to OS preference.
- [x] No paid services required — SQLite, self-hosted Docker images, GitHub
  Actions free tier.
- [x] Feature is independently testable — see Test Plan below; nothing here
  depends on a future feature to verify.

## Test Plan

See [docs/architecture/08_TESTING_STRATEGY.md](../architecture/08_TESTING_STRATEGY.md)
for the full strategy. Summary:

| Suite | Count | Result | Coverage |
|---|---|---|---|
| Backend unit | 14 | pass | — |
| Backend integration | 6 | pass | 97% statements overall |
| Frontend unit | 21 | pass | — |
| Frontend integration | 4 | pass | 98% stmts / 97% branches / 100% funcs+lines overall |
| E2E (Playwright) | 2 | pass | n/a |

Run: `make test` (unit + integration, both packages) and
`cd tests && npm run test:e2e` (E2E).

## Manual QA

See [docs/guides/Setup_Guide.md](../guides/Setup_Guide.md) for the full
step-by-step walkthrough. Checklist covers: fresh-clone bootstrap
(idempotent), backend standalone (health check, config override via env var,
log file creation, data directory auto-creation), frontend standalone
(renders configured app name, theme toggle persists, error state when
backend is down), full Docker Compose stack (health checks, layer-cache
behavior on rebuild), and a git-hygiene check (`git add -n .` produces no
`node_modules`/`.venv`/`.env`/build-artifact matches).

## Definition of Done

Production-ready for what it claims to be: a working, tested, documented
scaffold — not a working product. Confirmed via:

- All automated tests green (table above).
- `ruff check`, `black --check`, `mypy` (backend) and `eslint`, `tsc --noEmit`,
  `prettier --check` (frontend) all clean.
- Docker images build from scratch and the full stack reaches
  `running (healthy)` for both services.
- Documentation (this doc, architecture docs, guides, READMEs) reflects the
  actual implementation, not aspirational content.

## Git

Not yet committed to version control as of this writing — see the repository
root for current `git status`. Once committed: conventional commit message,
update `CHANGELOG.md`'s `[Unreleased]` section (already reflects this work),
push after the checklist above is re-verified.
