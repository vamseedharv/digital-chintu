# 08 Testing Strategy

Status: **implemented**, extended as each feature lands (Project Setup,
Dashboard, Plugin Framework, Settings, Assistant Onboarding) — same
three-tier structure throughout, don't invent a different one per feature.

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
  their own app instance locally in the test body (after
  `monkeypatch.setenv` + `get_settings.cache_clear()`), rather than relying
  on the shared `client` fixture — fixtures are resolved before the test body
  runs, so env vars set inside the test body can't affect an
  already-constructed fixture.
- **Any test that builds its own app must call `tests.conftest.make_test_client(create_app())`,
  never a bare `TestClient(create_app())`.** Since `008_Settings` added a
  real database, a bare `TestClient` would read/write the developer's actual
  `backend/data/chintu.db` (via `DATABASE_URL`'s default). `make_test_client()`
  overrides FastAPI's `get_db` dependency with an isolated in-memory SQLite
  database (`Base.metadata.create_all()`, not Alembic — see
  [03_DATABASE_DESIGN.md](03_DATABASE_DESIGN.md)'s "Testing"), so no test can
  ever touch the real file. The shared `client` fixture and the `db_session`
  fixture (for tests that exercise a repository/service directly, no FastAPI
  involved) both use the same isolation.
- `backend/app/db/session.py` binds its engine to settings at *import time*,
  so testing a different `DATABASE_URL` means `importlib.reload()`-ing the
  module under a monkeypatched environment (see `tests/unit/test_session.py`)
  — not a pattern to reach for casually, but necessary here without
  refactoring the production module. This is unrelated to (and doesn't
  replace) `make_test_client()`'s dependency-override isolation above.
- `tests/unit/test_scheduler.py` verifies the APScheduler instance
  (`core/scheduler.py`) starts and stops with the FastAPI app's lifespan
  (via `with make_test_client(create_app()):`) — it has no jobs to test yet,
  only that the lifecycle wiring itself works.
- `tests/unit/test_migrations.py` is the only test that touches Alembic at
  all — it runs the real `alembic` CLI as a subprocess against a throwaway
  `tmp_path` SQLite file, since `make_test_client()`'s `create_all()`
  shortcut never exercises the actual migration files.

Run with coverage: `pytest --cov-report=html` → `backend/htmlcov/index.html`.
Current coverage: **99% statements** (108 tests). No deliberate gaps left
unexplained: `db/base.py`'s `DeclarativeBase` is now exercised by
`SettingModel`.

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
  renders the real `ThemeProvider` + router (`AppShell` + its routes)
  together — including the 404 route and the mobile nav drawer's open/close
  behavior, not just the home page.

- `useSettings` mirrors `useHealth`'s exact state-machine and
  unmount-during-fetch-race test pattern, plus its own `saveState` machine
  for the `PATCH` action (idle/saving/success/error) — same shape, one more
  dimension.
- `OnboardingPage.test.tsx` renders through a real `createMemoryRouter` (not
  `MemoryRouter`) with a dummy `/` route, since it needs to assert on where
  `useNavigate()` actually lands after a save — mirrors the pattern
  `App.test.tsx` already used for router-dependent assertions.
- `App.test.tsx`'s `fetch` mock became URL-aware (`/health` vs `/settings`
  return different shapes) once `AppShell` started fetching both — see its
  `beforeEach`. Defaults `onboarding_complete: true` so existing tests
  exercise the normal app; a dedicated test overrides it `false` to assert
  the redirect gate itself.

Run with coverage: `npx vitest run --coverage` → `frontend-dashboard/coverage/index.html`.
Current coverage: **98.57% statements, 97.12% branches, 100% functions,
99.47% lines** (112 tests). Deliberate gaps: `ThemeProvider`'s `typeof
window === 'undefined'` SSR guard (untestable in jsdom without mocking the
mock) and `MobileNav`'s `!first || !last` empty-focusable-list guard
(defensive — the drawer always renders at least a close button and one nav
link in practice).

## E2E

`tests/playwright.config.ts` auto-starts both the backend (`alembic upgrade
head`, then `uvicorn`, via whichever of `backend/.venv/bin/python` or
`backend/.venv/Scripts/python.exe` actually exists — checked by file, not by
host OS, so a venv built on a different OS than the one running the test
doesn't silently break) and the frontend (`npm run dev`), and reuses them if
already running outside of CI.

Assertions favor properties over exact strings where the underlying value is
configurable — e.g. the E2E header-name check asserts the header text
matches whatever the health-status line reports, rather than hardcoding the
default app name, so it can't regress into re-hardcoding the assistant name.

Unlike the backend/frontend unit and integration suites, E2E drives the
*real* dev database (no `make_test_client()`-style isolation possible — it's
a real browser hitting a real server). The settings E2E test changes and
then restores the assistant name for exactly this reason — see
`tests/README.md`.

`tests/global-setup.ts` runs once before the suite and forces
`onboarding_complete: true` on the real backend — without it, every test
would hit `AppShell`'s onboarding redirect instead of the page it expects,
since a never-configured DB defaults that flag to `false`. The onboarding
test itself needs to flip it back to `false` around its own assertions; that
would race with every *other* test's page load under the default
`fullyParallel: true` (two tests briefly disagreeing about whether
onboarding is done), so `smoke.spec.ts` opts into
`test.describe.configure({ mode: 'serial' })` for the whole file — a small
enough suite that running one test at a time is cheap, and it removes the
race entirely rather than accepting flakiness.

Not wired into `.github/workflows/ci.yml` — kept as a local/manual suite for
now to keep CI fast; add a dedicated CI job once there's enough UI surface to
justify the extra runtime (browser install + two servers).

## What's intentionally not covered yet

No load/performance testing, no accessibility-audit automation, no visual
regression testing, no contract testing between frontend and backend beyond
the hand-written TypeScript interfaces matching the Python response shape.
Introduce these when a feature's requirements actually call for them.
