# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository state

This repository currently contains **only planning/specification documents** — there is no source code yet (no backend, frontend, or tests have been created). Everything under `docs/` is a design specification meant to drive future implementation with Claude Code. Do not assume any build/lint/test tooling exists — check for `backend/`, `frontend-dashboard/`, `frontend-mobile/`, etc. before assuming they've been created, and set up tooling (per the stack below) the first time you actually scaffold code.

Because there is no code, there are no build/lint/test commands to document yet. Once implementation starts, update this file with the real commands (e.g. `pytest` invocation, `npm run` scripts) instead of guessing at them.

## What Digital Chintu is

Digital Chintu is a planned **open-source, self-hosted AI home assistant platform** (see [docs/Foundation/01_Project_Vision.md](docs/Foundation/01_Project_Vision.md)):
- Multi-client: Smart Display, Web dashboard, Android (iOS later)
- Backend-first design
- Assistant name is configurable at onboarding (not hardcoded)
- No paid subscriptions required for core functionality
- Plugin architecture for extensibility (e.g. Home Assistant integration)
- Offline-first where practical
- Must run on Raspberry Pi, Linux, Windows, and Docker

## Planned architecture

From [docs/Foundation/02_System_Architecture.md](docs/Foundation/02_System_Architecture.md):
- Core Backend: FastAPI, using Clean Architecture with Service Layer + Repository Layer
- Plugin Engine (loads plugins like Home Assistant, custom plugins)
- Database: SQLite via SQLAlchemy
- REST + WebSocket API for real-time updates
- React Dashboard (web client)
- Android client, future iOS client
- Voice pipeline: OpenWakeWord (wake word) → Whisper.cpp (STT) → Piper (TTS)

## Planned tech stack

(From [docs/Foundation/04_Tech_Stack.md](docs/Foundation/04_Tech_Stack.md))

| Area | Choices |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy, SQLite, APScheduler |
| Frontend | React, TypeScript, Vite, TailwindCSS, Framer Motion |
| Voice | OpenWakeWord, Whisper.cpp, Piper |
| Testing | Pytest (backend), Vitest (frontend unit), Playwright (E2E) |
| Python lint/format | Ruff, Black, type hints required |
| TypeScript lint/format | ESLint, Prettier, strict mode |

## Planned repository layout

(From [docs/Foundation/03_Repository_Structure.md](docs/Foundation/03_Repository_Structure.md)) — this is a monorepo target, not yet created:

```
backend/            FastAPI backend
frontend-dashboard/ React web dashboard
frontend-mobile/    Android (and future iOS) client
shared/             Shared types/utilities across clients
plugins/            Plugin implementations (Home Assistant, custom, etc.)
docs/               Specifications (this folder)
docker/             Docker/deployment config
scripts/            Dev/ops scripts
tests/              Cross-cutting test suites
```

## Documentation structure — how to navigate `docs/`

The docs are organized in layers with different levels of detail; when implementing, read the most specific relevant doc first, but check the Foundation pack for repo-wide conventions:

- **`docs/Foundation/`** — the initial foundation pack (numbered 00–10). This is the most concrete/authoritative source for architecture, tech stack, repo layout, and coding standards *before any feature work begins*. Per [10_Master_Claude_Prompt.md](docs/Foundation/10_Master_Claude_Prompt.md), foundation work should be completed (backend/frontend skeleton, Docker, CI/CD) before any feature implementation starts.
- **`docs/SDS/`** — the Software Design Specification, organized by domain area (`00_Platform`, `01_UI`, `02_Backend`, `03_Voice`, `04_Productivity`, `05_Media`, `06_AI`, `07_Clients`, `08_Plugins`, `09_Operations`). Each doc is currently a template stub following a fixed 15-section outline (Context, User Stories, Functional/Non-functional Requirements, UX Flow, UI Components, Backend Design, Database, APIs, WebSocket Events, Configuration, Test Plan, Manual QA, Claude Code Prompt, Definition of Done) — sections are largely unfilled placeholders (`(TODO)`) and need to be fleshed out with real requirements before/while a given feature is implemented.
- **`docs/features/`** — numbered, sequential feature specs (001 through 050) intended to be implemented roughly in order, each building on the previous ones without breaking them. Also currently template stubs with recurring constraints: must run on Raspberry Pi/Linux/Windows/Docker, support dark and light themes, require no paid services, and be independently testable.
- **`docs/architecture/`** and **`docs/guides/`** — currently one-line placeholder stubs for architecture deep-dives (system architecture, DB design, API guidelines, plugin SDK, security, deployment, testing strategy, UI design system) and contributor guides (coding standards, git workflow, release process). Treat these as TODO — fill them in as the corresponding real decisions get made, don't invent content that contradicts the Foundation pack.

## Recurring constraints across specs

These show up repeatedly across the spec docs and should hold for any implementation work in this repo:
- Cross-platform: Raspberry Pi, Linux, Windows, and Docker
- No paid subscriptions/services required for core features
- Dark mode and light mode support in UI, with a glassmorphism-influenced design language; responsive and accessible
- Assistant name must remain a runtime-configurable setting, never hardcoded
- Each feature should be independently testable and must not break previously implemented features
- Conventional commits are expected for any generated commit
