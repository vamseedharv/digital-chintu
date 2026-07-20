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
        onboarding_override = overrides.get(SettingKey.ONBOARDING_COMPLETE)
        onboarding_complete = onboarding_override == "true"

        # No DB override of its own: an operator-pinned WAKE_WORD env var
        # wins if set, otherwise it's derived from the (possibly
        # DB-overridden) app_name — see docs/features/011_Wake_Word.md.
        wake_word = defaults.wake_word or f"Hey {app_name}"
        wake_word_enabled = self._bool_override(
            overrides, SettingKey.WAKE_WORD_ENABLED, default=True
        )
        stt_enabled = self._bool_override(overrides, SettingKey.STT_ENABLED, default=True)

        return EffectiveSettings(
            app_name=app_name,
            default_theme=default_theme,
            onboarding_complete=onboarding_complete,
            wake_word=wake_word,
            wake_word_enabled=wake_word_enabled,
            stt_enabled=stt_enabled,
        )

    @staticmethod
    def _bool_override(overrides: dict[str, str], key: SettingKey, *, default: bool) -> bool:
        override = overrides.get(key)
        return override == "true" if override is not None else default

    def update_app_name(self, value: str) -> None:
        validated = validate_short_text(value, "app_name")
        self._repository.set(SettingKey.APP_NAME, validated)

    def update_default_theme(self, value: Theme) -> None:
        self._repository.set(SettingKey.DEFAULT_THEME, value.value)

    def update_onboarding_complete(self, value: bool) -> None:
        self._repository.set(SettingKey.ONBOARDING_COMPLETE, "true" if value else "false")

    def update_wake_word_enabled(self, value: bool) -> None:
        self._repository.set(SettingKey.WAKE_WORD_ENABLED, "true" if value else "false")

    def update_stt_enabled(self, value: bool) -> None:
        self._repository.set(SettingKey.STT_ENABLED, "true" if value else "false")
