# Development

Local dev quickstart. For the full step-by-step walkthrough (prerequisites,
troubleshooting, verification) see
[docs/guides/Setup_Guide.md](docs/guides/Setup_Guide.md); for day-to-day
conventions once you're running (where new code goes, testing patterns,
config) see [docs/guides/Developer_Guide.md](docs/guides/Developer_Guide.md).
This file is the short version.

## Requirements

Python 3.12+, Node.js 22+, Git; Docker is optional. Supported platforms:
Linux, Windows, Raspberry Pi (arm64/armv7), and Docker.

## Bootstrap

```bash
# Linux / macOS / Raspberry Pi OS / Git Bash & WSL on Windows
./scripts/setup.sh
```

```powershell
# Native Windows PowerShell
./scripts/setup.ps1
```

Creates `backend/.venv`, installs backend (`pip install -e ".[dev]"`) and
frontend (`npm install`) dependencies, and copies every `.env.example` to
`.env` where one doesn't already exist. Safe to re-run.

## Run it

```bash
make backend-dev     # FastAPI, http://localhost:8000
make frontend-dev    # Vite dev server, http://localhost:5173
```

On native Windows without `make`, run the underlying commands from
[backend/README.md](backend/README.md) and
[frontend-dashboard/README.md](frontend-dashboard/README.md) directly.

Verify: `curl http://localhost:8000/api/v1/health` should return
`{"status":"ok",...}`, and `http://localhost:5173` should show that same
`app_name` in the sidebar.

## Test, lint, format

```bash
make test      # Pytest (backend) + Vitest (frontend), unit + integration
make lint      # Ruff + mypy + import-linter (backend); ESLint + tsc (frontend)
make format    # Black (backend); Prettier (frontend)
```

A single test:

```bash
pytest tests/unit/test_config.py::test_defaults_are_safe_for_an_unconfigured_deployment  # backend, from backend/
npx playwright test e2e/smoke.spec.ts -g "dashboard loads"                                # E2E, from tests/
```

End-to-end (Playwright, spans both services, not wired into CI — see
[tests/README.md](tests/README.md)):

```bash
cd tests && npm install && npx playwright install --with-deps chromium
npm run test:e2e
```

Run `make lint && make test` before opening a PR — CI
(`.github/workflows/ci.yml`) runs the same checks and must be green before
merging. See [docs/guides/Coding_Standards.md](docs/guides/Coding_Standards.md)
for exactly what's enforced.

## Docker instead of native

```bash
cp .env.example .env
docker compose up --build
```

See [docs/architecture/07_DEPLOYMENT.md](docs/architecture/07_DEPLOYMENT.md).

## Where things live

Clean Architecture on the backend (`api → services → repositories → domain`,
enforced by `import-linter`), a small component library plus an application
shell on the frontend (`app/` composition root, `routes/` pages,
`components/ui/` + `components/layout/`, `theme/`, `api/`, enforced by
ESLint's `import/no-restricted-paths`) — see
[docs/architecture/01_SYSTEM_ARCHITECTURE.md](docs/architecture/01_SYSTEM_ARCHITECTURE.md)
and [docs/architecture/02_REPOSITORY_STRUCTURE.md](docs/architecture/02_REPOSITORY_STRUCTURE.md)
for the full picture, or
[docs/guides/Developer_Guide.md](docs/guides/Developer_Guide.md) for where a
new feature's code should actually go.

## Troubleshooting

See [docs/guides/Setup_Guide.md](docs/guides/Setup_Guide.md#troubleshooting)
for the common gotchas (venv rebuilt against a different Python, port
conflicts, Raspberry Pi image pulls).
