"""Read-only runtime configuration — the non-secret subset of `Settings`
that a client needs to bootstrap against (assistant identity, defaults),
the same role `/health` already plays for `app_name`. `app_name`,
`default_theme`, and `wake_word` reflect any DB-backed override from
`GET /api/v1/settings` (see app/services/settings_service.py) —
`default_language` doesn't have an override yet and always reports the
env-driven default."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.v1.deps import get_settings_service
from app.core.config import get_settings
from app.services.settings_service import SettingsService

router = APIRouter()


class RuntimeConfigResponse(BaseModel):
    app_name: str
    wake_word: str
    default_theme: str
    default_language: str
    environment: str


@router.get("/config", response_model=RuntimeConfigResponse)
def get_runtime_config(
    service: SettingsService = Depends(get_settings_service),
) -> RuntimeConfigResponse:
    settings = get_settings()
    effective = service.get_effective_settings()
    return RuntimeConfigResponse(
        app_name=effective.app_name,
        wake_word=effective.wake_word,
        default_theme=effective.default_theme.value,
        default_language=settings.default_language,
        environment=settings.app_env.value,
    )
