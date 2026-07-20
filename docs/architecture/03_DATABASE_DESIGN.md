# 03 Database Design

Status: **Implemented** — SQLite via SQLAlchemy, migrated with Alembic. The
`settings` table (`008_Settings`) is the first real schema; see
[docs/features/008_Settings.md](../features/008_Settings.md) for the
feature this backs.

## Why the first model is `settings`, not a Phase 4 feature

Earlier planning ([BACKLOG.md](../../BACKLOG.md),
[ROADMAP.md](../../ROADMAP.md)) expected `017_Reminders`/`018_Alarms`
(Phase 4) to introduce the first database model and Alembic together, on
the theory that nothing before Phase 4 genuinely needed persistence. That
held until Settings (008): a Settings feature that can't durably save a
change isn't a Settings feature — env vars can't be safely rewritten from a
running app, and a per-browser `localStorage` override (the pattern
`ThemeProvider` already used for the theme *toggle*) isn't sufficient for
settings that need to be the same across every client (Smart Display, web,
Android — see [docs/Foundation/01_Project_Vision.md](../Foundation/01_Project_Vision.md)).

This was flagged and decided explicitly, not assumed: Settings became the
first real DB model and introduced Alembic ahead of Phase 4. Phase 4 now
reuses this same Alembic setup rather than introducing it fresh — see
[BACKLOG.md](../../BACKLOG.md)'s "Resolved ahead of schedule".

## Engine and connection

SQLite, via SQLAlchemy 2.0's `Mapped`/`mapped_column` declarative style
(`backend/app/db/base.py`'s `Base`, `backend/app/db/session.py`'s
`engine`/`SessionLocal`/`get_db()` — unchanged infrastructure from
`001_Project_Setup`). `check_same_thread=False` is required because FastAPI
serves each request on a worker thread that didn't create the engine.
`DATABASE_URL` (env var, `backend/app/core/config.py`) is the single source
of truth for the connection string — Alembic reads the same value (see
"Migrations" below) rather than duplicating it.

## Schema

### `settings`

A generic key/value table — deliberately schema-less per individual
setting, so adding a new one is a new row, never a new column or a new
migration:

| Column | Type | Notes |
|---|---|---|
| `key` | `VARCHAR(64)`, primary key | Matches a `SettingKey` (`backend/app/domain/settings.py`) — today `app_name`, `default_theme`. |
| `value` | `TEXT`, not null | Plain text; the repository/service layer serializes and parses it (e.g. a `Theme` enum's `.value`). |
| `updated_at` | `DATETIME`, not null | Set on insert and update. |

A row's *absence* is meaningful: no row for a key means "use the env-driven
default" (`app.core.config.Settings`), resolved by
`app/services/settings_service.py`'s `SettingsService.get_effective_settings()`.
This is why the table has no row for every possible setting up front — only
overridden ones are ever written.

No indexes beyond the primary key — the table is small (one row per
managed setting) and every read is either a point lookup by `key` or a
full scan (`get_all()`), both fine unindexed at this scale.

## Migrations

[Alembic](https://alembic.sqlalchemy.org/), `backend/alembic/` +
`backend/alembic.ini`. `alembic/env.py` sets `sqlalchemy.url` from
`app.core.config.get_settings().database_url` at runtime — `alembic.ini`'s
own `sqlalchemy.url` is a placeholder, never actually read, so the
connection string is never duplicated between the app and its migrations.

**Migrations run as a separate step before the app starts, not from inside
FastAPI's lifespan.** `backend-dev`'s Makefile target and the Docker image's
`CMD` both do `alembic upgrade head && <start the app>`. This was a
deliberate choice over auto-migrating inside `lifespan()`: doing it there
would tie migration timing to whether `TestClient` happens to trigger the
ASGI lifespan for a given test (it doesn't, for a bare `TestClient(app)`),
risking either tests silently skipping migrations or — worse — tests
running real migrations against the developer's actual `DATABASE_URL` file.
Running `alembic upgrade head` as its own step sidesteps that entirely:
tests never invoke Alembic at all (see "Testing" below), and production
startup order is simple and explicit.

`0001_create_settings_table.py` is the only revision today. Both directions
are tested (`backend/tests/unit/test_migrations.py`, via the real `alembic`
CLI against a throwaway SQLite file) — `upgrade head` creates the table
with the expected columns, `downgrade base` removes it, and `upgrade head`
twice in a row is a safe no-op.

## Testing

Everything *except* `test_migrations.py` bypasses Alembic entirely:
`backend/tests/conftest.py`'s `make_test_client()`/`db_session` fixtures
create an isolated in-memory SQLite database per test via
`Base.metadata.create_all()` (fast, no subprocess, no file I/O) and — for
API-level tests — override FastAPI's `get_db` dependency so no test can
ever read or write the developer's real `backend/data/chintu.db`. Every
test that constructs its own `TestClient(create_app())` (e.g. after
monkeypatching env vars) must go through `make_test_client()`, never a bare
`TestClient(create_app())`, for this isolation to hold — enforced by
convention today (see the comment on `make_test_client`), not tooling.

## Not implemented yet

- No per-user rows or any notion of "user" — see
  [docs/features/008_Settings.md](../features/008_Settings.md)'s
  "Deliberately out of scope".
- No secrets/encrypted columns — see
  [06_SECURITY.md](06_SECURITY.md) and [BACKLOG.md](../../BACKLOG.md)'s
  Phase 5 secrets-management item.
- No composite indexes or foreign keys yet — nothing to relate the
  `settings` table to until a second real table exists (Phase 4's
  Reminders/Alarms).
