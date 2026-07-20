# 013 Settings

## Status: Implemented

See [docs/features/008_Settings.md](../../features/008_Settings.md) for the
feature-level Definition of Done and the architecturally significant
decision this feature made (introducing the first DB model + Alembic ahead
of Phase 4 — see
[docs/architecture/03_DATABASE_DESIGN.md](../../architecture/03_DATABASE_DESIGN.md)).
`009_Assistant_Onboarding` later added a third managed key,
`onboarding_complete`, to this same domain — see that feature's own doc;
this page describes the domain as it stands today (three keys), not just
the original two.

## Purpose

Let a user change the two settings that already existed as env-driven
defaults but had no runtime write path: the assistant's display name and
the default theme. Establish the settings domain's schema/storage so later
features (voice, plugins, further theme options) register their own
settings without a core rewrite — without speculatively building UI or API
surface for settings that don't exist yet.

## User Stories

- As a user, I can rename the assistant from the dashboard instead of
  editing `.env` and restarting the backend.
- As a user, I can change the default theme from the dashboard, and see
  that it's actually saved (persists across a reload of the Settings page
  itself, and is reflected by `/api/v1/config`/`/api/v1/health`).
- As a developer adding a future setting, I add a `SettingKey`, a field on
  the API's response/update schemas, and a form field — no database
  migration, since the underlying table is a generic key/value store.

## Functional Requirements

1. `GET /api/v1/settings` returns the current effective value of every
   managed setting (a DB override if one exists, otherwise the env-driven
   default).
2. `PATCH /api/v1/settings` accepts a partial update (any subset of
   fields); omitted fields are left unchanged, invalid values (blank/
   over-length name, unknown theme) are rejected with `422` and persist
   nothing.
3. A successful update is immediately visible on the next `GET`, and is
   reflected by `GET /api/v1/config`/`GET /api/v1/health` too — the app
   has one consistent view of these two settings, not two.
4. The dashboard's Settings page loads current values into a form,
   shows a loading state while fetching and a saving state while
   submitting, and reports success or failure after a save attempt.

## Non-functional Requirements

- Cross platform: same backend/frontend stack as every other feature; no
  platform-specific code.
- No paid subscriptions: SQLite + Alembic, both free/self-hosted.
- Offline-first where practical: once loaded, the form holds its fetched
  values client-side; only the save action needs the backend reachable.

## UI

- Dark mode / light mode: inherited from the existing design tokens — no
  new styling concepts.
- Glassmorphism: the form sits inside the existing `Card` component.
- Responsive: single-column form, same `PageContainer` width as the
  Dashboard.
- Accessibility: `TextField`/`SelectField` (new, `components/ui/`) each
  associate a `<label>` with its control via `useId()`, expose descriptions
  via `aria-describedby`, and mark validation errors with `aria-invalid`
  plus a `role="alert"` message — the same pattern `HealthStatus` already
  uses for its own error state.

## Backend

FastAPI, Clean Architecture, now with real content in every layer that was
previously an empty placeholder package:

- `domain/settings.py` — `SettingKey` (the managed keys: `app_name`,
  `default_theme`, `onboarding_complete`), `EffectiveSettings`.
- `repositories/settings_repository.py` — plain key/value reads and writes.
- `services/settings_service.py` — resolves the effective value of each
  setting (override or env default) and validates new values.
- `api/v1/endpoints/settings.py` — `GET`/`PATCH /api/v1/settings`.
- `api/v1/deps.py` — new: the shared `get_settings_service` FastAPI
  dependency provider, also used by the now-updated `health.py`/`config.py`
  so every endpoint resolves the same effective values.

## Database

See [docs/architecture/03_DATABASE_DESIGN.md](../../architecture/03_DATABASE_DESIGN.md)
for the full schema and migration story.

## APIs

`GET /api/v1/settings` → `{app_name, default_theme, onboarding_complete}`.
`PATCH /api/v1/settings` → same shape in and out, partial. See
[docs/architecture/04_API_GUIDELINES.md](../../architecture/04_API_GUIDELINES.md)
for the REST conventions both endpoints follow (versioned prefix,
`snake_case`, `response_model`).

## WebSocket Events

None. No WebSocket transport exists anywhere in the app yet; a settings
change today only needs to be visible on the next fetch, not pushed live —
see [docs/features/008_Settings.md](../../features/008_Settings.md)'s
"Deliberately out of scope" for the related cross-tab/cross-client sync gap.

## Configuration

`app_name` and `default_theme` are writable at runtime (this feature);
`onboarding_complete` (`009_Assistant_Onboarding`) too, with no env-driven
concept of its own — it defaults to `false` until explicitly set. `wake_word`
and `default_language` remain env-only — see
[docs/features/008_Settings.md](../../features/008_Settings.md)'s
"Deliberately out of scope".

## Testing

**Unit**: `test_validation.py`, `test_settings_repository.py`,
`test_settings_service.py`, `test_migrations.py` (runs the real `alembic`
CLI against a throwaway DB — the only test that actually exercises the
migration files). Frontend: `TextField.test.tsx`, `SelectField.test.tsx`,
`useSettings.test.ts`, `SettingsPage.test.tsx`.

**Integration**: `test_settings_api.py` — persistence round-trips, partial
updates, validation rejection, and the cross-endpoint consistency check
(`/health`/`/config` reflect an override). Frontend: `App.test.tsx` gained
a navigation test for the new `/settings` route.

**E2E**: not extended for `008_Settings` itself, but a settings round-trip
test (`tests/e2e/smoke.spec.ts`) was added at the time and `009_Assistant_Onboarding`
later added another for the onboarding flow — both exercise this same
`GET`/`PATCH /api/v1/settings` surface.

## Manual QA

1. `make backend-dev` + `make frontend-dev`, open the Settings page.
2. Confirm it loads the current assistant name and theme.
3. Change the name, save, confirm the success message and that a reload of
   the Settings page shows the new name.
4. Confirm the sidebar/dashboard greeting shows the new name after a full
   page reload (not live — see the known cross-component sync gap).
5. Try an empty name — confirm it's rejected with an inline error, not
   silently accepted.
6. Change the theme, confirm `GET /api/v1/config` reflects it.
7. Stop the backend, reload the Settings page — confirm the "could not
   load" error state, not a crash.

## Definition of Done

See [docs/features/008_Settings.md](../../features/008_Settings.md).
