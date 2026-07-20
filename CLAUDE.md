# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository state

**Project Setup is complete** (see [docs/features/001_Project_Setup.md](docs/features/001_Project_Setup.md)): the monorepo scaffolding, backend skeleton, frontend skeleton, Docker, CI, and dev tooling all exist and are verified working. **Phase 1 (`010_Plugin_Framework`) is also done**: `backend/app/core/plugins.py` provides plugin discovery/registration, but no actual plugin exists yet. **`007_Dashboard` is done too**: the home route (`/`) is a real widget-hosting screen (greeting, clock, the existing health check, placeholder tiles for unbuilt features) — see `frontend-dashboard/src/components/dashboard/` and `frontend-dashboard/src/routes/DashboardPage.tsx`. **`008_Settings` is done as well**: `app_name`/`default_theme` are now DB-backed and writable at runtime (`GET`/`PATCH /api/v1/settings`, a Settings page in the dashboard) — this is the app's first real persistence, `backend/app/db/models.py`'s `SettingModel` plus `backend/alembic/`, introduced ahead of the originally-planned Phase 4 (see `BACKLOG.md`). `backend/app/domain`, `backend/app/services`, and `backend/app/repositories` each now hold one settings module and are otherwise still empty. No other feature work (reminders, voice, AI routing, media integrations, etc.) has started, and `frontend-mobile/`, `shared/`, `plugins/` (still no real plugin in it) remain placeholder directories only. Everything under `docs/` remains the design specification driving that future work.

## Commands

```bash
make setup         # bootstrap backend venv + install all dependencies (or scripts/setup.sh, scripts/setup.ps1)
make backend-dev   # run FastAPI backend with reload, http://localhost:8000
make frontend-dev  # run Vite dev server, http://localhost:5173
make lint          # Ruff + mypy (backend), ESLint + tsc (frontend)
make format        # Black (backend), Prettier (frontend)
make test          # Pytest (backend), Vitest (frontend)
make docker-up     # docker compose up --build
make docker-down   # docker compose down
```

Without `make` (native Windows without Git Bash/WSL), run the underlying commands directly from `backend/README.md` and `frontend-dashboard/README.md`. Full setup walkthrough: `docs/guides/Setup_Guide.md`. Day-to-day conventions (where new code goes, testing patterns): `docs/guides/Developer_Guide.md`.

Both backend and frontend test suites are split into `unit/` and `integration/` (see `docs/architecture/08_TESTING_STRATEGY.md`). End-to-end tests (Playwright, spans both services) live in `tests/` — see `tests/README.md`; not wired into CI. A single test: `pytest tests/unit/test_config.py::test_defaults_are_safe_for_an_unconfigured_deployment` (backend, from `backend/`) or `npx playwright test e2e/smoke.spec.ts -g "dashboard loads"` (E2E, from `tests/`).

## What Digital Chintu is

Digital Chintu is a planned **open-source, self-hosted AI home assistant platform** (see [docs/Foundation/01_Project_Vision.md](docs/Foundation/01_Project_Vision.md)):
- Multi-client: Smart Display, Web dashboard, Android (iOS later)
- Backend-first design
- Assistant name is configurable at onboarding (not hardcoded)
- No paid subscriptions required for core functionality
- Plugin architecture for extensibility (e.g. Home Assistant integration)
- Offline-first where practical
- Must run on Raspberry Pi, Linux, Windows, and Docker

## Architecture

From [docs/Foundation/02_System_Architecture.md](docs/Foundation/02_System_Architecture.md); scaffolded so far vs. still planned:
- Core Backend: FastAPI, Clean Architecture with Service Layer + Repository Layer — **implemented for one feature** (`backend/app/{api,core,domain,services,repositories,db}`; `008_Settings` populated one module per layer, the rest are still empty pending feature work)
- Database: SQLite via SQLAlchemy, migrated with Alembic — **implemented**: `settings` table (`backend/app/db/models.py`, `backend/alembic/`), the first real model — see `docs/architecture/03_DATABASE_DESIGN.md`
- React Dashboard (web client) — **implemented** (`frontend-dashboard/`), including a Dashboard and a Settings page
- REST API — **implemented**: `/api/v1/health`, `/config`, `/plugins`, `/settings`; WebSocket API — planned, not yet added
- Plugin Engine — **scaffolded** (`backend/app/core/plugins.py`: discovery, `Plugin` contract, dynamic router registration — see `docs/architecture/05_PLUGIN_SDK.md`); Home Assistant/custom plugin implementations themselves are still planned, `plugins/` has none yet
- Android client, future iOS client — planned, `frontend-mobile/` is a placeholder (framework not yet chosen)
- Voice pipeline: OpenWakeWord (wake word) → Whisper.cpp (STT) → Piper (TTS) — planned, not started

## Tech stack

