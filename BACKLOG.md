# Backlog

Granular, short-horizon items — smaller than a `docs/features/` entry, or
groundwork a future feature will need. For strategic/phase-level sequencing,
see [ROADMAP.md](ROADMAP.md). Roughly ordered by priority within each
section; not dated commitments.

## Before Phase 1 (Plugin Framework) starts

- [x] Design the plugin extension point: a discovery mechanism, a plugin
  interface/base class, and a dynamic router-registration hook in
  `backend/app/main.py`'s `create_app()`. Done and implemented — see
  `docs/features/010_Plugin_Framework.md` (Status: Done) and
  `docs/architecture/05_PLUGIN_SDK.md`. `plugins/` itself still has no real
  plugin in it; `041_Home_Assistant`/`042_Device_Control` are what will
  eventually use this.

## Resolved ahead of schedule

- [x] ~~Introduce the first SQLAlchemy model and Alembic at the same time —
  not before~~. **Superseded**: `008_Settings` needed real persistence to be
  a working feature (a Settings page that can't durably save anything isn't
  one), so it — not `017_Reminders` (Phase 4) — became the first real DB
  model and introduced Alembic. This was an explicit decision, not a silent
  one; see `docs/features/008_Settings.md` and
  `docs/architecture/03_DATABASE_DESIGN.md` for the full reasoning. Phase 4
  now reuses this same Alembic setup rather than introducing it fresh.

## Before Phase 4 (Productivity) starts

- [ ] Register the first APScheduler job and confirm the scheduler survives
  process restarts / app reloads as expected (`backend/app/core/scheduler.py`
  is wired but has never run a real job).

## Before Phase 2 (Voice Pipeline) or another theme-affecting feature starts

- [ ] Wire `frontend-dashboard/src/theme/ThemeProvider.tsx` to actually
  consume the backend's `default_theme` setting (now writable via
  `GET`/`PATCH /api/v1/settings`, see `docs/features/008_Settings.md`).
  Today `ThemeProvider` only checks `localStorage` then OS
  `prefers-color-scheme` — changing `default_theme` persists correctly but
  has no visible effect on a fresh browser's initial theme. Predates 008;
  deliberately not fixed under that feature's banner since it's a separate,
  bounded async-bootstrap change to already-tested core theming code.

## Verification gaps (environment-blocked, not skipped)

- [ ] Run `scripts/setup.ps1` on native Windows PowerShell (this session only
  verified its logic mirrors the tested `scripts/setup.sh`, never executed
  it directly — no native PowerShell runner was available).
- [ ] Run the native dev path and Docker Compose stack on physical Raspberry
  Pi hardware (multi-arch images are confirmed by base-image choice, not by
  running on a real device).
- [ ] Re-verify Docker `cpus` resource limit enforcement on a newer Docker
  Engine — confirmed as a no-op on Engine 20.10 / Compose 2.2.3 via
  `docker inspect` (`mem_limit` **is** enforced there; `cpus` isn't).

## Security

- [ ] Add authentication/authorization before any endpoint exposes sensitive
  data or write operations — everything under `/api/v1` is unauthenticated
  today. See `docs/architecture/06_SECURITY.md`.
- [ ] Add dependency-vulnerability scanning to CI (nothing currently checks
  `pip`/`npm` dependencies for known CVEs).
- [ ] Decide a secrets-management story before Phase 5 (Media & Info)
  integrations need API keys/OAuth tokens — plain `.env` won't be
  appropriate for multi-user or shared deployments.

## Code-level cleanups (low priority, explicitly deferred already)

- [ ] Backend JSON responses are `snake_case`; the frontend hand-copies them
  verbatim into TypeScript interfaces instead of transforming to
  `camelCase`. Revisit if/when an OpenAPI-generated client is introduced
  (natural trigger: Phase 7, when a second client exists). See
  `docs/architecture/02_REPOSITORY_STRUCTURE.md`.
- [ ] The backend's pip distribution name (`digital-chintu-backend`) wraps a
  generically-named `app` module — fine in its own venv, would collide if a
  second Python service ever shares one. Not urgent.
- [ ] `GET /api/v1/health` still returns a bare `dict[str, str]` instead of a
  Pydantic `response_model` — deliberate for an endpoint with no real
  schema. (`GET /api/v1/config`, added with the configuration system, is the
  first endpoint to use `response_model`; not retrofitting `health` since it
  genuinely has no schema to document.) See `docs/architecture/04_API_GUIDELINES.md`.
- [ ] `shared/` has no npm workspace wiring yet (no root `package.json`, no
  `workspaces` field) — set this up when it actually gets its first real
  content, not speculatively.

## Documentation still open

- [ ] `docs/guides/Prompt_Usage.md` and `docs/guides/Release_Process.md` are
  still one-line stubs — fill in when there's a real process to document.
- [ ] No `CODEOWNERS` — low priority until there's more than one regular
  contributor. (`CONTRIBUTING.md` now exists at the repo root.)
- [ ] `docs/MASTER_EXECUTION_PLAN.md` has been referenced by name in prior
  requests but does not exist in this repo — confirm whether it was meant
  to be committed, or stop referencing it.
