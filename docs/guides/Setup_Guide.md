# Setup Guide

Step-by-step local setup for Digital Chintu. For the day-to-day development
workflow once you're up and running, see
[Developer_Guide.md](Developer_Guide.md).

## 1. Prerequisites

| Tool | Minimum version | Check with |
|---|---|---|
| Python | 3.12 | `python --version` |
| Node.js | 22 | `node --version` |
| Docker (optional) | any recent | `docker --version` |
| Git | any recent | `git --version` |

On Windows without `make` installed (native PowerShell, not Git Bash/WSL),
skip the `make` commands below and run the underlying commands directly —
each package's own `README.md` (`backend/README.md`,
`frontend-dashboard/README.md`) has them.

## 2. Clone and bootstrap

```bash
git clone <repo-url>
cd digital-chintu
```

Choose native setup or Docker.

### Option A — native (backend + frontend run directly on your machine)

```bash
# Linux / macOS / Raspberry Pi OS / Git Bash & WSL on Windows
./scripts/setup.sh
```

```powershell
# Native Windows PowerShell
./scripts/setup.ps1
```

This creates `backend/.venv`, installs backend dependencies
(`pip install -e ".[dev]"`), installs frontend dependencies (`npm install`),
and copies every `.env.example` to `.env` (root, `backend/`,
`frontend-dashboard/`) where one doesn't already exist. Safe to re-run —
it won't recreate an existing venv or overwrite an existing `.env`.

### Option B — Docker

```bash
cp .env.example .env
docker compose up --build
```

No local Python/Node toolchain needed. See
[docs/architecture/07_DEPLOYMENT.md](../architecture/07_DEPLOYMENT.md) for
what this actually builds and runs.

## 3. Start the services (native)

In two separate terminals, from the repo root:

```bash
make backend-dev     # http://localhost:8000
make frontend-dev    # http://localhost:5173
```

Without `make`:

```bash
# Terminal 1
cd backend
.venv\Scripts\python.exe -m uvicorn app.main:app --reload   # Windows
# source .venv/bin/activate && uvicorn app.main:app --reload  # Linux/macOS/RPi

# Terminal 2
cd frontend-dashboard
npm run dev
```

## 4. Verify it's working

```bash
curl http://localhost:8000/api/v1/health
# {"status":"ok","app_name":"Chintu","environment":"development"}
```

Open `http://localhost:5173` — the header should show the same `app_name`
from that response (not a hardcoded string), and the "Backend connection"
card should say the backend is `ok`. Click the theme toggle — the page
should switch light/dark and remember your choice on reload.

## 5. Run the test suites

```bash
make test                       # backend (pytest) + frontend (vitest), unit + integration
cd tests && npm install && npx playwright install --with-deps chromium
npm run test:e2e                # E2E, from tests/ — auto-starts both servers
```

See [docs/architecture/08_TESTING_STRATEGY.md](../architecture/08_TESTING_STRATEGY.md)
for what each tier covers.

## 6. Common tasks reference

```bash
make setup          # re-run bootstrap
make lint            # Ruff + mypy (backend), ESLint + tsc (frontend)
make format           # Black (backend), Prettier (frontend)
make test            # unit + integration tests, both packages
make docker-up       # docker compose up --build
make docker-down     # docker compose down
```

## Troubleshooting

**`ModuleNotFoundError: pydantic_core._pydantic_core` or similar after
re-running setup.** Your `backend/.venv` was likely rebuilt against a
different Python interpreter than the one that originally installed its
packages (this can happen if your system has more than one `python`/`python3`
on `PATH`, e.g. a Microsoft Store Python alias). Fix: delete `backend/.venv`
entirely and re-run `scripts/setup.sh` / `setup.ps1`.

**Frontend loads but shows "Could not reach the backend."** The backend
isn't running, isn't on port 8000, or `frontend-dashboard/.env`'s
`VITE_API_BASE_URL` doesn't match where it's actually listening. Restart the
backend and confirm `curl http://localhost:8000/api/v1/health` works first.

**Port already in use.** Something else is bound to 8000 or 5173. Either
stop it, or override `BACKEND_PORT`/`FRONTEND_PORT` in your root `.env`
(Docker) — for native dev, pass `--port` to `uvicorn` or set Vite's
`--port` flag, and update `VITE_API_BASE_URL`/`CORS_ORIGINS` to match.

**`docker compose up` fails to pull an image on Raspberry Pi.** Confirm
Docker itself supports your Pi's architecture (arm64 vs armv7) — all three
base images used here (`python:3.12-slim`, `node:22-alpine`, `nginx:alpine`)
publish both, but very old Pi OS/Docker installs may not resolve them
correctly.
