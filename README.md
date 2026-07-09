# Digital Chintu

Digital Chintu is an open-source, self-hosted AI Home Platform — a configurable
home assistant with a web dashboard, mobile client, and (later) voice, plugin,
and automation features. No paid subscriptions are required to run it.

**The foundation is frozen (`v0.2.0`)**: the monorepo scaffolding, backend
and frontend skeletons (including a full application shell, routing, and a
small reusable component library), Docker, CI, and dev tooling all exist,
are tested, and have passed two review passes (UI-specific, then full
architecture) with every approved, non-feature finding fixed. **No product
feature has been built yet** — no reminders, voice, AI routing, plugins, or
media integrations. See [PROJECT_STATUS.md](PROJECT_STATUS.md) for the
current snapshot, [REPO_HEALTH_REPORT.md](REPO_HEALTH_REPORT.md) for a
verified build/lint/test health check of this exact snapshot,
[ROADMAP.md](ROADMAP.md) for what's next, [BACKLOG.md](BACKLOG.md) for
granular open items, and [CLAUDE.md](CLAUDE.md) for repository-wide
guidance.

## Repository layout

```
backend/             FastAPI backend (Clean Architecture: api/core/domain/services/repositories/db)
frontend-dashboard/  React + TypeScript + Vite + Tailwind web dashboard
frontend-mobile/     Mobile client (placeholder — framework TBD, see frontend-mobile/README.md)
shared/              Code shared across clients (placeholder, populated once an API surface exists)
plugins/             Plugin architecture (placeholder, see plugins/README.md)
docker/              Docker documentation (per-service Dockerfiles live with their service)
scripts/             Cross-platform developer bootstrap scripts
tests/               Cross-cutting end-to-end tests (Playwright)
docs/                Project specifications and architecture docs
```

## Requirements

- Python 3.12+
- Node.js 22+
- Docker (optional, for containerized runs)

Supported platforms: Linux, Windows, Raspberry Pi (arm64/armv7), and Docker.

## Quickstart

Full step-by-step walkthrough (prerequisites, troubleshooting, verification):
[docs/guides/Setup_Guide.md](docs/guides/Setup_Guide.md). Short version:

### Option 1 — native (backend + frontend run directly on your machine)

```bash
# Linux / macOS / Raspberry Pi OS / Git Bash & WSL on Windows
./scripts/setup.sh
```

```powershell
# Native Windows PowerShell
./scripts/setup.ps1
```

Then, in separate terminals:

```bash
make backend-dev     # starts the FastAPI backend on http://localhost:8000
make frontend-dev    # starts the Vite dev server on http://localhost:5173
```

Verify: `curl http://localhost:8000/api/v1/health` should return
`{"status":"ok",...}`, and `http://localhost:5173` should show that same
`app_name` in the page header.

### Option 2 — Docker

```bash
cp .env.example .env
docker compose up --build
```

See [docker/README.md](docker/README.md) and
[docs/architecture/07_DEPLOYMENT.md](docs/architecture/07_DEPLOYMENT.md) for details.

## Common tasks

All common tasks are available as `make` targets (see the [Makefile](Makefile)):

```bash
make setup          # bootstrap backend venv + install all dependencies
make lint           # Ruff, mypy, import-linter (backend); ESLint, tsc (frontend)
make format         # format backend (Black) and frontend (Prettier)
make test           # run backend (Pytest) and frontend (Vitest) test suites
make docker-up       # build and start all services via Docker Compose
make docker-down     # stop and remove Docker Compose services
```

On native Windows without `make` installed, run the equivalent commands directly
from [backend/README.md](backend/README.md) and [frontend-dashboard/README.md](frontend-dashboard/README.md),
or use Git Bash/WSL.

## Testing

Each package has `unit/` and `integration/` test suites, plus a
cross-cutting Playwright E2E suite. See
[docs/architecture/08_TESTING_STRATEGY.md](docs/architecture/08_TESTING_STRATEGY.md)
for the full strategy.

- Backend (`backend/tests/{unit,integration}/`): `pytest` in `backend/` (or `make test`).
  Coverage: `pytest --cov-report=html`.
- Frontend (`frontend-dashboard/src/__tests__/{unit,integration}/`): `npm run test`
  in `frontend-dashboard/` (or `make test`). Coverage: `npx vitest run --coverage`.
- End-to-end smoke tests (Playwright, spans both services): see [tests/README.md](tests/README.md).

CI (`.github/workflows/ci.yml`) runs the backend suite on Linux and Windows, and
the frontend suite on Linux, on every push and pull request to `main`.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the contribution workflow and
[DEVELOPMENT.md](DEVELOPMENT.md) for the local dev quickstart (deeper
day-to-day conventions live in [docs/guides/](docs/guides)).

## Documentation

- [PROJECT_STATUS.md](PROJECT_STATUS.md) — current snapshot: what exists, test coverage, platform verification, known limitations.
- [REPO_HEALTH_REPORT.md](REPO_HEALTH_REPORT.md) — verified build/lint/test health check of the frozen foundation.
- [ROADMAP.md](ROADMAP.md) — strategic phase-level sequencing of `docs/features/001`–`050`.
- [BACKLOG.md](BACKLOG.md) — granular open items and deferred cleanups.
- [DEPENDENCY_GRAPH.md](DEPENDENCY_GRAPH.md) — internal module graph (enforced by `import-linter`) and external package dependencies.
- [CONTRIBUTING.md](CONTRIBUTING.md) — how to propose a change.
- [DEVELOPMENT.md](DEVELOPMENT.md) — local dev quickstart.
- [CLAUDE.md](CLAUDE.md) — guidance for AI-assisted development in this repository.
- [docs/guides/Setup_Guide.md](docs/guides/Setup_Guide.md) — step-by-step local setup and troubleshooting.
- [docs/guides/Developer_Guide.md](docs/guides/Developer_Guide.md) — day-to-day conventions: where new code goes, testing patterns, config.
- [docs/guides/Coding_Standards.md](docs/guides/Coding_Standards.md) — lint/format/type-check rules actually enforced.
- [docs/guides/Git_Workflow.md](docs/guides/Git_Workflow.md) — branch naming, commit, and PR conventions.
- [docs/architecture/](docs/architecture) — system architecture, repository structure, deployment, testing strategy, API guidelines, security, UI design system — filled in as each part is implemented.
- [docs/Foundation/](docs/Foundation) — original vision, architecture, tech stack, and coding standards pack.
- [docs/SDS/](docs/SDS) — per-domain software design specifications.
- [docs/features/](docs/features) — sequential feature specs (this repository is implemented feature by feature; [001_Project_Setup.md](docs/features/001_Project_Setup.md) is done).
- [CHANGELOG.md](CHANGELOG.md) — notable changes, in [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format.

## License

[MIT](LICENSE)
