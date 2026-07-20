"""FastAPI application factory and entrypoint (`uvicorn app.main:app`)."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.plugins import DiscoveredPlugin, discover_plugins, register_plugins
from app.core.scheduler import scheduler
from app.core.voice.runtime import WakeWordRuntime
from app.core.voice.stt_runtime import SttRuntime
from app.db.session import get_db
from app.repositories.settings_repository import SettingsRepository
from app.services.settings_service import SettingsService

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

    wake_word_runtime: WakeWordRuntime = app.state.wake_word_runtime
    stt_runtime: SttRuntime = app.state.stt_runtime
    try:
        # Resolve via whatever get_db dependency is currently installed
        # (respects test overrides — see tests/conftest.py's make_test_client
        # — rather than always hitting the real configured database).
        db_dependency = app.dependency_overrides.get(get_db, get_db)
        with contextmanager(db_dependency)() as db:
            effective_settings = SettingsService(SettingsRepository(db)).get_effective_settings()
    except Exception:
        logger.exception("Failed to resolve voice-pipeline settings; leaving both disabled")
        effective_settings = None

    try:
        await wake_word_runtime.start(
            enabled=effective_settings.wake_word_enabled if effective_settings else False
        )
    except Exception:
        logger.exception("Wake-word runtime failed to start")

    try:
        stt_enabled = effective_settings.stt_enabled if effective_settings else False
        await stt_runtime.start(enabled=stt_enabled)
    except Exception:
        logger.exception("STT runtime failed to start")

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
        try:
            await stt_runtime.stop()
        except Exception:
            logger.exception("STT runtime failed to stop")
        try:
            await wake_word_runtime.stop()
        except Exception:
            logger.exception("Wake-word runtime failed to stop")
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

    # No DB access here — dependency overrides (see tests/conftest.py) aren't
    # installed until after create_app() returns, so the DB-backed
    # wake_word_enabled/stt_enabled toggles are resolved later, in
    # lifespan(). Constructing these runtimes needs no DB and is always safe.
    app.state.wake_word_runtime = WakeWordRuntime(
        model_name=settings.wake_word_model,
        sensitivity=settings.wake_word_sensitivity,
        preroll_seconds=settings.wake_word_preroll_seconds,
        audio_device=settings.voice_audio_device,
    )
    app.state.stt_runtime = SttRuntime(
        model_name=settings.stt_model,
        utterance_seconds=settings.stt_utterance_seconds,
        audio_device=settings.voice_audio_device,
    )

    return app


app = create_app()
