import pytest

from app.core.config import Settings, get_settings


def test_defaults_are_safe_for_an_unconfigured_deployment() -> None:
    settings = Settings(_env_file=None)  # type: ignore[call-arg]

    assert settings.app_name == "Chintu"
    assert settings.app_env == "development"
    # Must default to False: an accidental deployment with no .env shouldn't
    # leak verbose tracebacks (see backend/app/core/config.py).
    assert settings.debug is False
    assert settings.api_v1_prefix == "/api/v1"
    assert settings.database_url == "sqlite:///./data/chintu.db"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("http://localhost:5173", ["http://localhost:5173"]),
        (
            "http://localhost:5173,http://localhost:3000",
            ["http://localhost:5173", "http://localhost:3000"],
        ),
        (" http://a.test , http://b.test ", ["http://a.test", "http://b.test"]),
        ("", []),
        (",,", []),
    ],
)
def test_cors_origins_list_parses_comma_separated_env_value(raw: str, expected: list[str]) -> None:
    settings = Settings(_env_file=None, cors_origins=raw)  # type: ignore[call-arg]

    assert settings.cors_origins_list == expected


def test_settings_are_overridable_via_environment_variables(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_NAME", "Jarvis")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    settings = Settings(_env_file=None)  # type: ignore[call-arg]

    assert settings.app_name == "Jarvis"
    assert settings.debug is True
    assert settings.log_level == "DEBUG"


def test_get_settings_is_cached_until_explicitly_cleared() -> None:
    first = get_settings()
    second = get_settings()

    assert first is second

    get_settings.cache_clear()
    third = get_settings()

    assert third is not first
