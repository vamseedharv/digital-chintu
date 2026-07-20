# Project Status

Snapshot as of **2026-07-09** (`v0.2.0` — see [CHANGELOG.md](CHANGELOG.md)).
For where this is headed, see [ROADMAP.md](ROADMAP.md) and
[BACKLOG.md](BACKLOG.md). For a point-in-time build/lint/test verification
of this exact snapshot, see [REPO_HEALTH_REPORT.md](REPO_HEALTH_REPORT.md).

## TL;DR

**The foundation is frozen at `v0.2.0`**: monorepo scaffold, backend and
frontend skeletons (now including a full application shell — routing,
sidebar/drawer nav, a small reusable component library), Docker, CI, and dev
tooling all exist, are tested, and have passed two review passes (a
UI-specific review and a full architecture review) with every approved,
non-feature finding fixed. **No product feature has been built yet** — no
reminders, voice, AI, plugins, or media integrations. Everything below is
infrastructure that those features will be built on; Phase 1
(`010_Plugin_Framework`, see [ROADMAP.md](ROADMAP.md)) is next.

## What exists today

| Area | State |
|---|---|
| Backend | FastAPI app factory, Clean Architecture layer folders (`api/core/domain/services/repositories/db`), typed/validated env-driven config (assistant name, wake word, theme, language, dev/prod profiles — see `docs/architecture/01_SYSTEM_ARCHITECTURE.md`), structured logging, APScheduler (wired, no jobs), two endpoints (`/api/v1/health`, `/api/v1/config`) — the latter two added since the `v0.2.0` freeze, not yet part of a tagged release |
| Frontend | React + TypeScript + Vite + Tailwind v4 — application shell (`app/`: `AppShell`, router, nav), routed pages (`routes/`: home, 404, error), a reusable component library (`components/ui/`, `components/layout/`), dark/light theme (persisted) |
| Database | SQLite, SQLAlchemy engine/session scaffolding — **no models, no migrations** |
| Docker | Both services containerized, multi-arch, healthchecked, resource-limited, wired via `docker-compose.yml` |
| CI | GitHub Actions: backend (Linux+Windows), frontend (Linux) — lint, type-check, `import-linter` (backend) + `import/no-restricted-paths` (frontend), tests |
| Tests | 21 backend (unit+integration) + 58 frontend (unit+integration, 20 files) + 4 E2E — all passing |
| Docs | Architecture docs (`docs/architecture/`) and guides (`docs/guides/`) filled in for what's actually implemented; `CONTRIBUTING.md`/`DEVELOPMENT.md` now exist at the repo root |

## Test coverage

| Package | Tests | Statements | Branches | Functions | Lines |
|---|---|---|---|---|---|
| Backend (Pytest) | 21 | 97% | — | — | — |
| Frontend (Vitest) | 58 | 98.21% | 97.4% | 100% | 100% |
| E2E (Playwright) | 4 | n/a | n/a | n/a | n/a |

Remaining gaps are deliberate, not overlooked: `backend/app/db/base.py`'s
empty `DeclarativeBase` (nothing to test until models exist),
`ThemeProvider`'s SSR guard (untestable in jsdom without mocking the mock),
and `MobileNav`'s `!first || !last` empty-focusable-list guard (defensive —
the drawer always renders at least a close button and one nav link in
practice). See
[docs/architecture/08_TESTING_STRATEGY.md](docs/architecture/08_TESTING_STRATEGY.md).

## Platform verification

| Platform | Native dev | Docker |
|---|---|---|
| Windows | ✅ Verified this session (`scripts/setup.sh` via Git Bash, `make backend-dev`/`frontend-dev`) | ✅ Verified this session (build, run, healthcheck, resource limits inspected) |
| Linux | Same code path as Windows native/Docker; not independently re-run on a physical Linux box this session | Same image, not independently re-run |
| Raspberry Pi | `scripts/setup.sh` should work (same as Linux); **not run on physical hardware** | Multi-arch images confirmed (`python:3.12-slim`, `node:22-alpine`, `nginx:alpine` all publish arm64/armv7); **not run on physical hardware** |
| `scripts/setup.ps1` (native PowerShell) | Logic mirrors the verified `setup.sh`; **not independently executed** (no native PowerShell runner in this environment) | n/a |

## Known limitations (see BACKLOG.md for the full, prioritized list)

- No plugin discovery mechanism or interface exists yet — `plugins/` is a
  reserved directory name only.
- No task scheduler jobs registered (APScheduler is wired but idle).
- No database models/migrations (Alembic not yet introduced — correctly
  deferred until the first model).
- No authentication/authorization on any endpoint.
- Docker `cpus` resource limit is valid config but unenforced on the Docker
  Engine version tested (20.10) — confirmed via `docker inspect`.

## Architecture conformance

`import-linter` enforces `api -> services -> repositories -> domain` as a
one-way dependency in CI and `make lint` — verified to actually catch a
real violation, not just configured. The frontend has an equivalent now:
ESLint's `import/no-restricted-paths` stops `src/api`/`src/theme` from
importing `src/components`/`src/routes`/`src/app`, also verified against a
real violation. See [DEPENDENCY_GRAPH.md](DEPENDENCY_GRAPH.md) for the full
internal and external dependency picture.

## How to verify this yourself

```bash
make lint && make test          # backend + frontend, all gates
cd tests && npm run test:e2e    # E2E, both services auto-started
docker compose up --build       # full stack
```

See [docs/guides/Setup_Guide.md](docs/guides/Setup_Guide.md) for the full
walkthrough.
