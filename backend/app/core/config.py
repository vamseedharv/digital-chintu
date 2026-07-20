"""Application configuration, loaded from environment variables / .env file."""

import re
from enum import StrEnum
from functools import lru_cache

from pydantic import Field, ValidationInfo, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.validation import validate_short_text

_LANGUAGE_TAG_RE = re.compile(r"[a-z]{2,3}(-[A-Z]{2})?")


class Environment(StrEnum):
    """Deployment profile — drives which config-validation rules apply."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class Theme(StrEnum):
    """Default theme preference, before any per-user override."""

    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


class Settings(BaseSettings):
    """Runtime configuration. All values can be overridden via environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Chintu"
    app_env: Environment = Environment.DEVELOPMENT
    # Defaults to False so an accidental deployment without an explicit .env
    # doesn't leak verbose tracebacks. Local dev enables it via .env.example.
    debug: bool = False

    api_v1_prefix: str = "/api/v1"

    log_level: str = "INFO"
    log_dir: str = "logs"

    # Comma-separated list of allowed CORS origins, e.g. "http://localhost:5173,http://localhost:3000"
    cors_origins: str = "http://localhost:5173"

    database_url: str = "sqlite:///./data/chintu.db"

    # Assistant identity/behavior defaults. `app_name` is the assistant's
    # display/spoken name (CLAUDE.md: "never hardcoded"); the rest are
    # env-driven defaults a future onboarding/settings feature can read —
    # this layer doesn't persist per-user overrides, see docs/features/008_Settings.md.
    #
    # `wake_word` is `None` unless an operator pins an exact phrase via
    # WAKE_WORD — the *effective* phrase (what /api/v1/config and
    # /api/v1/settings actually report) defaults to "Hey {app_name}" instead,
    # computed in app/services/settings_service.py so it tracks a DB-overridden
    # app_name too. See docs/features/011_Wake_Word.md for why the phrase text
    # is decoupled from which acoustic model is listening.
    wake_word: str | None = None
    default_theme: Theme = Theme.SYSTEM
    default_language: str = "en-US"

    # Wake-word detection (docs/features/011_Wake_Word.md). All env-only,
    # deployment-level knobs — not managed by 008_Settings, same tier as
    # plugins_dir. Detection itself is an opt-in extra (`pip install
    # '.[voice]'`); these fields are harmless to set even when that extra
    # isn't installed.
    wake_word_model: str = "hey_jarvis"
    wake_word_sensitivity: float = Field(default=0.5, ge=0.0, le=1.0)
    wake_word_preroll_seconds: float = Field(default=1.0, ge=0.0, le=10.0)
    # Empty string means "use the system's default audio input device."
    voice_audio_device: str = ""

    # Plugin extension point (docs/architecture/05_PLUGIN_SDK.md). Relative
    # paths resolve against the process's working directory, same as log_dir
    # — the default matches running `uvicorn` from `backend/` (native dev),
    # landing on the repo-root `plugins/`. Docker overrides both to absolute
    # container paths, same pattern as DATABASE_URL.
    plugins_dir: str = "../plugins"
    # Comma-separated allow-list of plugin slugs. Empty/unset means "every
    # discovered plugin is enabled" — deliberately not deny-by-default like
    # CORS_ORIGINS, since reaching PLUGINS_DIR already requires deployment
    # access. See 05_PLUGIN_SDK.md's "Enabling / disabling".
    enabled_plugins: str = ""

    @field_validator("app_name", "wake_word_model")
    @classmethod
    def _not_blank(cls, value: str, info: ValidationInfo) -> str:
        return validate_short_text(value, info.field_name or "value")

    @field_validator("wake_word")
    @classmethod
    def _wake_word_not_blank_when_set(cls, value: str | None) -> str | None:
        return validate_short_text(value, "wake_word") if value is not None else None

    @field_validator("default_language")
    @classmethod
    def _valid_language_tag(cls, value: str) -> str:
        if not _LANGUAGE_TAG_RE.fullmatch(value):
            raise ValueError("default_language must be a BCP-47-style tag, e.g. 'en' or 'en-US'")
        return value

    @model_validator(mode="after")
    def _production_must_not_run_with_debug(self) -> "Settings":
        if self.app_env is Environment.PRODUCTION and self.debug:
            raise ValueError(
                "debug must be false when app_env is 'production' "
                "(see docs/architecture/06_SECURITY.md)"
            )
        return self

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def enabled_plugins_set(self) -> set[str] | None:
        """`None` means "all discovered plugins enabled" (the default) —
        see docs/architecture/05_PLUGIN_SDK.md's "Enabling / disabling"."""
        if not self.enabled_plugins.strip():
            return None
        return {slug.strip() for slug in self.enabled_plugins.split(",") if slug.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
