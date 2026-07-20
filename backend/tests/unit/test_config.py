import pytest
from pydantic import ValidationError

from app.core.config import Environment, Settings, Theme, get_settings


def test_defaults_are_safe_for_an_unconfigured_deployment() -> None:
    settings = Settings(_env_file=None)  # type: ignore[call-arg]

    assert settings.app_name == "Chintu"
    assert settings.app_env == "development"
    # Must default to False: an accidental deployment with no .env shouldn't
    # leak verbose tracebacks (see backend/app/core/config.py).
    assert settings.debug is False
    assert settings.api_v1_prefix == "/api/v1"
    assert settings.database_url == "sqlite:///./data/chintu.db"
    # None means "not pinned" — the effective phrase is derived from
    # app_name by app/services/settings_service.py instead.
    assert settings.wake_word is None
    assert settings.default_theme == "system"
    assert settings.default_language == "en-US"
    assert settings.wake_word_model == "hey_jarvis"
    assert settings.wake_word_sensitivity == 0.5
    assert settings.wake_word_preroll_seconds == 1.0
    assert settings.voice_audio_device == ""


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


def test_assistant_settings_are_overridable_via_environment_variables(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("WAKE_WORD", "Hey Jarvis")
    monkeypatch.setenv("DEFAULT_THEME", "dark")
    monkeypatch.setenv("DEFAULT_LANGUAGE", "hi-IN")
    monkeypatch.setenv("APP_ENV", "testing")

    settings = Settings(_env_file=None)  # type: ignore[call-arg]

    assert settings.wake_word == "Hey Jarvis"
    assert settings.default_theme is Theme.DARK
    assert settings.default_language == "hi-IN"
    assert settings.app_env is Environment.TESTING


def test_app_name_and_wake_word_are_trimmed_of_surrounding_whitespace() -> None:
    settings = Settings(_env_file=None, app_name="  Chintu  ", wake_word="  Hey Chintu  ")  # type: ignore[call-arg]

    assert settings.app_name == "Chintu"
    assert settings.wake_word == "Hey Chintu"


@pytest.mark.parametrize("field", ["app_name", "wake_word"])
def test_blank_assistant_identity_fields_are_rejected(field: str) -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, **{field: "   "})  # type: ignore[call-arg, arg-type]


def test_overly_long_wake_word_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, wake_word="x" * 65)  # type: ignore[call-arg]


def test_wake_word_settings_are_overridable_via_environment_variables(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("WAKE_WORD_MODEL", "alexa")
    monkeypatch.setenv("WAKE_WORD_SENSITIVITY", "0.8")
    monkeypatch.setenv("WAKE_WORD_PREROLL_SECONDS", "2.5")
    monkeypatch.setenv("VOICE_AUDIO_DEVICE", "USB Microphone")

    settings = Settings(_env_file=None)  # type: ignore[call-arg]

    assert settings.wake_word_model == "alexa"
    assert settings.wake_word_sensitivity == 0.8
    assert settings.wake_word_preroll_seconds == 2.5
    assert settings.voice_audio_device == "USB Microphone"


@pytest.mark.parametrize("sensitivity", [-0.1, 1.1])
def test_wake_word_sensitivity_out_of_range_is_rejected(sensitivity: float) -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, wake_word_sensitivity=sensitivity)  # type: ignore[call-arg]


def test_blank_wake_word_model_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, wake_word_model="   ")  # type: ignore[call-arg]


@pytest.mark.parametrize("invalid_tag", ["english", "EN", "en_US", "en-us", ""])
def test_malformed_language_tags_are_rejected(invalid_tag: str) -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, default_language=invalid_tag)  # type: ignore[call-arg]


@pytest.mark.parametrize("valid_tag", ["en", "en-US", "hi-IN", "fra"])
def test_well_formed_language_tags_are_accepted(valid_tag: str) -> None:
    settings = Settings(_env_file=None, default_language=valid_tag)  # type: ignore[call-arg]

    assert settings.default_language == valid_tag


def test_unknown_environment_profile_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, app_env="staging")  # type: ignore[call-arg, arg-type]


def test_unknown_theme_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, default_theme="blue")  # type: ignore[call-arg, arg-type]


def test_production_profile_forbids_debug_mode() -> None:
    with pytest.raises(ValidationError, match="debug must be false"):
        Settings(_env_file=None, app_env="production", debug=True)  # type: ignore[call-arg, arg-type]


def test_production_profile_allows_debug_disabled() -> None:
    settings = Settings(_env_file=None, app_env="production", debug=False)  # type: ignore[call-arg, arg-type]

    assert settings.app_env is Environment.PRODUCTION
    assert settings.debug is False


def test_development_profile_still_allows_debug_mode() -> None:
    settings = Settings(_env_file=None, app_env="development", debug=True)  # type: ignore[call-arg, arg-type]

    assert settings.debug is True
