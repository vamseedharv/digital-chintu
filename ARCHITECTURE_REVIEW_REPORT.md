# Architecture Review Report

**Date**: 2026-07-09
**Scope**: Full repository as of the completed UI Framework feature (Project Setup
foundation + `frontend-dashboard` application shell, routing, theme, and component
library). Supersedes the pre-UI-Framework review from earlier this session — several
ratings below have moved since then.

## Review scope & input caveat

Reviewed against `docs/architecture/01_SYSTEM_ARCHITECTURE.md`,
`02_REPOSITORY_STRUCTURE.md`, and `09_UI_DESIGN_SYSTEM.md`, plus the actual code
(imports grepped, tests re-run, contrast measured in-browser — not assumed from the
docs). `docs/MASTER_EXECUTION_PLAN.md` still does not exist in this repo — referenced
by name in past requests but never found; flagging again in case it was meant to be
committed.

## Current metrics (verified this session, not carried over from memory)

| | |
|---|---|
| Backend tests | 21/21 passing, 97% statement coverage |
| Frontend tests | 58/58 passing (20 files), 98.19% stmts / 97.4% branches / 100% funcs / 100% lines |
| E2E tests | 4/4 passing |
| Architecture conformance | `import-linter`: 1 contract kept, 0 broken (backend only — see §3) |
| Contrast (measured, not eyeballed) | Muted text 4.55:1 light / 6.78:1 dark — both pass WCAG AA |

## Ratings by section

| # | Section | Rating | Change since last review |
|---|---|---|---|
| 1 | Architecture consistency | ⚠️ 3.5/5 | Unchanged — `docs/features/002`–`009` reconciliation still holds |
| 2 | Folder structure | ✅ 5/5 | Unchanged; `components/ui/`, `components/layout/`, `app/`, `routes/` added cleanly, matching documented conventions |
| 3 | Dependency direction | ✅ 4/5 | Backend enforced by `import-linter`; **frontend has no equivalent enforcement** — new gap, see below |
| 4 | Scalability | ⚠️ 3/5 | Unchanged — scheduler wired but idle, no plugin registration mechanism |
| 5 | Maintainability | ✅ 5/5 | **Improved** — duplication removed (`NavLinks`, `buttonStyles.ts`), docs kept in sync, coverage up |
| 6 | Raspberry Pi compatibility | ✅ 4/5 | Unchanged — still no physical-hardware run |
| 7 | Docker readiness | ✅ 4.5/5 | Unchanged |
| 8 | Cross-platform compatibility | ✅ 4/5 | Unchanged |
| 9 | Clean Architecture violations | ✅ 5/5* | Unchanged (backend layers still empty) |
| 10 | SOLID violations | ✅ 4/5 | Unchanged |
| 11 | Naming inconsistencies | ✅ 4.5/5 | **Improved** — `ThemeToggle`'s divergent glass recipe fixed; one deferred item remains (JSON casing) |
| 12 | Future plugin compatibility | ❌ 2/5 | Unchanged |
| 13 | **UI component architecture** *(new)* | ✅ 4.5/5 | New section — component library is real, deduplicated, and tested |
| 14 | **Frontend accessibility** *(new)* | ✅ 4/5 | New section — verified empirically this session |
| 15 | **Animation quality** *(new)* | ✅ 4.5/5 | New section — global reduced-motion support added |

*Rating 9 keeps its asterisk from the original review: no violation exists because the protected backend layers are still empty, not because a real feature has tested the boundary.

---

## Detailed findings

### 1–12: Carried forward from the prior review

Sections 1, 2, 4, 6, 7, 8, 9, 10, 12 are unchanged from the architecture review
conducted earlier this session — none of that work touched backend scalability,
Raspberry Pi/Docker/cross-platform posture, Clean Architecture boundaries, SOLID, or
the plugin gap. Re-read that review's detail if you need the full reasoning; it still
holds.

