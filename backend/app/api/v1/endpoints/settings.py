"""Read/write runtime settings — a DB-backed override layer on top of the
env-driven defaults in app.core.config.Settings. Only `app_name` and
`default_theme` are managed here today; see
docs/features/008_Settings.md for what's deliberately out of scope."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, field_validator

from app.api.v1.deps import get_settings_service
from app.core.config import Theme
from app.core.validation import validate_short_text
from app.services.settings_service import SettingsService

router = APIRouter()


class SettingsResponse(BaseModel):
    app_name: str
    default_theme: Theme


class SettingsUpdate(BaseModel):
    """Partial update — omitted fields are left unchanged. `None` means
    "don't change this field", not "clear it"; there's no concept of an
    unset assistant name or theme to clear it to."""

    app_name: str | None = None
    default_theme: Theme | None = None

    @field_validator("app_name")
    @classmethod
    def _valid_app_name(cls, value: str | None) -> str | None:
        return validate_short_text(value, "app_name") if value is not None else None


@router.get("/settings", response_model=SettingsResponse)
def get_settings_endpoint(
    service: SettingsService = Depends(get_settings_service),
) -> SettingsResponse:
    effective = service.get_effective_settings()
    return SettingsResponse(app_name=effective.app_name, default_theme=effective.default_theme)


@router.patch("/settings", response_model=SettingsResponse)
def update_settings_endpoint(
    update: SettingsUpdate,
    service: SettingsService = Depends(get_settings_service),
) -> SettingsResponse:
    if update.app_name is not None:
        service.update_app_name(update.app_name)
    if update.default_theme is not None:
        service.update_default_theme(update.default_theme)

    effective = service.get_effective_settings()
    return SettingsResponse(app_name=effective.app_name, default_theme=effective.default_theme)
