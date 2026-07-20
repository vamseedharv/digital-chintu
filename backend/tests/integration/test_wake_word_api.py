"""Integration tests for the wake-word status/trigger endpoints. The
`voice` extras are never installed in this venv (see backend/pyproject.toml)
— that's the real, exercised CI condition, not a simulated one."""

import pytest
from fastapi.testclient import TestClient

from app.core.voice.events import WakeWordEvent, wake_word_events
from app.main import create_app
from tests.conftest import make_test_client


def test_trigger_works_without_the_app_lifespan_having_run(client: TestClient) -> None:
    # The `client` fixture never enters `with ...:` (see tests/conftest.py),
    # so lifespan hasn't run and app.state.wake_word_runtime was never
    # start()-ed — trigger_manual() must still work regardless (the
    # documented push-to-talk fallback).
    response = client.post("/api/v1/wake-word/trigger")

    assert response.status_code == 200
    body = response.json()
    assert body["trigger"] == "manual"
    assert body["model"] is None
    assert body["confidence"] == 1.0
    assert "detected_at" in body


def test_status_reports_the_pre_start_default_without_the_app_lifespan_having_run(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/wake-word/status")

    assert response.status_code == 200
    assert response.json() == {
        "enabled": False,
        "listening": False,
        "model": None,
        "reason": "wake-word runtime has not started yet",
    }


def test_status_reflects_the_real_fail_soft_path_through_the_full_app_lifespan() -> None:
    # A real end-to-end check that create_app() -> lifespan() -> SettingsService
    # -> WakeWordRuntime.start() are wired together correctly — not just that
    # WakeWordRuntime itself degrades gracefully in isolation (see
    # tests/unit/test_voice_runtime.py). wake_word_enabled defaults to True
    # (fresh, empty settings DB), and openwakeword/sounddevice genuinely
    # aren't installed, so this exercises the real "not installed" path.
    with make_test_client(create_app()) as client:
        response = client.get("/api/v1/wake-word/status")

    assert response.status_code == 200
    body = response.json()
    assert body["enabled"] is True
    assert body["listening"] is False
    assert body["model"] is None
    assert body["reason"] is not None
    assert body["reason"] != "wake-word runtime has not started yet"


@pytest.mark.asyncio
async def test_trigger_publishes_to_the_shared_event_bus_through_the_real_app() -> None:
    received: list[WakeWordEvent] = []

    async def listener(event: WakeWordEvent) -> None:
        received.append(event)

    wake_word_events.subscribe(listener)
    try:
        with make_test_client(create_app()) as client:
            response = client.post("/api/v1/wake-word/trigger")
    finally:
        wake_word_events.unsubscribe(listener)

    assert response.status_code == 200
    assert len(received) == 1
    assert received[0].trigger == "manual"


def test_openapi_schema_documents_the_wake_word_endpoints(client: TestClient) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/api/v1/wake-word/status" in paths
    assert "get" in paths["/api/v1/wake-word/status"]
    assert "/api/v1/wake-word/trigger" in paths
    assert "post" in paths["/api/v1/wake-word/trigger"]
