import logging
from collections.abc import Iterator
from pathlib import Path

import pytest

from app.core.config import get_settings
from app.core.logging import configure_logging


@pytest.fixture()
def _reset_root_logger() -> Iterator[None]:
    """configure_logging() mutates the process-wide root logger. Restore it
    afterward so this test can't affect logging in any other test, and close
    file handlers so Windows doesn't lock the tmp_path directory on cleanup."""
    original_handlers = logging.getLogger().handlers[:]
    original_level = logging.getLogger().level
    yield
    root = logging.getLogger()
    for handler in root.handlers:
        handler.close()
    root.handlers = original_handlers
    root.setLevel(original_level)


def test_configure_logging_creates_the_log_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, _reset_root_logger: None
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("LOG_DIR", "test_logs")
    get_settings.cache_clear()

    configure_logging()

    assert (tmp_path / "test_logs").is_dir()


def test_configure_logging_sets_level_from_settings(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, _reset_root_logger: None
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    get_settings.cache_clear()

    configure_logging()

    assert logging.getLogger().level == logging.WARNING


def test_configure_logging_is_idempotent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, _reset_root_logger: None
) -> None:
    monkeypatch.chdir(tmp_path)
    get_settings.cache_clear()

    configure_logging()
    configure_logging()

    # Calling it twice must not accumulate duplicate handlers (each call would
    # otherwise double-log every message).
    assert len(logging.getLogger().handlers) == 2
