from app.core.scheduler import scheduler
from app.main import create_app
from tests.conftest import make_test_client


def test_scheduler_starts_and_stops_with_the_app_lifespan() -> None:
    with make_test_client(create_app()):
        assert scheduler.running

    assert not scheduler.running
