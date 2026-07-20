# 009 Assistant Onboarding

## Status: Done

A first-run flow (`GET`/visit `/onboarding`) walks a new user through naming
the assistant and choosing a theme, both persisted through `008_Settings`'s
existing `GET`/`PATCH /api/v1/settings` — no separate storage mechanism. A
third managed setting, `onboarding_complete` (bool, defaults `false`), gates
it: `AppShell` redirects any route to `/onboarding` while it's `false`, and
completing or skipping the wizard sets it `true`. Adding this key needed
**zero database migration** — it's just a new row in the existing generic
key/value `settings` table, exactly validating the extensibility
`008_Settings` was designed for (see
[docs/architecture/03_DATABASE_DESIGN.md](../architecture/03_DATABASE_DESIGN.md)).

**Not a one-time irreversible gate**: `/onboarding` is a real, always
navigable route (a "Run setup again" link lives on the Settings page), and
`onboarding_complete` can be flipped back to `false` like any other setting
— there's no special-cased "only once" logic anywhere.

This closes Phase 0 — see [ROADMAP.md](../../ROADMAP.md)'s Phase 0 table.

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
