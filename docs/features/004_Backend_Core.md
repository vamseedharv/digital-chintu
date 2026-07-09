# 004 Backend Core

## Status: Mostly delivered under 001_Project_Setup

The FastAPI app factory, Clean Architecture layer folders
(`api/core/domain/services/repositories/db`), environment-driven config,
structured logging, and a health endpoint all exist — see
[docs/architecture/01_SYSTEM_ARCHITECTURE.md](../architecture/01_SYSTEM_ARCHITECTURE.md).
**Remaining scope, not yet done**: standardized error-response format,
request-logging middleware, exception handlers, and a task scheduler wiring
point (APScheduler is named in the tech stack but wasn't wired in until this
review — see `backend/app/core/scheduler.py`, added empty pending the first
feature that needs it, same pattern as `domain/services/repositories`).

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
