# backend

FastAPI backend for Digital Chintu, structured as a Clean Architecture skeleton:

```
app/
  main.py          FastAPI app factory (entrypoint: app.main:app)
  core/            Cross-cutting: configuration, logging, validation
  api/v1/          HTTP interface layer (routers, endpoints)
  domain/          Framework-independent entities/interfaces (settings; otherwise empty)
  services/        Application/business logic (settings; otherwise empty)
  repositories/    Data-access implementations (settings; otherwise empty)
  db/              SQLAlchemy engine/session/declarative base/models
alembic/           Migrations (see docs/architecture/03_DATABASE_DESIGN.md)
tests/
  unit/            Isolated tests of a single module (config, logging, db session, settings)
  integration/     Tests of the wired-up FastAPI app via TestClient (routing, middleware, settings together)
```

The `domain`, `services`, and `repositories` packages started empty and now
hold the settings feature's layers — see
[docs/features/001_Project_Setup.md](../docs/features/001_Project_Setup.md)
for why they existed ahead of any real feature, and
[docs/features/008_Settings.md](../docs/features/008_Settings.md) for the
first thing to actually land in them.

## Setup

```bash
python -m venv .venv
# Linux/macOS/Raspberry Pi:
source .venv/bin/activate
# Windows PowerShell:
.venv\Scripts\Activate.ps1

pip install -e ".[dev]"
cp .env.example .env
alembic upgrade head
```

## Run

```bash
alembic upgrade head   # apply any new migrations first — safe to re-run, no-op if already current
uvicorn app.main:app --reload
```

The API is served at `http://localhost:8000`; health check at
`http://localhost:8000/api/v1/health`.

## Test

```bash
pytest                    # runs unit + integration, with coverage (see pyproject.toml)
pytest tests/unit
pytest tests/integration
pytest --cov-report=html  # writes htmlcov/index.html
```

## Lint & format

```bash
ruff check .
mypy .
black --check .

# to auto-fix:
ruff check . --fix
black .
```

## Configuration

All settings are environment variables (see `.env.example`), typed and
validated by a single `Settings` model (`pydantic-settings`,
`app/core/config.py`), cached process-wide via `get_settings()`. Beyond the
infrastructure basics (`APP_ENV`, `DEBUG`, `LOG_LEVEL`, `CORS_ORIGINS`,
`DATABASE_URL`), this includes assistant-identity defaults: `APP_NAME`,
`WAKE_WORD`, `DEFAULT_THEME` (`light`/`dark`/`system`), and
`DEFAULT_LANGUAGE` (a BCP-47-style tag, e.g. `en-US`) — all runtime-overridable
via environment variable, never hardcoded. `APP_ENV=production` combined
with `DEBUG=true` is a validation error, not just a discouraged default.
The non-secret subset is readable via `GET /api/v1/config`. `app_name` and
`default_theme` are now also writable at runtime via `GET`/`PATCH
/api/v1/settings` — persisted as DB-backed overrides on top of these
env-driven defaults (see
[docs/features/008_Settings.md](../docs/features/008_Settings.md) and
[docs/architecture/03_DATABASE_DESIGN.md](../docs/architecture/03_DATABASE_DESIGN.md)).
`wake_word` and `default_language` remain env-only for now. A dedicated
onboarding flow is still a future feature
([009_Assistant_Onboarding.md](../docs/features/009_Assistant_Onboarding.md)).
