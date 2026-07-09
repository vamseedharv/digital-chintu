# 07 Deployment

Status: **implemented** for Docker Compose (single-host); native process deployment is
supported the same way as local dev (see [docs/guides/Setup_Guide.md](../guides/Setup_Guide.md)).

## Docker Compose (recommended)

```bash
cp .env.example .env
docker compose up --build
```

This builds and runs two services (`docker-compose.yml`):

| Service | Image base | Exposes | Notes |
|---|---|---|---|
| `backend` | `python:3.12-slim` | `${BACKEND_PORT:-8000}` → 8000 | Runs as non-root user `chintu`; SQLite data and logs persisted in named volumes (`backend-data`, `backend-logs`) |
| `frontend-dashboard` | `node:22-alpine` (build) → `nginx:alpine` (runtime) | `${FRONTEND_PORT:-5173}` → 80 | Multi-stage: Vite build, then static files served by Nginx; waits for `backend`'s healthcheck before starting |

All three base images (`python:3.12-slim`, `node:22-alpine`, `nginx:alpine`)
are multi-arch, so the same compose file runs unmodified on Linux, Windows
(Docker Desktop), and Raspberry Pi (arm64/armv7).

### Configuration

Every backend setting is passed through from the repo-root `.env` (loaded
automatically by `docker compose`) — see `.env.example` for the full list
(`APP_NAME`, `APP_ENV`, `DEBUG`, `LOG_LEVEL`, `CORS_ORIGINS`, port overrides).
`VITE_API_BASE_URL` is a **build-time** argument (Vite inlines `VITE_*` vars
at build, not at container start), so it must point at wherever the backend
will be reachable *from the browser* — not from inside the Docker network.

If you change `BACKEND_PORT` or `FRONTEND_PORT`, also update
`VITE_API_BASE_URL` / `CORS_ORIGINS` to match — they aren't derived from the
port variables automatically.

### Image build details worth knowing

- **`backend/Dockerfile`** installs dependencies in a separate layer from
  the application source (against a throwaway placeholder package), so
  editing `app/` code doesn't force a full dependency reinstall on rebuild —
  only `pyproject.toml` changes do.
- **`.dockerignore`** exists for both services — without it, the host's
  `node_modules`/`.venv` would be sent into the build context.
- Both services have a Compose `healthcheck`; `frontend-dashboard` won't
  start serving until `backend` reports healthy
  (`depends_on: condition: service_healthy`).

### Common operations

```bash
docker compose ps                       # check health status
docker compose logs -f backend          # tail backend logs
docker compose build --no-cache backend # force a full rebuild
docker compose down                     # stop + remove containers/network (keeps volumes)
docker compose down -v                  # also remove the named volumes (destroys SQLite data)
```

## Native (non-Docker) deployment

Same commands as local dev — run the backend with a production ASGI
process (`uvicorn app.main:app --host 0.0.0.0 --port 8000`, no `--reload`)
behind whatever reverse proxy/process manager the host provides, and serve
the frontend's `npm run build` output (`frontend-dashboard/dist/`) via any
static file server. Set `DEBUG=false` and `APP_ENV=production` in
`backend/.env` — the code defaults to `debug=False` already, so this only
matters if you're relying on a `.env` file at all; see
[06_SECURITY.md](06_SECURITY.md).

## Not yet implemented

- No CI/CD pipeline publishes images or deploys anywhere — `.github/workflows/ci.yml`
  only runs lint/type-check/tests on push and PR.
- No orchestration beyond Compose (no Kubernetes manifests, no multi-host setup).
- No backup/restore tooling for the SQLite volume (tracked as a future feature,
  see `docs/features/036_Backup_Restore.md`).
