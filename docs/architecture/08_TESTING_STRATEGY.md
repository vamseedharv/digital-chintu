# 08 Testing Strategy

Status: **implemented** for the Project Setup surface (config, logging, db session
scaffolding, health endpoint, theme, health-check UI). Extend the same pattern as
each new feature lands — don't invent a different structure per feature.

## Three tiers

| Tier | Tooling | Scope | Where |
|---|---|---|---|
| Unit | Pytest (backend), Vitest (frontend) | One module/hook/component, dependencies mocked or monkeypatched | `backend/tests/unit/`, `frontend-dashboard/src/__tests__/unit/` |
| Integration | Pytest + `TestClient` (backend), Testing Library (frontend) | The real app wired together — routing + middleware + config, or the composed component tree — no external services | `backend/tests/integration/`, `frontend-dashboard/src/__tests__/integration/` |
| E2E | Playwright | Both real services running together, driven through a real browser | `tests/e2e/` |
| Architecture conformance | `import-linter` | Static check that `api -> services -> repositories -> domain` isn't violated — not a test of behavior, a test of structure | `backend/pyproject.toml`'s `[tool.importlinter]`, run via `make lint` |

Run all three test tiers locally with `make test` (unit + integration for
both packages) plus `cd tests && npm run test:e2e` (E2E, separate because it
needs both servers running and is slower). Architecture conformance runs as
part of `make lint`, not `make test` — it's a lint-time structural check, not
a behavioral test.

## Backend

- `tests/conftest.py` has one autouse fixture that clears the
  `get_settings()` `@lru_cache` before and after every test — without it, an
  env var set by one test leaks into the next test's `Settings()` instance.
- Tests that need a non-default config build their own `Settings(...)` or
  `TestClient(create_app())` locally in the test body (after
  `monkeypatch.setenv` + `get_settings.cache_clear()`), rather than relying
  on the shared `client` fixture — fixtures are resolved before the test body
  runs, so env vars set inside the test body can't affect an
  already-constructed fixture.
- `backend/app/db/session.py` binds its engine to settings at *import time*,
  so testing a different `DATABASE_URL` means `importlib.reload()`-ing the
  module under a monkeypatched environment (see `tests/unit/test_session.py`)
  — not a pattern to reach for casually, but necessary here without
  refactoring the production module.
- `tests/unit/test_scheduler.py` verifies the APScheduler instance
  (`core/scheduler.py`) starts and stops with the FastAPI app's lifespan
  (via `with TestClient(create_app()):`) — it has no jobs to test yet, only
  that the lifecycle wiring itself works.

Run with coverage: `pytest --cov-report=html` → `backend/htmlcov/index.html`.
Current coverage: **97% statements** (the only gap is `db/base.py`'s empty
`DeclarativeBase` class — nothing to test until real models exist).

## Frontend

- Components that fetch their own data are kept minimal — `HealthStatus`
  takes its state as a prop (`health: HealthState`) rather than fetching
  internally, so it can be unit-tested with plain prop variations instead of
  mocking `fetch`.
- `useHealth` (the shared fetch hook) is unit-tested directly via
  `renderHook`, including the unmount-during-fetch race (both the success and
  error resolution paths) so a late `setState` after unmount can't slip back
  in unnoticed.
- `ThemeProvider`/`useTheme` tests mock `window.matchMedia` (not implemented
  by jsdom) via `src/setupTests.ts`'s global polyfill plus a per-test override
  for OS-preference scenarios.
- `App.test.tsx` (integration) mocks only the network boundary (`fetch`) and
  renders the real `ThemeProvider` + `App` + `HealthStatus` together.

Run with coverage: `npx vitest run --coverage` → `frontend-dashboard/coverage/index.html`.
Current coverage: **98% statements, 97% branches, 100% functions/lines** (the
one gap is `ThemeProvider`'s `typeof window === 'undefined'` SSR guard,
untestable in jsdom without mocking the mock).

## E2E

`tests/playwright.config.ts` auto-starts both the backend (`uvicorn`, via
whichever of `backend/.venv/bin/python` or `backend/.venv/Scripts/python.exe`
actually exists — checked by file, not by host OS, so a venv built on a
different OS than the one running the test doesn't silently break) and the
frontend (`npm run dev`), and reuses them if already running outside of CI.

Assertions favor properties over exact strings where the underlying value is
configurable — e.g. the E2E header-name check asserts the header text
matches whatever the health-status line reports, rather than hardcoding the
default app name, so it can't regress into re-hardcoding the assistant name.

Not wired into `.github/workflows/ci.yml` — kept as a local/manual suite for
now to keep CI fast; add a dedicated CI job once there's enough UI surface to
justify the extra runtime (browser install + two servers).

## What's intentionally not covered yet

No load/performance testing, no accessibility-audit automation, no visual
regression testing, no contract testing between frontend and backend beyond
the hand-written TypeScript interfaces matching the Python response shape.
Introduce these when a feature's requirements actually call for them.
