"""Read-only runtime configuration — the non-secret subset of `Settings`
that a client needs to bootstrap against (assistant identity, defaults),
the same role `/health` already plays for `app_name`."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import get_settings

router = APIRouter()


class RuntimeConfigResponse(BaseModel):
    app_name: str
    wake_word: str
    default_theme: str
    default_language: str
    environment: str


@router.get("/config", response_model=RuntimeConfigResponse)
def get_runtime_config() -> RuntimeConfigResponse:
    settings = get_settings()
    return RuntimeConfigResponse(
        app_name=settings.app_name,
        wake_word=settings.wake_word,
        default_theme=settings.default_theme.value,
        default_language=settings.default_language,
        environment=settings.app_env.value,
    )
