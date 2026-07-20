"""Business logic for the settings subsystem: resolves the effective value
of each managed setting (a DB override if one exists, otherwise the
env-driven default) and validates new values before they're persisted.
"""

from app.core.config import Theme, get_settings
from app.core.validation import validate_short_text
from app.domain.settings import EffectiveSettings, SettingKey
from app.repositories.settings_repository import SettingsRepository


class SettingsService:
    def __init__(self, repository: SettingsRepository) -> None:
        self._repository = repository

    def get_effective_settings(self) -> EffectiveSettings:
        defaults = get_settings()
        overrides = self._repository.get_all()

        app_name = overrides.get(SettingKey.APP_NAME, defaults.app_name)
        theme_override = overrides.get(SettingKey.DEFAULT_THEME)
        default_theme = (
            Theme(theme_override) if theme_override is not None else defaults.default_theme
        )

        return EffectiveSettings(app_name=app_name, default_theme=default_theme)

    def update_app_name(self, value: str) -> None:
        validated = validate_short_text(value, "app_name")
        self._repository.set(SettingKey.APP_NAME, validated)

    def update_default_theme(self, value: Theme) -> None:
        self._repository.set(SettingKey.DEFAULT_THEME, value.value)
