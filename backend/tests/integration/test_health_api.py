import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import create_app
from tests.conftest import make_test_client


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app_name"]
    assert body["environment"]


def test_health_reflects_the_configured_app_name(monkeypatch: pytest.MonkeyPatch) -> None:
    # The whole point of app_name being configurable is that this response
    # changes with it — assert against a locally-built client so the env var
    # is set before create_app() (and its cached Settings) run.
    monkeypatch.setenv("APP_NAME", "Jarvis")
    get_settings.cache_clear()

    client = make_test_client(create_app())
    response = client.get("/api/v1/health")

    assert response.json()["app_name"] == "Jarvis"


def test_unknown_route_returns_404(client: TestClient) -> None:
    response = client.get("/api/v1/does-not-exist")

    assert response.status_code == 404


def test_cors_allows_a_configured_origin(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CORS_ORIGINS", "http://allowed.test")
    get_settings.cache_clear()
    client = make_test_client(create_app())

    response = client.get("/api/v1/health", headers={"Origin": "http://allowed.test"})

    assert response.headers["access-control-allow-origin"] == "http://allowed.test"


def test_cors_rejects_an_unconfigured_origin(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CORS_ORIGINS", "http://allowed.test")
    get_settings.cache_clear()
    client = make_test_client(create_app())

    response = client.get("/api/v1/health", headers={"Origin": "http://not-allowed.test"})

    # Starlette's CORS middleware still serves the request (CORS is enforced
    # by the browser, not the server) but omits the allow-origin header for
    # an origin that isn't on the allow-list.
    assert "access-control-allow-origin" not in response.headers


def test_openapi_schema_documents_the_health_endpoint(client: TestClient) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/api/v1/health" in response.json()["paths"]
