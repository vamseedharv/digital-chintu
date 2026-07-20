import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import create_app


def test_config_returns_the_runtime_settings(client: TestClient) -> None:
    response = client.get("/api/v1/config")

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "app_name": "Chintu",
        "wake_word": "Hey Chintu",
        "default_theme": "system",
        "default_language": "en-US",
        "environment": "development",
    }


def test_config_reflects_environment_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    # Same pattern as test_health_reflects_the_configured_app_name: build a
    # local client so the env vars are set before create_app()'s cached
    # Settings are constructed.
    monkeypatch.setenv("WAKE_WORD", "Hey Jarvis")
    monkeypatch.setenv("DEFAULT_THEME", "dark")
    monkeypatch.setenv("DEFAULT_LANGUAGE", "hi-IN")
    get_settings.cache_clear()

    client = TestClient(create_app())
    response = client.get("/api/v1/config")

    body = response.json()
    assert body["wake_word"] == "Hey Jarvis"
    assert body["default_theme"] == "dark"
    assert body["default_language"] == "hi-IN"


def test_openapi_schema_documents_the_config_endpoint(client: TestClient) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()
    assert "/api/v1/config" in schema["paths"]
    # Unlike /health's bare dict[str, str], this endpoint has a real
    # response_model — confirm the schema actually documents its shape.
    response_schema = schema["paths"]["/api/v1/config"]["get"]["responses"]["200"]["content"][
        "application/json"
    ]["schema"]
    assert "$ref" in response_schema
