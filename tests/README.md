# tests

Cross-cutting end-to-end tests (Playwright), spanning the backend and
frontend-dashboard together — unit/integration tests live with each package
instead (`backend/tests/`, `frontend-dashboard/src/__tests__/`).

## Setup

Requires the backend virtualenv and frontend dependencies to already exist
(run `make setup` / `scripts/setup.sh` / `scripts/setup.ps1` from the repo
root first), plus the Playwright browser binaries. The backend's webServer
command runs `alembic upgrade head` before starting uvicorn (see
`docs/architecture/03_DATABASE_DESIGN.md`), so a fresh checkout's database
is migrated automatically — no separate step needed:

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

This is a smoke suite (dashboard loads with its widget grid, backend health
status renders, settings can be changed and persist, onboarding walks a
first-run user through setup, theme toggle works) — not wired into the
default CI gate in `.github/workflows/ci.yml`, to keep CI fast. Run it
locally, or add a dedicated CI job once there's enough UI surface to justify
the extra runtime.

The settings and onboarding tests drive the real dev database (not a
sandboxed one, unlike the backend/frontend unit and integration suites) and
restore whatever they changed afterward, so re-running the suite doesn't
leave a permanent side effect on your local `backend/data/chintu.db`.
`global-setup.ts` also forces `onboarding_complete: true` once before the
suite runs, so a never-configured DB doesn't send every other test into the
onboarding wizard instead of the page it expects — and the whole spec file
runs serially (`test.describe.configure({ mode: 'serial' })`) so the
onboarding test's temporary flip to `false` can't race with any other
test's page load. See `docs/architecture/08_TESTING_STRATEGY.md`'s "E2E"
section for the full reasoning.
