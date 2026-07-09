import importlib
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import ModuleType

import pytest
from sqlalchemy import text

from app.core.config import get_settings
from app.db import session as session_module


@pytest.fixture()
def reloaded_session(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[ModuleType]:
    """app/db/session.py binds settings/engine at import time, so exercising
    a different DATABASE_URL means reloading it under a monkeypatched env.
    Disposes the engine and reloads once more with the real environment
    afterward, so this module's changes can't leak into other tests."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./data/test.db")
    get_settings.cache_clear()

    reloaded = importlib.reload(session_module)
    yield reloaded

    reloaded.engine.dispose()
    get_settings.cache_clear()
    importlib.reload(session_module)


def test_creates_missing_data_directory_for_a_relative_sqlite_path(
    tmp_path: Path, reloaded_session: ModuleType
) -> None:
    # create_engine() is lazy and doesn't open the db file until first use,
    # so the directory (created eagerly at import time) is what's under test
    # here — without it, that first connection fails with
    # "unable to open database file" instead of creating the file on demand.
    assert (tmp_path / "data").is_dir()


def test_get_db_yields_a_working_session_that_closes_after_use(
    reloaded_session: ModuleType,
) -> None:
    generator = reloaded_session.get_db()
    db = next(generator)

    assert db.execute(text("SELECT 1")).scalar() == 1

    # Exhausting the generator runs the `finally: db.close()` block.
    with pytest.raises(StopIteration):
        next(generator)


def test_engine_connection_works_from_a_different_thread(reloaded_session: ModuleType) -> None:
    # FastAPI serves each request on a worker thread that didn't create the
    # engine. Without check_same_thread=False, SQLite raises "objects created
    # in a thread can only be used in that same thread" the moment a
    # connection from a different thread runs a query.
    def query_from_worker_thread() -> int:
        with reloaded_session.engine.connect() as conn:
            return int(conn.execute(text("SELECT 1")).scalar_one())

    with ThreadPoolExecutor(max_workers=1) as executor:
        result = executor.submit(query_from_worker_thread).result(timeout=5)

    assert result == 1
