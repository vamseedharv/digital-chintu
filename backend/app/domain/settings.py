"""Domain-level concepts for the settings subsystem — framework-independent,
no SQLAlchemy or Pydantic-BaseSettings coupling. See
docs/architecture/03_DATABASE_DESIGN.md and docs/features/008_Settings.md.
"""

from dataclasses import dataclass
from enum import StrEnum

from app.core.config import Theme


class SettingKey(StrEnum):
    """Keys of the settings this feature manages today. Adding a new
    setting: a key here, a case in SettingsService, and a field on the
    API's SettingsResponse/SettingsUpdate — no database migration, since
    the settings table is a generic key/value store (see
    app/db/models.py's SettingModel)."""

    APP_NAME = "app_name"
    DEFAULT_THEME = "default_theme"
    ONBOARDING_COMPLETE = "onboarding_complete"
    WAKE_WORD_ENABLED = "wake_word_enabled"


@dataclass(frozen=True)
class EffectiveSettings:
    """The resolved value of every managed setting. `app_name`/`default_theme`
    fall back to the env-driven default from `app.core.config.Settings` when
    no override exists; `onboarding_complete` has no env-driven concept — it
    defaults to `False` (never onboarded) until explicitly set `True`.
    `wake_word` has no override of its own — it's derived from `app_name`
    (or the `WAKE_WORD` env pin, if set) by `SettingsService`, not persisted;
    `wake_word_enabled` defaults to `True` and is the on/off toggle for
    always-on listening (see docs/features/011_Wake_Word.md)."""

    app_name: str
    default_theme: Theme
    onboarding_complete: bool
    wake_word: str
    wake_word_enabled: bool
