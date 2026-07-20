"""Read/write runtime settings — a DB-backed override layer on top of the
env-driven defaults in app.core.config.Settings. `app_name`, `default_theme`,
`onboarding_complete`, `wake_word_enabled`, and `stt_enabled` are managed
here today (`wake_word` itself is read-only/derived, not independently
overridable — see docs/features/011_Wake_Word.md); see
docs/features/008_Settings.md for what's deliberately out of scope."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, field_validator

from app.api.v1.deps import get_settings_service
from app.core.config import Theme
from app.core.validation import validate_short_text
from app.domain.settings import EffectiveSettings
from app.services.settings_service import SettingsService

router = APIRouter()


class SettingsResponse(BaseModel):
    app_name: str
    default_theme: Theme
    onboarding_complete: bool
    # Read-only — derived from app_name, not independently settable. See
    # docs/features/011_Wake_Word.md.
    wake_word: str
    wake_word_enabled: bool
    stt_enabled: bool


class SettingsUpdate(BaseModel):
    """Partial update — omitted fields are left unchanged. `None` means
    "don't change this field", not "clear it"; there's no concept of an
    unset assistant name or theme to clear it to."""

    app_name: str | None = None
    default_theme: Theme | None = None
    onboarding_complete: bool | None = None
    wake_word_enabled: bool | None = None
    stt_enabled: bool | None = None

    @field_validator("app_name")
    @classmethod
    def _valid_app_name(cls, value: str | None) -> str | None:
        return validate_short_text(value, "app_name") if value is not None else None


def _to_response(effective: EffectiveSettings) -> SettingsResponse:
    return SettingsResponse(
        app_name=effective.app_name,
        default_theme=effective.default_theme,
        onboarding_complete=effective.onboarding_complete,
        wake_word=effective.wake_word,
        wake_word_enabled=effective.wake_word_enabled,
        stt_enabled=effective.stt_enabled,
    )


@router.get("/settings", response_model=SettingsResponse)
def get_settings_endpoint(
    service: SettingsService = Depends(get_settings_service),
) -> SettingsResponse:
    return _to_response(service.get_effective_settings())


@router.patch("/settings", response_model=SettingsResponse)
def update_settings_endpoint(
    update: SettingsUpdate,
    service: SettingsService = Depends(get_settings_service),
) -> SettingsResponse:
    if update.app_name is not None:
        service.update_app_name(update.app_name)
    if update.default_theme is not None:
        service.update_default_theme(update.default_theme)
    if update.onboarding_complete is not None:
        service.update_onboarding_complete(update.onboarding_complete)
    if update.wake_word_enabled is not None:
        service.update_wake_word_enabled(update.wake_word_enabled)
    if update.stt_enabled is not None:
        service.update_stt_enabled(update.stt_enabled)

    return _to_response(service.get_effective_settings())
