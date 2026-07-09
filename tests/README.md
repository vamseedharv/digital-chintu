# tests

Cross-cutting end-to-end tests (Playwright), spanning the backend and
frontend-dashboard together — unit/integration tests live with each package
instead (`backend/tests/`, `frontend-dashboard/src/__tests__/`).

## Setup

Requires the backend virtualenv and frontend dependencies to already exist
(run `make setup` / `scripts/setup.sh` / `scripts/setup.ps1` from the repo
root first), plus the Playwright browser binaries:

```bash
npm install
npx playwright install --with-deps chromium
```

## Run

```bash
npm run test:e2e       # headless
npm run test:e2e:ui    # interactive UI mode
```

The Playwright config automatically starts the backend (Uvicorn) and
frontend (Vite dev server) if they aren't already running, and reuses them
if they are (set outside of CI). No need to start them manually first.

## Scope

This is a smoke suite (dashboard loads, backend health status renders,
theme toggle works) — not wired into the default CI gate in
`.github/workflows/ci.yml`, to keep CI fast. Run it locally, or add a
dedicated CI job once there's enough UI surface to justify the extra runtime.
