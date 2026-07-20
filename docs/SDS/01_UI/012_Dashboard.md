# 012 Dashboard

## Status: Implemented

See [docs/features/007_Dashboard.md](../../features/007_Dashboard.md) for
the feature-level Definition of Done. This is the first real product
screen — it replaces the diagnostic-only home page with a widget-hosting
home screen, without depending on any feature that hasn't been built yet.

## Purpose

Give the assistant a real home screen: a time-aware greeting using the
configured assistant name, a live clock, the existing backend health check,
and placeholder tiles for the features that will eventually populate this
screen (weather, reminders, to-do, shopping list). Establishes the "widget"
pattern — a `WidgetCard` shell plus a responsive grid — that later features
add real tiles to, without needing to touch layout code.

## Context

Builds on `006_Theme_Engine` (dark/light, glassmorphism, component library)
and `004_Backend_Core`/config system (`GET /api/v1/config`,
`GET /api/v1/health`). Read `docs/architecture/09_UI_DESIGN_SYSTEM.md` for
the existing component library (`Card`, `Heading`, `Text`) reused here, and
`docs/architecture/04_API_GUIDELINES.md` for the REST conventions the
existing endpoints already follow — no new endpoint was needed (see
"Backend Design" below).

## User Stories

- As a user, when I open the dashboard I see a greeting that names the
  assistant I configured, so it doesn't feel like a generic template.
- As a user, I can see the current time and date at a glance without
  needing a separate clock.
- As a user, I can see at a glance which features aren't built yet (rather
  than a broken link or a missing page), so the product feels intentional
  even while incomplete.
- As a developer adding a future feature (weather, reminders, to-do,
  shopping list), I have an obvious place to add a real widget — replace
  the matching `PlaceholderWidget` call in `DashboardPage.tsx` with a real
  component that also renders through `WidgetCard` — without redesigning
  the page layout.

## Functional Requirements

1. The dashboard is the app's home route (`/`), replacing the previous
   diagnostic-only `HomePage`.
