# 011 Wake Word

## Status: Not started

`WAKE_WORD` exists as a validated config value (non-blank, ≤64 chars —
`backend/app/core/config.py`, default `"Hey Chintu"`, readable via
`GET /api/v1/config`), added as part of the configuration system. No
wake-word *detection* engine (OpenWakeWord, per
[docs/Foundation/04_Tech_Stack.md](../Foundation/04_Tech_Stack.md)) is
integrated — this feature is otherwise fully open.

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