(From [docs/Foundation/04_Tech_Stack.md](docs/Foundation/04_Tech_Stack.md); ✅ = in use today)

| Area | Choices |
|---|---|
| Backend | ✅ Python 3.12, FastAPI, SQLAlchemy, SQLite, Alembic, APScheduler (wired into app lifespan, no jobs yet) |
| Frontend | ✅ React 19, TypeScript, Vite, Tailwind CSS v4, Framer Motion |
| Voice | OpenWakeWord, Whisper.cpp, Piper — not started |
| Testing | ✅ Pytest (backend, unit+integration), Vitest (frontend, unit+integration), Playwright (E2E, `tests/`) |
| Python lint/format | ✅ Ruff, Black, mypy (strict), type hints required |
| TypeScript lint/format | ✅ ESLint (flat config), Prettier, strict mode |

## Repository layout

(From [docs/Foundation/03_Repository_Structure.md](docs/Foundation/03_Repository_Structure.md)) — monorepo, now scaffolded:

```
backend/            FastAPI backend (Clean Architecture skeleton, see backend/README.md)
frontend-dashboard/ React + TypeScript + Vite + Tailwind dashboard (see frontend-dashboard/README.md)
frontend-mobile/    Placeholder — Android/iOS framework not yet chosen (frontend-mobile/README.md)
shared/             Placeholder — shared client code, populated once an API surface exists
plugins/            Plugin engine implemented (backend/app/core/plugins.py); no real plugin dropped in yet
docs/               Specifications (this folder)
docker/             Docker documentation (Dockerfiles live per-service; docker-compose.yml at repo root)
scripts/            Cross-platform dev bootstrap scripts (setup.sh, setup.ps1)
tests/              Cross-cutting Playwright E2E suite
```

## Documentation structure — how to navigate `docs/`

The docs are organized in layers with different levels of detail; when implementing, read the most specific relevant doc first, but check the Foundation pack for repo-wide conventions:

- **`docs/Foundation/`** — the initial foundation pack (numbered 00–10). This is the most concrete/authoritative source for architecture, tech stack, repo layout, and coding standards *before any feature work begins*. Per [10_Master_Claude_Prompt.md](docs/Foundation/10_Master_Claude_Prompt.md), foundation work should be completed (backend/frontend skeleton, Docker, CI/CD) before any feature implementation starts.
- **`docs/SDS/`** — the Software Design Specification, organized by domain area (`00_Platform`, `01_UI`, `02_Backend`, `03_Voice`, `04_Productivity`, `05_Media`, `06_AI`, `07_Clients`, `08_Plugins`, `09_Operations`). Each doc is currently a template stub following a fixed 15-section outline (Context, User Stories, Functional/Non-functional Requirements, UX Flow, UI Components, Backend Design, Database, APIs, WebSocket Events, Configuration, Test Plan, Manual QA, Claude Code Prompt, Definition of Done) — sections are largely unfilled placeholders (`(TODO)`) and need to be fleshed out with real requirements before/while a given feature is implemented.
- **`docs/features/`** — numbered, sequential feature specs (001 through 050) intended to be implemented roughly in order, each building on the previous ones without breaking them. Recurring constraints: must run on Raspberry Pi/Linux/Windows/Docker, support dark and light themes, require no paid services, and be independently testable. `001_Project_Setup.md` is filled in and done; `002`–`009` have a Status note reconciling them against what 001 already delivered — `004`/`005`/`006`/`007`/`008` all done, `009` still not started; `010_Plugin_Framework` is done and implemented (see BACKLOG.md); `011` onward are still untouched template stubs.
- **`docs/architecture/`** — filled in for what's actually implemented: `01_SYSTEM_ARCHITECTURE`, `02_REPOSITORY_STRUCTURE`, `03_DATABASE_DESIGN`, `04_API_GUIDELINES`, `05_PLUGIN_SDK`, `06_SECURITY`, `07_DEPLOYMENT`, `08_TESTING_STRATEGY`, `09_UI_DESIGN_SYSTEM` all describe real, current behavior (each also lists what's still a gap).
- **`docs/guides/`** — `Setup_Guide.md`, `Developer_Guide.md`, `Coding_Standards.md`, and `Git_Workflow.md` are filled in and real. `Prompt_Usage.md` and `Release_Process.md` are still stubs — nothing has been decided for those yet; don't invent a policy in them.

## Recurring constraints across specs

These show up repeatedly across the spec docs and should hold for any implementation work in this repo:
- Cross-platform: Raspberry Pi, Linux, Windows, and Docker
- No paid subscriptions/services required for core features
- Dark mode and light mode support in UI, with a glassmorphism-influenced design language; responsive and accessible
- Assistant name must remain a runtime-configurable setting, never hardcoded
- Each feature should be independently testable and must not break previously implemented features
- Conventional commits are expected for any generated commit
