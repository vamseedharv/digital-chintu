# 007 Dashboard

## Status: Done

The home route (`/`) is now a real widget-hosting dashboard, not the
diagnostic-only page it was: a greeting naming the configured assistant, a
live clock, the existing `HealthStatus` backend check (unchanged, now one
tile among several), and placeholder tiles for Weather/Reminders/To-do/
Shopping List. See
[docs/SDS/01_UI/012_Dashboard.md](../SDS/01_UI/012_Dashboard.md) for the
full requirements, UX flow, and component breakdown, and
[docs/architecture/09_UI_DESIGN_SYSTEM.md](../architecture/09_UI_DESIGN_SYSTEM.md)
for the `WidgetCard` shell added to the component library. No backend
changes were needed — see 012_Dashboard.md's "Backend Design" for why.

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
