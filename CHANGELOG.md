# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Monorepo scaffolding: `backend/`, `frontend-dashboard/`, `frontend-mobile/`,
  `shared/`, `plugins/`, `docker/`, `scripts/`, `tests/` (see
  [docs/features/001_Project_Setup.md](docs/features/001_Project_Setup.md)).
- Backend (`backend/`): FastAPI app factory, layered Clean Architecture
  folders (`api`, `core`, `domain`, `services`, `repositories`, `db`),
  environment-based configuration, structured logging, and a
  `/api/v1/health` endpoint. Ruff, Black, mypy (strict), and Pytest configured.
- Frontend dashboard (`frontend-dashboard/`): React + TypeScript + Vite,
  Tailwind CSS v4, Framer Motion, a dark/light theme provider, and a
  backend health-check view. ESLint, Prettier, and Vitest configured.
- `frontend-mobile/`, `shared/`, `plugins/` reserved as documented
  placeholders — no implementation yet.
- Docker: per-service `Dockerfile`s (multi-arch, Raspberry Pi-compatible)
  and a root `docker-compose.yml` running backend + frontend-dashboard
  together with a persisted SQLite volume.
- GitHub Actions CI (`.github/workflows/ci.yml`): backend suite on Linux and
  Windows, frontend suite on Linux.
- Root `Makefile` and cross-platform bootstrap scripts (`scripts/setup.sh`,
  `scripts/setup.ps1`).
- Cross-cutting Playwright end-to-end smoke suite (`tests/`), spanning
  backend + frontend together.
- Root and per-package `README.md` files, `LICENSE` (MIT), `.editorconfig`,
  `.gitignore`.
