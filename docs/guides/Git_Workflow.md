# Git Workflow

Lightweight conventions, matching what's already in use in this repo. Not a
formal policy — revisit once there's more than one regular contributor.

## Commits

Conventional commits, already used throughout this repo's history:
`feat:`, `fix:`, `docs:`, `chore:`, `test:`, `refactor:`. Scope to a single
logical change; prefer several small commits over one large one when a
change touches unrelated concerns (e.g. a dependency bump and a bug fix are
two commits, not one).

## Branches

Name branches after the `docs/features/NNN_Feature_Name.md` they implement,
lowercased and hyphenated: `feature/017-reminders`,
`feature/010-plugin-framework`. For work that isn't a numbered feature (a
fix, a chore, an architecture change like this review):
`fix/short-description`, `chore/short-description`.

## Pull requests

- CI (`.github/workflows/ci.yml`) must be green before merging: backend
  (Ruff, Black, mypy, import-linter, Pytest) on Linux + Windows, frontend
  (ESLint, Prettier, tsc, Vitest, build) on Linux.
- Run `make lint && make test` locally first — CI matches these exactly, so
  there shouldn't be surprises.
- Update the relevant `docs/features/NNN_*.md` (Deliverables, Acceptance
  Criteria, Definition of Done) and `CHANGELOG.md`'s `[Unreleased]` section
  as part of the same PR, not as a follow-up.
- Squash-merge to keep `main`'s history one-commit-per-feature/fix; keep the
  full history on the branch if you want it for review.

## What's still undecided

Formal branch-protection rules, required-reviewer counts, and a release/tag
process (`docs/guides/Release_Process.md` is still a stub) haven't been
established — don't invent them here; ask if they start to matter.
