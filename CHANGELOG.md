# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Configuration system (`backend/app/core/config.py`): typed, validated
  settings on top of the existing `pydantic-settings` base —
  `Environment` (`development`/`testing`/`production`) and `Theme`
  (`light`/`dark`/`system`) enums, new `WAKE_WORD`/`DEFAULT_THEME`/
  `DEFAULT_LANGUAGE` settings alongside the existing `APP_NAME`, non-blank/
  length validation on assistant-identity fields, BCP-47-style format
  validation on `default_language`, and a hard validation error for
  `app_env=production` + `debug=true` together (fails fast at startup
  instead of serving verbose tracebacks in production).
- `GET /api/v1/config`: read-only runtime configuration endpoint exposing
  the non-secret settings above via a Pydantic `response_model` — the first
  endpoint to use one (see `docs/architecture/04_API_GUIDELINES.md`).
- Backend tests: 19 new unit tests (`tests/unit/test_config.py`) covering
  defaults, env-var overrides, and every new validation rule; 3 new
  integration tests (`tests/integration/test_config_api.py`) for the new
  endpoint, including its OpenAPI schema.

No UI, AI, or reminders work included — config values only (wake word,
theme, language are settings a future feature reads/exposes, not the
wake-word engine, an AI router, or reminders themselves). See
`docs/features/008_Settings.md`, `009_Assistant_Onboarding.md`, and
`011_Wake_Word.md` for what's still open on top of this.

- Plugin framework (`backend/app/core/plugins.py`, `010_Plugin_Framework`):
  filesystem-based discovery under a new `PLUGINS_DIR` setting (each
  `<name>/plugin.py` exposing a module-level `plugin: Plugin` instance), a
  `Plugin` contract (`PluginMetadata` + optional router/`on_startup`/
  `on_shutdown`), and dynamic router registration mounting each enabled
  plugin at `/api/v1/plugins/{slug}` — no more hand-editing
  `api/v1/router.py` to add a plugin. See
  `docs/architecture/05_PLUGIN_SDK.md` for the full contract (trust model,
  discovery, versioning, fail-fast vs. fail-soft handling).