2. A greeting widget shows a time-of-day message (morning/afternoon/
   evening/night, computed from the local browser clock) and names the
   assistant using the configured `app_name` — never a hardcoded product
   name (see [CLAUDE.md](../../../CLAUDE.md)'s standing constraint). It
   re-evaluates periodically (every 60s) so the greeting doesn't go stale
   on an always-on display across a bucket boundary (e.g. 11:59 → 12:00).
3. A clock widget shows the current local time and date, updating every
   second.
4. The existing backend-connectivity check (`HealthStatus`, built for
   `001_Project_Setup`) is retained unchanged and embedded as one tile
   among the others — its diagnostic value isn't lost, it's just no longer
   the entire page.
5. Placeholder tiles for Weather, Reminders, To-do, and Shopping List each
   show a title, one-line description, and a "Coming soon" marker — no
   data, no broken links, no dependency on any unbuilt feature or API.
6. The widget grid is a static, frontend-only definition (see "Backend
   Design") — no per-user layout customization yet.

## Non-functional Requirements

- Cross-platform: same React SPA as every other route; no platform-specific
  code. Verified via the existing Raspberry Pi/Linux/Windows/Docker
  posture (`docs/architecture/07_DEPLOYMENT.md`) — nothing here changes it.
- No paid subscriptions or external services: the clock uses the browser's
  own `Intl`/`Date` APIs (no timezone/weather API call); the greeting uses
  already-fetched config data.
- Offline-first where practical: once the initial JS bundle and the one
  `GET /api/v1/config`-derived `app_name` have loaded, the clock and
  greeting keep working without any further network access — only the
  `HealthStatus` tile depends on a live backend connection, and it already
  degrades to an explicit error state (see `HealthStatus.tsx`) rather than
  breaking the page.
- Independently testable: the framework works with zero real feature
  widgets built (today's actual state) as well as once a real widget
  replaces a placeholder.

## UX Flow

1. User navigates to `/` (the only entry point — it's the default route).
2. While `GET /api/v1/config`'s data hasn't resolved yet, the greeting
   widget shows using the app's default name (same
   loading-to-resolved pattern `AppShell` already uses for the sidebar);
   once resolved, it re-renders with the configured name — no layout
   shift, just a text update, matching the existing `HealthStatus`
   loading→success/error pattern.
3. The grid below the greeting renders immediately (clock and placeholders
   need no network data); the system-status tile independently shows its
   own loading → success/error states exactly as it does today.
4. Widgets reflow responsively: one column on narrow viewports, two on
   tablet, three on desktop (see "UI Components").

## UI Components

- `components/dashboard/WidgetCard.tsx` — shared shell: glass `Card` +
  optional `LucideIcon` + `<h2>` title + content slot. Every tile-style
  widget (built-in or future) renders through this, so a new widget writes
  only its content, not layout.
- `components/dashboard/GreetingWidget.tsx` — the page's `<h1>` (not
  wrapped in `WidgetCard` — it's the page hero, not a grid tile) plus a
  muted line naming the assistant.
- `components/dashboard/ClockWidget.tsx` — a `WidgetCard` tile with the
  current time (`tabular-nums`, updates every second) and date.
- `components/dashboard/PlaceholderWidget.tsx` — a generic `WidgetCard`
  tile taking `{ icon, title, description }`, used for the four
  not-yet-built features today; deleted call-by-call as each feature
  lands, not deleted all at once.
- `components/HealthStatus.tsx` — unchanged from `001_Project_Setup`,
  now one grid tile among several instead of the page's sole content.
- `routes/DashboardPage.tsx` — composes the above: `GreetingWidget` as a
  hero, then a `grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6` of
  `ClockWidget`, `HealthStatus`, and four `PlaceholderWidget`s.
- `components/layout/PageContainer.tsx` — widened from `max-w-2xl` to
  `max-w-5xl` so a 2–3 column widget grid has room; this affects every
  page (404/error pages just get more side margin around their already
  centered content, no regression).
- Dark/light and glassmorphism: entirely inherited from the existing
  `Card`/`Heading`/`Text` primitives and `@theme` tokens — no new styling
  concepts introduced (`docs/architecture/09_UI_DESIGN_SYSTEM.md`).
- Accessibility: exactly one `<h1>` (the greeting) with each widget tile as
  a sibling `<h2>`, a correct heading outline for assistive tech; icons
  carry `aria-hidden`; the clock is deliberately *not* an `aria-live`
  region (a screen reader announcing the time every second would be
  noise — the text is available on request like any other static content).

## Backend Design

**No new backend endpoint.** Everything the dashboard needs already
exists:

- The greeting widget's assistant name comes from `AppShellContext.appName`
  (already computed in `AppShell` from `useHealth()`'s `app_name`, the same
  value `GET /api/v1/config` also exposes) — reusing it avoids a second,
  redundant fetch for a value already in memory.
- The clock is entirely client-side (`Date`/`Intl`), no backend involved.
- The system-status tile reuses `GET /api/v1/health` via the existing
  `HealthStatus`/`useHealth` — untouched.
- The four placeholder tiles have no data source.

**The widget set itself is a static frontend definition** (the JSX in
`DashboardPage.tsx`), the same precedent `app/navigation.ts`'s nav-item
list already sets for "an ordered list with no per-user state." A
server-driven layout (which widgets a given user has enabled, their order)
would require persistence and a notion of "user" that doesn't exist yet —
no database models, no auth, no `037_User_Profiles`. Building that now
would be speculative; revisit once a real feature needs per-user
customization, not before.

## Database

None. No models, no migrations — see "Backend Design" above for why.

## APIs

None new. Reuses `GET /api/v1/config` (indirectly, via the already-fetched
`app_name`) and `GET /api/v1/health`, both documented in
`docs/architecture/04_API_GUIDELINES.md`.

## WebSocket Events

None. No WebSocket transport exists anywhere in the app yet (see
`docs/architecture/01_SYSTEM_ARCHITECTURE.md`'s "Known gaps"); nothing on
this screen needs real-time push — the clock ticks locally, and the health
check already polls-on-mount rather than subscribing.

## Configuration

The assistant name (`APP_NAME` → `Settings.app_name` →
`GET /api/v1/config`/`GET /api/v1/health`) is the only configuration this
screen consumes, and it already flows through unchanged — no new setting
was added for the dashboard itself.

## Test Plan

**Unit** (`frontend-dashboard/src/__tests__/unit/`):
`greeting.test.ts` (every time-of-day bracket boundary), `WidgetCard.test.tsx`
(title/content rendering, icon presence/absence and its `aria-hidden`),
`GreetingWidget.test.tsx` (greeting text, assistant-name interpolation,
bucket change while mounted — using `vi.useFakeTimers()`), `ClockWidget.test.tsx`
(initial render, ticking forward, timer cleanup on unmount),
`PlaceholderWidget.test.tsx` (title/description/"Coming soon"),
`DashboardPage.test.tsx` (all widgets present, greeting uses the
context-supplied app name, the real `HealthStatus` still renders).

**Integration** (`frontend-dashboard/src/__tests__/integration/App.test.tsx`):
extended to assert the dashboard's widgets render as part of the full
routed app (real `ThemeProvider` + router), alongside the existing
health-status/theme-toggle/404/mobile-nav assertions.

**E2E** (`tests/e2e/smoke.spec.ts`): a new test asserts the greeting heading,
the assistant-name line, and every widget title (Clock, Weather, Reminders,
To-do, Shopping list) are visible on a real browser load — alongside the
pre-existing health-status/theme-toggle/404/mobile-nav smoke tests, which
still pass unmodified since `HealthStatus` itself didn't change.

## Manual QA

1. `make backend-dev` + `make frontend-dev`, open `http://localhost:5173`.
2. Confirm the greeting matches the time of day and names the configured
   `APP_NAME` (change it in `backend/.env` and restart to verify it isn't
   hardcoded).
3. Confirm the clock ticks and the date is correct.
4. Confirm the backend-connection tile shows success; stop the backend and
   reload to confirm it shows the error state (unchanged behavior).
5. Confirm all four placeholder tiles render with a "Coming soon" marker
   and no console errors.
6. Resize to mobile/tablet/desktop widths — confirm the grid reflows to
   1/2/3 columns.
7. Toggle dark/light mode — confirm every tile (including the new
   `WidgetCard` shell) themes correctly.
8. Run `cd tests && npm run test:e2e`.

## Definition of Done

- `make lint && make test` green (backend unaffected; frontend: 81 unit/
  integration tests, ESLint, Prettier, `tsc -b --noEmit` all clean).
- `npx playwright test` (from `tests/`) green, 5/5 including the new
  widget-grid assertion.
- This document and `docs/features/007_Dashboard.md` reflect what's
  actually built, no `(TODO)` placeholders left in the sections above.
- Verified in a real browser: content, dark/light theme, responsive
  reflow, no console errors.
