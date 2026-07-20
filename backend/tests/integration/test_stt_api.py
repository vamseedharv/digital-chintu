"""Integration tests for the STT status endpoint. The `voice` extras are
never installed in this venv (see backend/pyproject.toml) — that's the
real, exercised CI condition, not a simulated one. No dedicated trigger
endpoint exists — POST /api/v1/wake-word/trigger is what drives STT (see
docs/features/012_Speech_To_Text.md), verified here via the OpenAPI schema
and the fact it still returns 200 with SttRuntime wired into the app."""

from fastapi.testclient import TestClient

from app.main import create_app
from tests.conftest import make_test_client


def test_status_reports_the_pre_start_default_without_the_app_lifespan_having_run(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/stt/status")

    assert response.status_code == 200
    assert response.json() == {
        "enabled": False,
        "available": False,
        "model": None,
        "reason": "STT runtime has not started yet",
        "last_transcription": None,
        "last_transcribed_at": None,
    }


def test_status_reflects_the_real_fail_soft_path_through_the_full_app_lifespan() -> None:
    # A real end-to-end check that create_app() -> lifespan() -> SettingsService
    # -> SttRuntime.start() are wired together correctly — not just that
    # SttRuntime itself degrades gracefully in isolation (see
    # tests/unit/test_stt_runtime.py). stt_enabled defaults to True (fresh,
    # empty settings DB), and pywhispercpp genuinely isn't installed, so
    # this exercises the real "not installed" path.
    with make_test_client(create_app()) as client:
        response = client.get("/api/v1/stt/status")

    assert response.status_code == 200
    body = response.json()
    assert body["enabled"] is True
    assert body["available"] is False
    assert body["model"] is None
    assert body["reason"] is not None
    assert body["reason"] != "STT runtime has not started yet"


def test_wake_word_trigger_still_works_with_stt_wired_into_the_app(client: TestClient) -> None:
    # SttRuntime being unavailable (no `voice` extras) must not break the
    # wake-word endpoint it subscribes to.
    response = client.post("/api/v1/wake-word/trigger")

    assert response.status_code == 200


def test_openapi_schema_documents_the_stt_endpoint(client: TestClient) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/api/v1/stt/status" in paths
    assert "get" in paths["/api/v1/stt/status"]
