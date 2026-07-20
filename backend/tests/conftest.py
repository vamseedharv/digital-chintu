from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_db
from app.main import create_app


@pytest.fixture(autouse=True)
def _clear_settings_cache() -> Iterator[None]:
    """Settings are cached process-wide via @lru_cache; without this, an env
    var set by one test can leak into the next test's Settings() instance."""
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def make_test_client(app: FastAPI) -> TestClient:
    """Build a TestClient backed by an isolated, in-memory settings
    database, instead of the real DATABASE_URL file. Use this — never a
    bare TestClient(create_app()) — anywhere a test needs to construct its
    own app (e.g. after monkeypatching env vars), so tests can never read or
    write the developer's real backend/data/chintu.db.

    StaticPool keeps a single in-memory connection alive for the engine's
    lifetime — the default pool would hand out a fresh (and separately
    empty) in-memory database per checkout.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db() -> Iterator[Session]:
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


@pytest.fixture()
def client() -> TestClient:
    return make_test_client(create_app())


@pytest.fixture()
def db_session() -> Iterator[Session]:
    """A plain, isolated in-memory Session for tests that exercise a
    repository or service directly, without going through FastAPI at all."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()
