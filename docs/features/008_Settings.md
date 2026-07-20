# 008 Settings

## Status: Done

A DB-backed override layer now sits on top of the env-driven defaults in
`backend/app/core/config.py`: `app_name` and `default_theme` are readable
and writable at runtime via `GET`/`PATCH /api/v1/settings`, persisted in a
new `settings` table (SQLite via SQLAlchemy, migrated with Alembic — see
[docs/architecture/03_DATABASE_DESIGN.md](../architecture/03_DATABASE_DESIGN.md)),
and reflected consistently by the existing `GET /api/v1/health`/
`GET /api/v1/config` endpoints. A Settings page in the dashboard
(`frontend-dashboard/src/routes/SettingsPage.tsx`) lets a user change both.
`wake_word` and `default_language` remain env-only — out of scope for this
pass (see "Deliberately out of scope" below).

**Architecturally significant**: this is the first feature needing real
persistence, and per an explicit decision (not a silent one — see
[BACKLOG.md](../../BACKLOG.md)) it introduces SQLAlchemy models and Alembic
now, ahead of `017_Reminders`/`018_Alarms` (Phase 4), which is where earlier
planning docs originally expected the *first* database model to land. The
rationale: a Settings feature that can't durably persist a change isn't
really a Settings feature — see
[docs/architecture/03_DATABASE_DESIGN.md](../architecture/03_DATABASE_DESIGN.md)
for the full reasoning. Phase 4 now reuses this same Alembic setup rather
than introducing it.

**Known gap, not fixed here**: `frontend-dashboard/src/theme/ThemeProvider.tsx`
has never actually read the backend's `default_theme` — it only checks
`localStorage`, then OS `prefers-color-scheme`. Changing the theme via this
Settings page is real and persists correctly (confirmed via
`GET /api/v1/config`), but has no visible effect on a fresh browser's
initial theme until `ThemeProvider` is wired to consume it — tracked in
[BACKLOG.md](../../BACKLOG.md), deliberately not fixed under this feature's
banner (it predates 008 and is a separate, bounded piece of work).

## Deliberately out of scope

- `wake_word`, `default_language`: exist as env-driven settings today but
  weren't asked for in this pass — adding them is a small, obvious
  extension (a new `SettingKey`, a field on the API schemas, a form field)
  once a real need exists (voice/multilingual features), not before.
- No secrets: nothing in this feature stores API keys/tokens. Phase 5
  (Media & Info) needs a real secrets story before that's safe — see
  [BACKLOG.md](../../BACKLOG.md).
- No per-user overrides: there's one household-wide settings table, no
  concept of "user" yet (`037_User_Profiles` is unstarted). Every client
  sees the same values.
- No live cross-tab/cross-client sync: after saving, the Settings page
  itself reflects the change immediately, but the sidebar/dashboard
  greeting (fetched once on mount elsewhere in the app) only picks it up
  on the next reload — no shared cache/invalidation mechanism exists yet.

## Objective
Implement the feature in a production-ready manner.

## Claude Code Instructions
You are the lead architect and senior full-stack engineer.
Read existing architecture before coding.
Never break previous features.

## Scope
Define and implement this feature.

## Deliverables
- Backend
- Database
- APIs
- WebSocket events
- React UI
- Settings integration
- Documentation
- Unit tests
- Integration tests
- Manual QA

## Acceptance Criteria
- Works on Raspberry Pi, Linux, Windows and Docker.
- Dark and light themes supported where applicable.
- No paid services required.
- Feature is independently testable.

## Git
Create feature branch.
Use conventional commit.
Update CHANGELOG.
Push to GitHub after verification.
