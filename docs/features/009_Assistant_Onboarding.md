# 009 Assistant Onboarding

## Status: Not started

The assistant's name (`APP_NAME`) is runtime-configurable via environment
variable end-to-end (backend config → `/api/v1/health` and `/api/v1/config`
→ frontend header, verified with tests), validated non-blank at the config
layer — but there is no onboarding *flow* for a user to set it (or the wake
word, default theme, or default language, all now equally
config-layer-configurable) through the UI. Fully open.

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