- New `ENABLED_PLUGINS` setting: a comma-separated allow-list of plugin
  slugs; empty/unset enables every discovered plugin (deliberately not
  deny-by-default like `CORS_ORIGINS` — see 05_PLUGIN_SDK.md's "Enabling /
  disabling").
- `GET /api/v1/plugins`: read-only list of discovered plugins (slug, name,
  version, enabled state).
- `docker-compose.yml`: read-only bind mount (`./plugins:/app/plugins:ro`)
  so plugins dropped into the host's `plugins/` are picked up without an
  image rebuild.
- Backend tests: 13 new unit tests (`tests/unit/test_plugins.py`) covering
  discovery, duplicate-slug failure, broken/invalid plugins being skipped,
  and version/allow-list gating; 10 new integration tests
  (`tests/integration/test_plugins_api.py`) covering the endpoint, mounted
  routing, a broken plugin not blocking startup, and lifespan startup/
  shutdown hooks including failure isolation.

No real plugin exists yet — this is the extension point only. See
`docs/features/010_Plugin_Framework.md` (Status: Done) and
`docs/features/041_Home_Assistant.md`/`042_Device_Control.md` for what's
still open on top of this.

- Dashboard (`007_Dashboard`): the home route (`/`) is now a real
  widget-hosting screen instead of the diagnostic-only page it was.
  `components/dashboard/`: `WidgetCard` (shared glass-card + icon + `<h2>`
  shell every tile widget renders through), `GreetingWidget` (time-of-day
  greeting, names the configured assistant, re-evaluates every 60s),
  `ClockWidget` (live local time/date, updates every second), and
  `PlaceholderWidget` (generic "Coming soon" tile, reused for Weather/
  Reminders/To-do/Shopping List until each has a real feature). The
  existing `HealthStatus` check is unchanged, now one grid tile among
  several rather than the whole page. No new backend endpoint — reuses
  the already-fetched `app_name` and the existing `/api/v1/health` check;
  see `docs/SDS/01_UI/012_Dashboard.md`'s "Backend Design" for why a
  server-driven layout isn't built yet.
- `components/layout/PageContainer.tsx`: widened `max-w-2xl` → `max-w-5xl`
  so a multi-column widget grid has room; affects every page (404/error
  pages just get more side margin, no regression).
- `AppShellContext` gained `appName: string` (previously only `health`),
  so pages can use the already-computed assistant name directly.
- Frontend tests: 23 new/changed unit tests (`greeting.test.ts`,
  `WidgetCard.test.tsx`, `GreetingWidget.test.tsx`, `ClockWidget.test.tsx`,
  `PlaceholderWidget.test.tsx`, `DashboardPage.test.tsx` replacing
  `HomePage.test.tsx`) plus one new integration assertion in `App.test.tsx`.
- E2E: `tests/e2e/smoke.spec.ts` gained a test asserting the greeting and
  every widget tile render on a real page load.

- Settings (`008_Settings`): `app_name` and `default_theme` are now
  DB-backed and writable at runtime, via a new Settings page in the
  dashboard and `GET`/`PATCH /api/v1/settings`. **This is the app's first
  real persistence** — a `settings` key/value table (`backend/app/db/models.py`'s
  `SettingModel`) and Alembic (`backend/alembic/`), introduced ahead of the
  originally-planned Phase 4 (`017_Reminders`) because a Settings feature
  that can't durably persist a change isn't one — see
  `docs/architecture/03_DATABASE_DESIGN.md` for the full reasoning and
  `BACKLOG.md`'s "Resolved ahead of schedule". `GET /api/v1/health` and
  `GET /api/v1/config` now resolve through the same effective-settings
  layer, so an override is reflected everywhere, not just by the new
  endpoint.
- Backend: `domain/settings.py` (`SettingKey`, `EffectiveSettings`),
  `repositories/settings_repository.py`, `services/settings_service.py`,
  `api/v1/endpoints/settings.py`, `api/v1/deps.py` (new shared dependency
  providers) — the first real modules in what were previously empty
  `domain`/`services`/`repositories` packages. `core/validation.py`
  extracts the short-text validator `core/config.py` already had, now
  shared with the settings API schema.
- Migrations run as an explicit step before the app starts (`alembic
  upgrade head && <serve>`), not from inside FastAPI's lifespan — wired
  into `Makefile`'s `backend-dev`, the backend `Dockerfile`'s `CMD`, and
  `tests/playwright.config.ts`'s webServer command. See
  `docs/architecture/03_DATABASE_DESIGN.md`'s "Migrations" for why.
- Frontend: `components/ui/TextField.tsx`/`SelectField.tsx` (the first form
  primitives), `api/settings.ts`/`useSettings.ts`, `routes/SettingsPage.tsx`,
  a new "Settings" nav item/route.
- Backend tests: `test_validation.py`, `test_settings_repository.py`,
  `test_settings_service.py`, `test_migrations.py` (runs the real `alembic`
  CLI against a throwaway DB), `test_settings_api.py` (persistence
  round-trips, partial updates, validation, and the cross-endpoint
  consistency check against `/health`/`/config`). `tests/conftest.py`
  gained `make_test_client()`/`db_session` — every existing test that built
  its own `TestClient(create_app())` now goes through the former so no test
  can read or write the developer's real `backend/data/chintu.db`.
- Frontend tests: `TextField.test.tsx`, `SelectField.test.tsx`,
  `useSettings.test.ts`, `SettingsPage.test.tsx`, plus a navigation
  assertion in `App.test.tsx`. Two `MobileNav.test.tsx` focus-trap
  assertions updated for the new second nav item.
- E2E: a settings round-trip test (changes the assistant name, reloads,
  confirms it persisted, then restores the original value since this test
  drives the real dev database, not a sandboxed one).

**Known gap, not fixed here**: `ThemeProvider` doesn't consume the (now
writable) `default_theme` setting — only `localStorage`/OS preference.
Changing it via Settings persists correctly but has no visible effect on a
fresh browser's initial theme yet; tracked in `BACKLOG.md`. See
`docs/features/008_Settings.md` for what else is deliberately out of scope
(`wake_word`/`default_language`, per-user overrides, live cross-tab sync).

## [0.2.0] - 2026-07-09

**Foundation frozen.** UI Framework built, then reviewed twice (a UI-specific
pass and a full architecture review) and every approved, non-feature finding
from both fixed in the same release. No product feature (reminders, voice,
AI, plugins, media) has started — see [PROJECT_STATUS.md](PROJECT_STATUS.md)
and [REPO_HEALTH_REPORT.md](REPO_HEALTH_REPORT.md) for the frozen snapshot.

### Added

