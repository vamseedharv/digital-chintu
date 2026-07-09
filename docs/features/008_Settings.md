# 008 Settings

## Status: Not started

Configuration today is env-var-driven only (`backend/app/core/config.py`,
requires a restart to change). There is no user-facing Settings feature —
no API to read/write settings at runtime, no Settings UI. Fully open.

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
