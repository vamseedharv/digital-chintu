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
non-feature finding fixed. Since that freeze (all still unreleased): the
plugin extension point (`010_Plugin_Framework`); **the first real product
screen**, the Dashboard (`007_Dashboard`) — a widget-hosting home screen
(greeting, clock, the existing health check, placeholder tiles for
Weather/Reminders/To-do/Shopping List); **the first real persistence**,
Settings (`008_Settings`) — `app_name`/`default_theme` are now DB-backed
and writable at runtime via a Settings page, backed by the app's first
SQLAlchemy model and Alembic migration (introduced ahead of the originally
planned Phase 4 — see [BACKLOG.md](BACKLOG.md)); and **Assistant Onboarding**
(`009_Assistant_Onboarding`) — a first-run wizard gated by a third Settings
key (`onboarding_complete`), skippable and re-runnable, not a one-time gate.

**Phase 0 is now fully closed** (001 through 009 all ✅ Done, save `004`'s
two narrow, non-blocking, now-tracked gaps — see
[ROADMAP.md](ROADMAP.md)'s Phase 0 table). No reminders, voice, AI, or media
integrations exist yet, and no real plugin has been built on top of the
plugin extension point. Phase 1 (Plugin Framework) is done; Phase 2 (Voice
Pipeline) is next per [ROADMAP.md](ROADMAP.md).

## What exists today

| Area | State |
|---|---|
| Backend | FastAPI app factory, Clean Architecture layer folders (`api/core/domain/services/repositories/db`), typed/validated env-driven config (assistant name, wake word, theme, language, dev/prod profiles — see `docs/architecture/01_SYSTEM_ARCHITECTURE.md`), structured logging, APScheduler (wired, no jobs), a plugin extension point (discovery/interface/dynamic router registration, no real plugin yet — `docs/architecture/05_PLUGIN_SDK.md`), a settings domain (DB-backed `app_name`/`default_theme`/`onboarding_complete` overrides — `docs/architecture/03_DATABASE_DESIGN.md`), four endpoint modules (`/api/v1/health`, `/api/v1/config`, `/api/v1/plugins`, `/api/v1/settings`) — all added since the `v0.2.0` freeze, not yet part of a tagged release |
| Frontend | React + TypeScript + Vite + Tailwind v4 — application shell (`app/`: `AppShell`, router, nav, onboarding-redirect gate), routed pages (`routes/`: **dashboard** (widget grid: greeting, clock, health check, placeholder tiles — `components/dashboard/`), **settings** (`SettingsPage`, `TextField`/`SelectField`), **onboarding** (`OnboardingPage` — full-screen, sibling of `AppShell`), 404, error), a reusable component library (`components/ui/`, `components/layout/`), dark/light theme (persisted) |
| Database | SQLite via SQLAlchemy, migrated with Alembic — **`settings` table, the first real model** (`docs/architecture/03_DATABASE_DESIGN.md`) |
| Docker | Both services containerized, multi-arch, healthchecked, resource-limited, wired via `docker-compose.yml`; backend image now runs `alembic upgrade head` before serving |
| CI | GitHub Actions: backend (Linux+Windows), frontend (Linux) — lint, type-check, `import-linter` (backend) + `import/no-restricted-paths` (frontend), tests |
| Tests | 108 backend (unit+integration) + 112 frontend (unit+integration) + 7 E2E — all passing, all added/grown since the `v0.2.0` freeze |
| Docs | Architecture docs (`docs/architecture/`) and guides (`docs/guides/`) filled in for what's actually implemented; `CONTRIBUTING.md`/`DEVELOPMENT.md` now exist at the repo root |

## Test coverage

| Package | Tests | Statements | Branches | Functions | Lines |
|---|---|---|---|---|---|
| Backend (Pytest) | 108 | 99% | — | — | — |
| Frontend (Vitest) | 112 | 98.57% | 97.12% | 100% | 99.47% |
| E2E (Playwright) | 7 | n/a | n/a | n/a | n/a |

Remaining gaps are deliberate, not overlooked (`backend/app/db/base.py`'s
`DeclarativeBase` is now exercised by `SettingModel` and no longer one of
them): `ThemeProvider`'s SSR guard (untestable in jsdom without mocking the
mock), and `MobileNav`'s `!first || !last` empty-focusable-list guard (defensive —
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

- Plugin discovery/interface/registration exists (`backend/app/core/plugins.py`,
  `010_Plugin_Framework`), but no real plugin has been built yet —
  `plugins/` has no subdirectories.
- No task scheduler jobs registered (APScheduler is wired but idle).
- `ThemeProvider` doesn't consume the (now writable) `default_theme`
  setting yet — only `localStorage`/OS preference. Changing it via the
  Settings page persists correctly but has no visible effect on a fresh
  browser's initial theme. See `docs/features/008_Settings.md`.
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