- UI Framework (`frontend-dashboard/`): application shell (`app/AppShell.tsx`)
  with a responsive sidebar (desktop) / drawer nav (mobile, focus-managed,
  Escape-to-close), routing via `react-router` (`app/router.tsx`, with a
  404 page and a route-level error boundary page), a reusable component
  library (`components/ui/`: `Button`, `Card`, `Spinner`, `Skeleton`,
  `EmptyState`, `Heading`, `Text`), design tokens and a `.glass` utility
  (`index.css`'s `@theme` block, Tailwind v4), and `lucide-react` icons.
  No dashboard widgets, weather, reminders, AI, or plugin content — shell
  and primitives only. See `docs/features/005_Frontend_Framework.md` and
  `docs/features/006_Theme_Engine.md`.

### Changed

Post-implementation review of the UI Framework — component duplication,
naming, theme consistency, accessibility, animation, and performance:

- Extracted `NavLinks` (shared by `Sidebar` and `MobileNav`) — the two had
  duplicated the nav-item rendering, and `MobileNav`'s copy was silently
  missing the focus ring `Sidebar`'s had.
- Added `LinkButton` and factored `Button`'s styling into `buttonStyles.ts`'s
  `buttonClasses()` — `NotFoundPage` and `ErrorPage` had each duplicated the
  same long button-styled `<Link>` className by hand.
- `ThemeToggle` now uses the `.glass` utility (was a slightly different,
  hand-typed translucent-blur recipe) and has a focus-visible ring (was
  missing — the only interactive control without one).
- `Card` now has its own built-in mount animation; `HealthStatus` no longer
  wraps it in a redundant `motion.div`.
- Added `<MotionConfig reducedMotion="user">` at the app root — every
  Framer Motion animation now respects `prefers-reduced-motion`.
- `MobileNav` now traps Tab focus while open (previously only set initial
  focus and closed on Escape — Tab could leave the drawer into the page
  behind it).
- Verified (not assumed) muted-text contrast empirically: 4.55:1 light /
  6.78:1 dark, both passing WCAG AA.

See [ROADMAP.md](ROADMAP.md) and [BACKLOG.md](BACKLOG.md) for what's planned
next.

Architecture Review follow-up (see `ARCHITECTURE_REVIEW_REPORT.md`'s
"Improvements, in priority order") — approved, non-feature items only:

- Added `eslint-plugin-import`'s `import/no-restricted-paths` to the frontend
  ESLint config, mirroring the backend's `import-linter`: `src/api` and
  `src/theme` can no longer import from `src/components`, `src/routes`, or
  `src/app`. Verified it catches a real violation (tested, then reverted)
  before wiring it in — including fixing the default resolver, which
  silently ignored every `.tsx` import until configured with the right
  extensions.
- Consolidated `MobileNav`'s backdrop and drawer-slide animations onto one
  shared `DRAWER_TRANSITION` constant so their durations can't drift apart.
- Reviewed `EmptyState` for redundant screen-reader announcement: icon is
  already `aria-hidden`, heading carries the accessible name — no code
  change needed. Real screen-reader testing still requires a human; not
  automatable here.
- Plugin extension point design and the remaining carried-forward backlog
  items (scheduler job registration, RPi/PowerShell hardware verification,
  security items) are out of scope for this pass — they're feature work or
  environment-blocked verification, not architecture refactors. Still
  tracked in [BACKLOG.md](BACKLOG.md).

## [0.1.0] - 2026-07-09

Foundation release: the monorepo scaffold, backend/frontend skeletons,
Docker, CI, and dev tooling are stable and verified. No product features
(reminders, voice, AI, plugins, media integrations) yet — see
[PROJECT_STATUS.md](PROJECT_STATUS.md) for the full picture.

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

### Changed

- Post-setup architecture review: reconciled `docs/features/002`–`009`
  against what `001_Project_Setup` already delivered (marked done/partially
  done/not started, so future work doesn't duplicate or miss gaps).
- Wired APScheduler into the backend (`app/core/scheduler.py`, started/stopped
  via the FastAPI app's `lifespan`) — no jobs registered yet; scaffolding
  ahead of the first feature (Reminders/Alarms) that needs it.
- Added `import-linter` to enforce the `api -> services -> repositories ->
  domain` dependency direction in CI and `make lint` (verified it actually
  catches a violation before wiring it in).
- Added fixed Docker resource limits (`mem_limit`/`cpus`) to both services in
  `docker-compose.yml`, conservative for Raspberry Pi deployment.
