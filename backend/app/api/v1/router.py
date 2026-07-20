"""Aggregates all v1 API endpoint routers."""

from fastapi import APIRouter

from app.api.v1.endpoints import config, health

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(config.router, tags=["config"])
