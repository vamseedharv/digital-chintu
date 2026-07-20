"""Health check endpoint used by clients, Docker healthchecks, and monitoring."""

from fastapi import APIRouter, Depends

from app.api.v1.deps import get_settings_service
from app.core.config import get_settings
from app.services.settings_service import SettingsService

router = APIRouter()


@router.get("/health")
def get_health(service: SettingsService = Depends(get_settings_service)) -> dict[str, str]:
    settings = get_settings()
    effective = service.get_effective_settings()
    return {
        "status": "ok",
        "app_name": effective.app_name,
        "environment": settings.app_env,
    }
