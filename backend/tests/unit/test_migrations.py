"""Exercises the actual Alembic migration files via the `alembic` CLI
against a throwaway database — everything else in this suite creates
tables via Base.metadata.create_all() for speed, which never touches
alembic/versions/ at all, so this is the only place that would catch a
broken migration."""

import os
import subprocess
import sys
from pathlib import Path

from sqlalchemy import create_engine, inspect

BACKEND_DIR = Path(__file__).resolve().parents[2]


def _run_alembic(args: list[str], database_url: str) -> None:
    env = {**os.environ, "DATABASE_URL": database_url}
    result = subprocess.run(
        [sys.executable, "-m", "alembic", *args],
        cwd=BACKEND_DIR,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_alembic_upgrade_creates_the_settings_table(tmp_path: Path) -> None:
    database_url = f"sqlite:///{(tmp_path / 'test.db').as_posix()}"

    _run_alembic(["upgrade", "head"], database_url)

    engine = create_engine(database_url)
    inspector = inspect(engine)
    assert "settings" in inspector.get_table_names()
    columns = {col["name"] for col in inspector.get_columns("settings")}
    assert columns == {"key", "value", "updated_at"}
    engine.dispose()


def test_alembic_downgrade_removes_the_settings_table(tmp_path: Path) -> None:
    database_url = f"sqlite:///{(tmp_path / 'test.db').as_posix()}"

    _run_alembic(["upgrade", "head"], database_url)
    _run_alembic(["downgrade", "base"], database_url)

    engine = create_engine(database_url)
    inspector = inspect(engine)
    assert "settings" not in inspector.get_table_names()
    engine.dispose()


def test_alembic_upgrade_is_idempotent(tmp_path: Path) -> None:
    database_url = f"sqlite:///{(tmp_path / 'test.db').as_posix()}"

    _run_alembic(["upgrade", "head"], database_url)
    _run_alembic(["upgrade", "head"], database_url)  # already at head — must be a safe no-op

    engine = create_engine(database_url)
    inspector = inspect(engine)
    assert "settings" in inspector.get_table_names()
    engine.dispose()
