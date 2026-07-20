from fastapi.testclient import TestClient


def test_get_settings_returns_env_defaults_when_nothing_is_overridden(client: TestClient) -> None:
    response = client.get("/api/v1/settings")

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "app_name": "Chintu",
        "default_theme": "system",
        "onboarding_complete": False,
        "wake_word": "Hey Chintu",
        "wake_word_enabled": True,
        "stt_enabled": True,
    }


def test_patch_updates_app_name_and_returns_the_new_value(client: TestClient) -> None:
    response = client.patch("/api/v1/settings", json={"app_name": "Jarvis"})

    assert response.status_code == 200
    assert response.json() == {
        "app_name": "Jarvis",
        "default_theme": "system",
        "onboarding_complete": False,
        # Derived from app_name — see test_wake_word_tracks_app_name_renames.
        "wake_word": "Hey Jarvis",
        "wake_word_enabled": True,
        "stt_enabled": True,
    }


def test_patch_updates_default_theme_and_returns_the_new_value(client: TestClient) -> None:
    response = client.patch("/api/v1/settings", json={"default_theme": "dark"})

    assert response.status_code == 200
    assert response.json() == {
        "app_name": "Chintu",
        "default_theme": "dark",
        "onboarding_complete": False,
        "wake_word": "Hey Chintu",
        "wake_word_enabled": True,
        "stt_enabled": True,
    }


def test_a_persisted_update_is_reflected_on_a_later_get(client: TestClient) -> None:
    client.patch("/api/v1/settings", json={"app_name": "Jarvis"})

    response = client.get("/api/v1/settings")

    assert response.json()["app_name"] == "Jarvis"


def test_a_partial_update_leaves_the_other_field_unchanged(client: TestClient) -> None:
    client.patch("/api/v1/settings", json={"app_name": "Jarvis"})

    response = client.patch("/api/v1/settings", json={"default_theme": "dark"})

    assert response.json() == {
        "app_name": "Jarvis",
        "default_theme": "dark",
        "onboarding_complete": False,
        "wake_word": "Hey Jarvis",
        "wake_word_enabled": True,
        "stt_enabled": True,
    }


def test_an_empty_update_is_a_no_op(client: TestClient) -> None:
    response = client.patch("/api/v1/settings", json={})

    assert response.status_code == 200
    assert response.json() == {
        "app_name": "Chintu",
        "default_theme": "system",
        "onboarding_complete": False,
        "wake_word": "Hey Chintu",
        "wake_word_enabled": True,
        "stt_enabled": True,
    }


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


def test_onboarding_complete_defaults_to_false(client: TestClient) -> None:
    response = client.get("/api/v1/settings")

    assert response.json()["onboarding_complete"] is False


def test_patch_can_mark_onboarding_complete(client: TestClient) -> None:
    response = client.patch("/api/v1/settings", json={"onboarding_complete": True})

    assert response.status_code == 200
    assert response.json()["onboarding_complete"] is True


def test_onboarding_complete_persists_across_requests(client: TestClient) -> None:
    client.patch("/api/v1/settings", json={"onboarding_complete": True})

    response = client.get("/api/v1/settings")

    assert response.json()["onboarding_complete"] is True


def test_onboarding_can_be_marked_incomplete_again(client: TestClient) -> None:
    # Not a one-time irreversible gate — re-running onboarding should be
    # able to flip it back, same as any other setting.
    client.patch("/api/v1/settings", json={"onboarding_complete": True})

    response = client.patch("/api/v1/settings", json={"onboarding_complete": False})

    assert response.json()["onboarding_complete"] is False


def test_skipping_onboarding_does_not_touch_app_name_or_theme(client: TestClient) -> None:
    client.patch("/api/v1/settings", json={"app_name": "Jarvis", "default_theme": "dark"})

    response = client.patch("/api/v1/settings", json={"onboarding_complete": True})

    assert response.json() == {
        "app_name": "Jarvis",
        "default_theme": "dark",
        "onboarding_complete": True,
        "wake_word": "Hey Jarvis",
        "wake_word_enabled": True,
        "stt_enabled": True,
    }


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
    # wake_word now tracks a renamed assistant too (011_Wake_Word) — the
    # only setting still purely env-driven is default_language.
    assert body["wake_word"] == "Hey Jarvis"
    assert body["default_language"] == "en-US"


def test_wake_word_tracks_app_name_renames(client: TestClient) -> None:
    client.patch("/api/v1/settings", json={"app_name": "Jarvis"})

    response = client.get("/api/v1/settings")

    assert response.json()["wake_word"] == "Hey Jarvis"


def test_wake_word_enabled_defaults_to_true(client: TestClient) -> None:
    response = client.get("/api/v1/settings")

    assert response.json()["wake_word_enabled"] is True


def test_patch_can_disable_wake_word(client: TestClient) -> None:
    response = client.patch("/api/v1/settings", json={"wake_word_enabled": False})

    assert response.status_code == 200
    assert response.json()["wake_word_enabled"] is False


def test_wake_word_enabled_persists_across_requests(client: TestClient) -> None:
    client.patch("/api/v1/settings", json={"wake_word_enabled": False})

    response = client.get("/api/v1/settings")

    assert response.json()["wake_word_enabled"] is False


def test_stt_enabled_defaults_to_true(client: TestClient) -> None:
    response = client.get("/api/v1/settings")

    assert response.json()["stt_enabled"] is True


def test_patch_can_disable_stt(client: TestClient) -> None:
    response = client.patch("/api/v1/settings", json={"stt_enabled": False})

    assert response.status_code == 200
    assert response.json()["stt_enabled"] is False


def test_stt_enabled_persists_across_requests(client: TestClient) -> None:
    client.patch("/api/v1/settings", json={"stt_enabled": False})

    response = client.get("/api/v1/settings")

    assert response.json()["stt_enabled"] is False


def test_stt_enabled_and_wake_word_enabled_are_independent(client: TestClient) -> None:
    client.patch("/api/v1/settings", json={"stt_enabled": False})

    response = client.get("/api/v1/settings")

    assert response.json()["stt_enabled"] is False
    assert response.json()["wake_word_enabled"] is True


def test_openapi_schema_documents_the_settings_endpoint(client: TestClient) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/api/v1/settings" in paths
    assert "get" in paths["/api/v1/settings"]
    assert "patch" in paths["/api/v1/settings"]
