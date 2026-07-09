# Contributing

Thanks for considering a contribution to Digital Chintu. This is a young,
foundation-stage project (see [PROJECT_STATUS.md](PROJECT_STATUS.md)) — the
process below is intentionally lightweight and will grow once there's more
than one regular contributor.

## Before you start

- Read [CLAUDE.md](CLAUDE.md) for repository-wide conventions and
  [ROADMAP.md](ROADMAP.md) / [BACKLOG.md](BACKLOG.md) for what's already
  planned — new scope should fit `docs/features/001`–`050`'s numbering, not
  invent parallel scope. If you're proposing something not already listed
  there, open an issue to discuss it first.
- Set up your local environment: [DEVELOPMENT.md](DEVELOPMENT.md).

## Workflow

1. **Branch**: name it after the `docs/features/NNN_Feature_Name.md` it
   implements (`feature/017-reminders`), or `fix/short-description` /
   `chore/short-description` for non-numbered work. See
   [docs/guides/Git_Workflow.md](docs/guides/Git_Workflow.md).
2. **Commit**: [Conventional Commits](https://www.conventionalcommits.org/)
   (`feat:`, `fix:`, `docs:`, `chore:`, `test:`, `refactor:`), one logical
   change per commit.
3. **Code**: follow [docs/guides/Developer_Guide.md](docs/guides/Developer_Guide.md)
   (where new code goes, testing patterns, config) and
   [docs/guides/Coding_Standards.md](docs/guides/Coding_Standards.md) (lint/
   format/type rules actually enforced). Never break a previously
   implemented feature.
4. **Test**: add unit + integration tests as you go, not after. Match the
   existing three-tier structure — see
   [docs/architecture/08_TESTING_STRATEGY.md](docs/architecture/08_TESTING_STRATEGY.md).
5. **Document**: update the relevant `docs/features/NNN_*.md`'s
   Deliverables/Acceptance Criteria/Definition of Done and
   [CHANGELOG.md](CHANGELOG.md)'s `[Unreleased]` section in the same PR, not
   as a follow-up.
6. **Verify locally** before opening a PR:
   ```bash
   make lint && make test
   ```
   CI (`.github/workflows/ci.yml`) runs the same checks (backend on Linux +
   Windows, frontend on Linux) and must be green before merging.
7. **Open a PR** against `main`. Squash-merge is preferred to keep `main`'s
   history one-commit-per-feature/fix.

## Reporting bugs / proposing features

Open a GitHub issue. For bugs, include steps to reproduce and which platform
(Linux/Windows/Raspberry Pi/Docker) you hit it on — this project explicitly
targets all four (see [CLAUDE.md](CLAUDE.md)'s recurring constraints).

## Code of conduct

Not formally adopted yet. Be respectful and constructive; ask if this needs
to be established before it becomes a problem.
