"""Application configuration, loaded from environment variables / .env file."""

import re
from enum import StrEnum
from functools import lru_cache

from pydantic import ValidationInfo, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

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
    wake_word: str = "Hey Chintu"
    default_theme: Theme = Theme.SYSTEM
    default_language: str = "en-US"

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

    @field_validator("app_name", "wake_word")
    @classmethod
    def _not_blank(cls, value: str, info: ValidationInfo) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError(f"{info.field_name} must not be blank")
        if len(stripped) > 64:
            raise ValueError(f"{info.field_name} must be 64 characters or fewer")
        return stripped

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
