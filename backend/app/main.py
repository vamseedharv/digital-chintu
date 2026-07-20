"""FastAPI application factory and entrypoint (`uvicorn app.main:app`)."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.plugins import DiscoveredPlugin, discover_plugins, register_plugins
from app.core.scheduler import scheduler

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    scheduler.start()
    plugins: list[DiscoveredPlugin] = getattr(app.state, "plugins", [])
    for item in plugins:
        if not item.enabled:
            continue
        try:
            await item.plugin.on_startup()
        except Exception:
            logger.exception("Plugin '%s' failed to start up", item.plugin.metadata.slug)
    try:
        yield
    finally:
        for item in plugins:
            if not item.enabled:
                continue
            try:
                await item.plugin.on_shutdown()
            except Exception:
                logger.exception("Plugin '%s' failed to shut down", item.plugin.metadata.slug)
        scheduler.shutdown()


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()

    app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.api_v1_prefix)

    discovered_plugins = discover_plugins(Path(settings.plugins_dir), settings.enabled_plugins_set)
    register_plugins(app, discovered_plugins, settings.api_v1_prefix)

    return app


app = create_app()
