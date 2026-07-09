# Developer Guide

Day-to-day conventions for working in this codebase, once you're already set
up (see [Setup_Guide.md](Setup_Guide.md) if not). Read
[docs/architecture/](../architecture/) for the *why* behind these; this is
the *how*.

## Where new code goes (backend)

`backend/app/` follows Clean Architecture. When adding a feature:

1. **`domain/`** — define entities/interfaces here if the feature needs
   framework-independent business objects. Skip if the feature is thin
   enough not to need them.
2. **`repositories/`** — data access behind an interface, using
   `app/db/session.py`'s `get_db()` dependency. Add SQLAlchemy models in
   `app/db/` alongside `base.py`, and introduce Alembic *at that point* (not
   before — there's nothing to migrate yet).
3. **`services/`** — orchestration/business logic calling repositories.
4. **`api/v1/endpoints/`** — one file per resource, registered in
   `api/v1/router.py`. Use a Pydantic `response_model` for anything beyond a
   trivial response (the health endpoint's bare `dict[str, str]` is a
   deliberate exception for something with no real schema — don't copy that
   part).

Don't let `api/` import from `repositories/` directly, or `services/` import
FastAPI/Starlette types — keep the dependency direction one-way
(api → services → repositories → domain). Nothing enforces this
automatically yet (see `docs/architecture/01_SYSTEM_ARCHITECTURE.md`'s
"Known gaps"); hold the line by convention until it's worth adding tooling.

## Where new code goes (frontend)

`frontend-dashboard/src/`:

- **`api/`** — one file per backend resource (`health.ts` pattern: a typed
  interface + a thin function calling `apiGet` from `client.ts`; add an
  `apiPost`/etc. to `client.ts` itself when a feature first needs one, rather
  than duplicating fetch logic in the resource file). Add a `use<Thing>()`
  hook alongside it if a component needs the fetch/loading/error state
  machine (see `useHealth.ts`).
- **`components/`** — presentational where possible. Prefer passing state in
  as props (like `HealthStatus`'s `health` prop) over having every component
  fetch its own data — it's what makes unit-testing them straightforward and
  avoids duplicate network calls when two components need the same data.
- **`theme/`** — don't add new theme-like state here piecemeal; if a second
  piece of global UI state appears, decide deliberately whether it belongs
  in the same `ThemeContext` pattern or needs its own.

## Configuration

Every runtime setting is an environment variable read once via
`pydantic-settings` (`backend/app/core/config.py`). To add one:

1. Add the field to the `Settings` class with a sensible, safe default
   (never `debug`-like flags defaulting to an insecure value — see
   `docs/architecture/06_SECURITY.md`).
2. Document it in `backend/.env.example`.
3. If Docker Compose needs to pass it through, add it to `docker-compose.yml`'s
   `environment:` block (`${VAR:-default}` pattern) and to the root
   `.env.example`.

Frontend build-time config works the same way via Vite's `VITE_*` env vars
(`frontend-dashboard/.env.example`) — remember these are baked in at build
time, not read at container start (see `docs/architecture/07_DEPLOYMENT.md`).

## Testing

Match the existing three-tier structure (see
`docs/architecture/08_TESTING_STRATEGY.md`) — don't invent a different
layout per feature:

- `backend/tests/unit/` / `frontend-dashboard/src/__tests__/unit/` — one
  module/hook/component, dependencies mocked.
- `backend/tests/integration/` / `frontend-dashboard/src/__tests__/integration/`
  — the real app wired together.
- `tests/e2e/` — only for flows that genuinely need both real services and a
  real browser; keep this suite small, it's the slowest tier.

Backend gotchas to know before writing tests:
- `get_settings()` is cached process-wide (`@lru_cache`) — the autouse
  `_clear_settings_cache` fixture in `tests/conftest.py` resets it between
  tests. If you construct a `Settings()` directly with custom values, pass
  `_env_file=None` to avoid picking up a real local `backend/.env`.
- Fixtures that build a `TestClient(create_app())` do so at fixture-setup
  time, before your test body runs — `monkeypatch.setenv()` in the test body
  won't affect an already-built `client` fixture. Build the client locally
  in the test if it needs custom env vars (see
  `test_health_reflects_the_configured_app_name` for the pattern).

Frontend gotcha: jsdom doesn't implement `window.matchMedia` — it's polyfilled
globally in `src/setupTests.ts`; override it per-test (see
`ThemeProvider.test.tsx`) when a test needs a specific OS-preference value.

## Linting, formatting, type-checking

```bash
make lint      # Ruff + mypy --strict (backend), ESLint + tsc --noEmit (frontend)
make format    # Black (backend), Prettier (frontend)
```

Both backend (`mypy --strict`) and frontend (TypeScript `strict: true` plus
`noUncheckedIndexedAccess`/`noImplicitOverride`) run in strict mode — new
code should type-check cleanly under that, not with suppressions. If you
must suppress (e.g. a third-party typing gap), use the narrowest possible
`# type: ignore[specific-code]` / `@ts-expect-error` with a comment
explaining why, not a blanket ignore.

## Adding a feature end-to-end

1. Read the relevant spec in `docs/features/NNN_Feature_Name.md` (fill in
   the template's TODOs with the real requirements as you go — see
   `docs/features/001_Project_Setup.md` for what a filled-in one looks like).
2. Implement backend (domain → repositories → services → api), then
   frontend, following the placement rules above.
3. Add unit + integration tests as you go, not after.
4. Update the feature's own doc's Deliverables/Acceptance
   Criteria/Definition of Done, plus `CHANGELOG.md`'s `[Unreleased]` section.
5. Run `make lint && make test` before committing.
6. Never break a previously implemented feature — if a change to shared
   infrastructure (config, logging, db session) affects existing tests,
   fix it in the same change, don't leave it red.

## Git

Conventional commits (`feat:`, `fix:`, `docs:`, `chore:`, `test:`, etc.).
Branch-naming and PR-process conventions aren't formally decided yet —
`docs/guides/Git_Workflow.md` is still a placeholder; don't invent a policy
here, ask before establishing one if it matters for your workflow.
