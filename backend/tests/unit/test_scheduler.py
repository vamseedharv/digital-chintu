from fastapi.testclient import TestClient

from app.core.scheduler import scheduler
from app.main import create_app


def test_scheduler_starts_and_stops_with_the_app_lifespan() -> None:
    with TestClient(create_app()):
        assert scheduler.running

    assert not scheduler.running
