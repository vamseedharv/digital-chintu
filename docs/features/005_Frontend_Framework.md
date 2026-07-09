# 005 Frontend Framework

## Status: Done

React + TypeScript + Vite + Tailwind CSS v4 + Framer Motion, ESLint/Prettier/tsc
strict mode, Vitest unit+integration tests — all set up in
`frontend-dashboard/`. Extended with a full UI Framework layer: application
shell, responsive sidebar/drawer navigation, `react-router` routing (with
404 and error-boundary pages), and a reusable component library
(`components/ui/`). See
[docs/architecture/02_REPOSITORY_STRUCTURE.md](../architecture/02_REPOSITORY_STRUCTURE.md).
No remaining scope for the framework itself; UI *features* built on top of it
(Dashboard, Settings, etc.) are separate, still-open docs below — this
feature intentionally contains no dashboard widgets, weather, reminders, AI,
or plugin content.

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
