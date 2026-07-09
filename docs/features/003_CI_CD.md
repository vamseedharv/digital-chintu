# 003 CI CD

## Status: Delivered under 001_Project_Setup

CI was implemented as part of [001_Project_Setup.md](001_Project_Setup.md):
`.github/workflows/ci.yml` runs lint/type-check/tests for the backend
(Linux + Windows matrix) and frontend (Linux) on every push and PR. No CD
(deployment automation) exists yet — that's genuinely open, not delivered.
See [docs/architecture/07_DEPLOYMENT.md](../architecture/07_DEPLOYMENT.md)
("Not yet implemented" section) before starting CD work here.

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