**§3 Dependency direction — new gap surfaced.** The backend's `api -> services ->
repositories -> domain` direction is enforced by `import-linter` in CI. The frontend
has an equivalent, informally-documented direction (`components` → `api`/`theme`,
never the reverse) but **nothing enforces it** — no `eslint-plugin-import`
`no-restricted-paths` rule, no `dependency-cruiser`. This was tolerable with two
components; now there are 17 frontend modules across `app/`, `components/ui/`,
`components/layout/`, `routes/`, and `theme/`. Recommend adding lint-time enforcement
before the component count grows further — see Priority list below.

**§5 Maintainability — improved, with evidence.** The UI Framework review this
session found and fixed two real instances of component duplication (`Sidebar`/
`MobileNav`'s nav-link rendering; `NotFoundPage`/`ErrorPage`'s button-styled `Link`)
and one accessibility regression hiding inside that duplication (`MobileNav`'s copy
was silently missing a focus ring `Sidebar`'s had — exactly the kind of drift
duplication invites). Both are now single-source-of-truth (`NavLinks`,
`buttonStyles.ts`). Documentation (`docs/architecture/09_UI_DESIGN_SYSTEM.md`,
`CHANGELOG.md`, `BACKLOG.md`) was updated in the same pass, not left to drift.

**§11 Naming inconsistencies — one fixed, one still deferred.** `ThemeToggle`
previously hand-rolled a translucent-blur style close to but subtly different from
the `.glass` utility (`bg-white/60` + `backdrop-blur` vs. `.glass`'s `/70` +
`backdrop-blur-md`) — fixed, now uses `.glass` directly. Still deferred (correctly,
per its own documented trigger): backend `snake_case` JSON vs. frontend's
verbatim-copied interfaces, revisit when a second client/OpenAPI-generated client
exists.

### 13. UI component architecture *(new section)*

`components/ui/` (`Button`, `LinkButton`, `Card`, `Spinner`, `Skeleton`, `EmptyState`,
`Heading`, `Text`, `buttonStyles.ts`) and `components/layout/` (`PageContainer`,
`NavLinks`, `Sidebar`, `MobileNav`) form a real, if still small, reusable library —
not just "some components that happen to be reused." Evidence: `Button` and
`LinkButton` share one styling function rather than two implementations; `Sidebar`
and `MobileNav` share one nav-rendering component rather than two. Every primitive has
direct unit test coverage. Gap: no equivalent of `import-linter` for the frontend
(see §3) — the library's internal consistency currently depends on someone noticing
duplication in review, which is exactly how the two instances above went unnoticed
until this pass.

### 14. Frontend accessibility *(new section)*

Semantic landmarks, skip-to-content link, `aria-label`s on icon-only controls,
`NavLink`'s automatic `aria-current="page"`, and (as of this session) a full Tab
focus trap in `MobileNav` and a focus-visible ring on every interactive control
including `ThemeToggle` (previously missing). Contrast was **measured**, not assumed:
a canvas-based sRGB extraction + the real WCAG relative-luminance formula run
in-browser gave 4.55:1 (light) / 6.78:1 (dark) for the muted-text case, both passing
AA. Gap: `EmptyState`'s icon-plus-heading pattern hasn't been checked against a screen
reader for redundant announcement (icon is `aria-hidden`, heading carries the text —
likely fine, not independently verified with an actual screen reader).

### 15. Animation quality *(new section)*

`<MotionConfig reducedMotion="user">` at the app root (`main.tsx`) means every Framer
Motion animation in the app respects `prefers-reduced-motion` automatically — added
this session, previously absent everywhere. `Card` now owns its entrance animation
directly (was duplicated as a manual wrapper in `HealthStatus`). Gap: `MobileNav`'s
backdrop and drawer-slide animations run independently rather than through one
shared transition config — harmless today (both are 0.2s), but would need
consolidating if either ever changes duration without the other following.

---

## Improvements, in priority order

1. **Add frontend dependency-direction enforcement** (§3) — `eslint-plugin-import`'s
   `no-restricted-paths` or `dependency-cruiser`, mirroring what `import-linter`
   already does for the backend. The two duplication bugs found this session were
   both *within* a layer, not a cross-layer violation, but the risk grows with the
   component count and there's currently zero tooling protecting against it.
2. **Design the plugin extension point** (§12, carried forward, still highest-impact
   unaddressed gap) — before or as part of `010_Plugin_Framework`.
3. **Verify `EmptyState` with an actual screen reader** (§14) — cheap to check, not
   yet done.
4. **Consolidate `MobileNav`'s two independent animation configs** (§15) — low
   priority, cosmetic-consistency only.
5. Everything else carried forward from the prior review (scheduler job
   registration, RPi/PowerShell hardware verification, security items) — unchanged,
   see `BACKLOG.md` for the full current list.

---

No code changes made in producing this report. Metrics and contrast figures were
re-verified this session (test runs, in-browser measurement), not carried over from
memory.
