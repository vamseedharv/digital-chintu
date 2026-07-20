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
