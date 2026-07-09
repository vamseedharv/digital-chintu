# 002 Docker

## Status: Delivered under 001_Project_Setup

Docker was implemented as part of [001_Project_Setup.md](001_Project_Setup.md),
not as a separate feature: `backend/Dockerfile`, `frontend-dashboard/Dockerfile`,
both `.dockerignore`s, and the root `docker-compose.yml` all exist and are
verified working (see
[docs/architecture/07_DEPLOYMENT.md](../architecture/07_DEPLOYMENT.md)). No
remaining scope for this doc — nothing to implement here.

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
