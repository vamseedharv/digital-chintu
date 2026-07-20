# backend

FastAPI backend for Digital Chintu, structured as a Clean Architecture skeleton:

```
app/
  main.py          FastAPI app factory (entrypoint: app.main:app)
  core/            Cross-cutting: configuration, logging
  api/v1/          HTTP interface layer (routers, endpoints)
  domain/          Framework-independent entities/interfaces (empty — no features yet)
  services/        Application/business logic (empty — no features yet)
  repositories/    Data-access implementations (empty — no features yet)
  db/              SQLAlchemy engine/session/declarative base
tests/
  unit/            Isolated tests of a single module (config, logging, db session)
  integration/     Tests of the wired-up FastAPI app via TestClient (routing, middleware, config together)
```

The `domain`, `services`, and `repositories` packages are intentionally empty.
They exist so the first real feature has a place to land without restructuring
the project — see [docs/features/001_Project_Setup.md](../docs/features/001_Project_Setup.md)
for why database models and business logic are out of scope here.

## Setup

```bash
python -m venv .venv
# Linux/macOS/Raspberry Pi:
source .venv/bin/activate
# Windows PowerShell:
.venv\Scripts\Activate.ps1

pip install -e ".[dev]"
cp .env.example .env
```

## Run

```bash
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
The non-secret subset is readable via `GET /api/v1/config`; there's no write
API yet — an onboarding/settings UI to change any of this at runtime is a
future feature ([docs/features/008_Settings.md](../docs/features/008_Settings.md),
[009_Assistant_Onboarding.md](../docs/features/009_Assistant_Onboarding.md)).
