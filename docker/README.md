# docker

Shared Docker documentation for Digital Chintu.

Per-service `Dockerfile`s live next to their service (`backend/Dockerfile`,
`frontend-dashboard/Dockerfile`) rather than here, so each image only builds
the context it needs. This folder holds cross-cutting notes and any shared
compose fragments that don't belong to a single service.

## Running everything with Docker

From the repository root:

```bash
cp .env.example .env
docker compose up --build
```

This builds and starts:

- `backend` — FastAPI app served by Uvicorn, SQLite data persisted in a named volume.
- `frontend-dashboard` — the React dashboard, built and served via Nginx.

Both base images (`python:3.12-slim`, `node:22-alpine`, `nginx:alpine`) are
multi-arch, so the same `docker-compose.yml` works unmodified on Linux, Windows
(Docker Desktop), and Raspberry Pi (arm64/armv7).

See the root [docker-compose.yml](../docker-compose.yml) and [README.md](../README.md)
for the full quickstart.
