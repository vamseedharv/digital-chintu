from fastapi.testclient import TestClient


def test_get_settings_returns_env_defaults_when_nothing_is_overridden(client: TestClient) -> None:
    response = client.get("/api/v1/settings")

    assert response.status_code == 200
    body = response.json()
    assert body == {"app_name": "Chintu", "default_theme": "system"}


def test_patch_updates_app_name_and_returns_the_new_value(client: TestClient) -> None:
    response = client.patch("/api/v1/settings", json={"app_name": "Jarvis"})

    assert response.status_code == 200
    assert response.json() == {"app_name": "Jarvis", "default_theme": "system"}


def test_patch_updates_default_theme_and_returns_the_new_value(client: TestClient) -> None:
    response = client.patch("/api/v1/settings", json={"default_theme": "dark"})

    assert response.status_code == 200
    assert response.json() == {"app_name": "Chintu", "default_theme": "dark"}


def test_a_persisted_update_is_reflected_on_a_later_get(client: TestClient) -> None:
    client.patch("/api/v1/settings", json={"app_name": "Jarvis"})

    response = client.get("/api/v1/settings")

    assert response.json()["app_name"] == "Jarvis"


def test_a_partial_update_leaves_the_other_field_unchanged(client: TestClient) -> None:
    client.patch("/api/v1/settings", json={"app_name": "Jarvis"})

    response = client.patch("/api/v1/settings", json={"default_theme": "dark"})

    assert response.json() == {"app_name": "Jarvis", "default_theme": "dark"}


def test_an_empty_update_is_a_no_op(client: TestClient) -> None:
    response = client.patch("/api/v1/settings", json={})

    assert response.status_code == 200
    assert response.json() == {"app_name": "Chintu", "default_theme": "system"}


def test_patch_rejects_a_blank_app_name(client: TestClient) -> None:
    response = client.patch("/api/v1/settings", json={"app_name": "   "})

    assert response.status_code == 422


def test_patch_rejects_an_overly_long_app_name(client: TestClient) -> None:
    response = client.patch("/api/v1/settings", json={"app_name": "x" * 65})

    assert response.status_code == 422


def test_patch_rejects_an_unknown_theme(client: TestClient) -> None:
    response = client.patch("/api/v1/settings", json={"default_theme": "purple"})

    assert response.status_code == 422


def test_a_rejected_update_does_not_persist_anything(client: TestClient) -> None:
    client.patch("/api/v1/settings", json={"app_name": "   "})

    response = client.get("/api/v1/settings")

    assert response.json()["app_name"] == "Chintu"


def test_health_reflects_an_overridden_app_name(client: TestClient) -> None:
    client.patch("/api/v1/settings", json={"app_name": "Jarvis"})

    response = client.get("/api/v1/health")

    assert response.json()["app_name"] == "Jarvis"


def test_config_reflects_an_overridden_app_name_and_theme(client: TestClient) -> None:
    client.patch("/api/v1/settings", json={"app_name": "Jarvis", "default_theme": "dark"})

    response = client.get("/api/v1/config")

    body = response.json()
    assert body["app_name"] == "Jarvis"
    assert body["default_theme"] == "dark"
    # Settings not managed by this feature yet still report the env default.
    assert body["wake_word"] == "Hey Chintu"
    assert body["default_language"] == "en-US"


def test_openapi_schema_documents_the_settings_endpoint(client: TestClient) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/api/v1/settings" in paths
    assert "get" in paths["/api/v1/settings"]
    assert "patch" in paths["/api/v1/settings"]
