# 006 Theme Engine

## Status: Done

Dark/light toggle (class-based, persisted, OS-preference default), a design
token layer (brand color ramp + `.glass` utility in `index.css`'s `@theme`
block), typography primitives (`Heading`, `Text`), and an icon system
(`lucide-react`) are all implemented — see
[docs/architecture/09_UI_DESIGN_SYSTEM.md](../architecture/09_UI_DESIGN_SYSTEM.md).
**Remaining scope, not yet done**: a custom spacing scale (Tailwind's default
is used as-is — sufficient so far) and a broader component library beyond
`components/ui/`'s current set — extract more primitives as real UI features
(Dashboard, Settings) need them, not speculatively.

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
