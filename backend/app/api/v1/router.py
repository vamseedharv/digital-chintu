"""Aggregates all v1 API endpoint routers."""

from fastapi import APIRouter

from app.api.v1.endpoints import config, health, plugins

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(config.router, tags=["config"])
api_router.include_router(plugins.router, tags=["plugins"])
