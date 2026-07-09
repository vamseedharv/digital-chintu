"""Application configuration, loaded from environment variables / .env file."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration. All values can be overridden via environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Chintu"
    app_env: str = "development"
    # Defaults to False so an accidental deployment without an explicit .env
    # doesn't leak verbose tracebacks. Local dev enables it via .env.example.
    debug: bool = False

    api_v1_prefix: str = "/api/v1"

    log_level: str = "INFO"
    log_dir: str = "logs"

    # Comma-separated list of allowed CORS origins, e.g. "http://localhost:5173,http://localhost:3000"
    cors_origins: str = "http://localhost:5173"

    database_url: str = "sqlite:///./data/chintu.db"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
