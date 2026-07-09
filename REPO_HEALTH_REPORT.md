# Repository Health Report

**Date**: 2026-07-09
**Scope**: Full repository at the frozen foundation baseline (`v0.2.0`, commit
`893896e` — UI Framework + Architecture Review — plus this documentation
freeze pass on top). Every check below was actually run this session, not
carried over from an earlier report.

## Freeze declaration

The foundation (`docs/features/001`–`009`) is **frozen at `v0.2.0`**: built,
reviewed twice (a UI-specific pass, then a full architecture review), and
every approved, non-feature finding from both passes fixed. No product
feature (reminders, voice, AI, plugins, media) has started. This report is
the verification gate for that freeze — see [PROJECT_STATUS.md](PROJECT_STATUS.md)
for the narrative snapshot and [CHANGELOG.md](CHANGELOG.md)'s `[0.2.0]` entry
for what changed.

## Build / lint / test — verified this session

| Check | Result |
|---|---|
| Backend Ruff | ✅ All checks passed |
| Backend mypy `--strict` | ✅ No issues found (26 source files) |
| Backend `import-linter` | ✅ 1 contract kept, 0 broken |
| Backend Pytest | ✅ 21/21 passed |
| Backend coverage | 97% statements (99 stmts, 3 missed — all in `db/base.py`'s empty `DeclarativeBase`) |
| Frontend ESLint (incl. `import/no-restricted-paths`) | ✅ 0 problems |
| Frontend `tsc -b --noEmit` | ✅ Clean |
| Frontend Vitest | ✅ 58/58 passed (20 files) |
| Frontend coverage | 98.21% stmts / 97.4% branches / 100% funcs / 100% lines |
| E2E (Playwright, `tests/e2e/smoke.spec.ts`) | ✅ 4/4 passed |

Two frontend coverage gaps, both deliberate: `ThemeProvider`'s SSR guard and
`MobileNav`'s empty-focusable-list guard (see
[08_TESTING_STRATEGY.md](docs/architecture/08_TESTING_STRATEGY.md)). Backend's
only gap is likewise deliberate — nothing to test in `db/base.py` until a
real model exists.

## Architecture conformance

Both import-direction contracts verified against a real violation this
session (injected, caught, reverted), not just configured:

- Backend: `import-linter` — `api -> services -> repositories -> domain`, one-way.
- Frontend: ESLint's `import/no-restricted-paths` — `src/api`/`src/theme`
  can't import `src/components`/`src/routes`/`src/app`. (Needed an explicit
  `.ts`/`.tsx` resolver setting to work at all — the default resolver
  silently ignores TypeScript imports; see
  [DEPENDENCY_GRAPH.md](DEPENDENCY_GRAPH.md).)

## Dependency health

| | Result |
|---|---|
| `npm audit` (frontend-dashboard, all deps) | ✅ 0 vulnerabilities |
| Backend vulnerability scan | ❌ Not run — `pip-audit` isn't installed or wired in; tracked in [BACKLOG.md](BACKLOG.md)'s Security section |
| Backend outdated dev deps (non-security) | `black`, `mypy`, `pytest`, `pytest-cov`, `pydantic_core` all have newer releases available — none pinned in a way that blocks upgrading, just not proactively bumped |

No dependency-vulnerability scanning is wired into CI for either package —
this is a known, already-tracked gap, not new.

## Documentation completeness

| Set | Filled in | Stub / not started |
|---|---|---|
| `docs/features/` (50 files) | 9 (`001`–`009`) | 41 (`010`–`050`, untouched templates) |
| `docs/architecture/` (10 files) | 7 (`01`,`02`,`04`,`06`,`07`,`08`,`09`) | 3 (`03_DATABASE_DESIGN`, `05_PLUGIN_SDK`, `10_CLAUDE_CODE_RULES` — nothing to document until models/plugins exist, or rules to write) |
| `docs/guides/` (6 files) | 4 | 2 (`Prompt_Usage.md`, `Release_Process.md`) |
| `docs/SDS/` (41 files) | 0 | 41 — all still template stubs, per `CLAUDE.md` |
| Root-level docs | `README.md`, `CHANGELOG.md`, `PROJECT_STATUS.md`, `ROADMAP.md`, `BACKLOG.md`, `DEPENDENCY_GRAPH.md`, `ARCHITECTURE_REVIEW_REPORT.md`, `CONTRIBUTING.md`, `DEVELOPMENT.md`, this report — all present | — |

This matches the project's own stated plan (`docs/features` are meant to be
filled in feature-by-feature, `docs/SDS` fleshed out alongside them) — not a
gap introduced by this freeze.

## Platform verification (carried forward, not re-run this session)

| Platform | Native dev | Docker |
|---|---|---|
| Windows | ✅ Verified (architecture review session) | ✅ Verified (architecture review session) |
| Linux | Same code path; not independently re-run | Same image; not independently re-run |
| Raspberry Pi | Not run on physical hardware | Multi-arch images confirmed by base-image choice; not run on physical hardware |

No code, Docker, or CI config changed in this documentation-freeze pass, so
this table is unchanged from [PROJECT_STATUS.md](PROJECT_STATUS.md)'s prior
verification — re-running it wouldn't produce new information.

## Git state

Baseline commit `893896e` ("ARCHITECTURE REVIEW REPORT") carries the UI
Framework build and the architecture-review fixes. This freeze pass adds
14 more changed/new files on top (version bumps, `CHANGELOG.md`/
`PROJECT_STATUS.md`/`ROADMAP.md`/`BACKLOG.md` updates, architecture-doc
corrections, `CONTRIBUTING.md`, `DEVELOPMENT.md`, this report) — not yet
committed.

## Risk register (unchanged by this pass — see BACKLOG.md for full detail)

Highest-impact open items, none of which are foundation defects:

1. No plugin extension point — `010_Plugin_Framework` is next up and needs
   one before it can start.
2. No authentication/authorization on any endpoint — must land before any
   feature exposes sensitive data or write operations.
3. No dependency-vulnerability scanning in CI (backend or frontend).
4. Raspberry Pi and native-PowerShell paths verified by config/logic
   inspection, not by running on the actual target.

## Verdict

**Foundation is healthy and frozen.** Every automated check that can run in
this environment passes; the two intentionally-uncovered code paths and the
open backlog items are documented, not hidden. Safe to build
`010_Plugin_Framework` on top of.
