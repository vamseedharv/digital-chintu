# 008 Settings

## Status: Not started

Configuration is env-var-driven, typed, and validated
(`backend/app/core/config.py`; see
[docs/architecture/01_SYSTEM_ARCHITECTURE.md](../architecture/01_SYSTEM_ARCHITECTURE.md)'s
"Configuration flow"), including assistant name, wake word, default theme,
and default language — and read-only via `GET /api/v1/config`. Changing any
of it still requires a restart and editing `.env` by hand: there is no
user-facing Settings feature — no API to *write* settings at runtime, no
persisted per-user overrides, no Settings UI. Fully open; this feature
should decide whether it wraps/replaces the env-driven defaults with a
DB-backed override layer.

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
