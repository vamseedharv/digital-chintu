"""SQLAlchemy engine/session setup, shared by all future repositories."""

from collections.abc import Generator
from pathlib import Path
from urllib.parse import urlsplit

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

_is_sqlite = settings.database_url.startswith("sqlite")
_connect_args = {"check_same_thread": False} if _is_sqlite else {}

if _is_sqlite:
    # SQLite won't create missing parent directories itself — without this,
    # the first query against a fresh checkout fails with
    # "unable to open database file" (only masked under Docker, where the
    # Dockerfile pre-creates /app/data).
    _url_path = urlsplit(settings.database_url).path
    # urlsplit always keeps one leading "/" as the path separator after the
    # (empty) netloc; strip exactly that one to recover the real filesystem
    # path, whether it's relative ("./data/db.sqlite") or absolute
    # ("/app/data/db.sqlite" from a 4-slash sqlite://// URL). A blanket
    # lstrip("/") would wrongly turn an absolute path into a relative one.
    _db_path = _url_path[1:] if _url_path.startswith("/") else _url_path
    if _db_path:
        Path(_db_path).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(settings.database_url, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a request-scoped database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
