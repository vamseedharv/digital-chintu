"""Aggregates all v1 API endpoint routers."""

from fastapi import APIRouter

from app.api.v1.endpoints import config, health, plugins, settings, wake_word

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(config.router, tags=["config"])
api_router.include_router(plugins.router, tags=["plugins"])
api_router.include_router(settings.router, tags=["settings"])
api_router.include_router(wake_word.router, tags=["wake-word"])
