"""Orchestrates wake-word detection: builds the engine/audio source (or
degrades gracefully if either is unavailable), runs the listen loop as a
background asyncio.Task alongside the app lifespan (main.py), and always
offers a manual/push-to-talk fallback regardless of that state — the
documented degradation path for hardware/dependency-constrained deployments.
See docs/features/011_Wake_Word.md."""

import asyncio
import contextlib
import logging
from collections import deque
from dataclasses import dataclass
from datetime import UTC, datetime

from app.core.voice.audio import AudioSource, AudioUnavailable, MicrophoneAudioSource
from app.core.voice.engine import ModelUnavailable, WakeWordEngine
from app.core.voice.events import WakeWordEvent, WakeWordEventBus, wake_word_events

logger = logging.getLogger(__name__)

_FRAME_MS = 80


@dataclass(frozen=True)
class WakeWordStatus:
    enabled: bool
    listening: bool
    model: str | None
    reason: str | None


class WakeWordRuntime:
    """`engine`/`audio_source` are injectable so tests can drive this with
    small fakes — no real openwakeword/sounddevice needed. When omitted,
    `start()` constructs the real implementations, which is where an
    ImportError/missing-device/download failure surfaces and is caught.

    Construction takes no DB-dependent state (`wake_word_enabled` lives in
    the settings DB) — `enabled` is a parameter of `start()` instead, so a
    runtime instance can always be created safely in `main.py`'s
    `create_app()` (no database touched, no dependency-override timing
    issues) while the actual DB-backed toggle is resolved later, inside
    `lifespan()`, once request-scoped dependency overrides are in place."""

    def __init__(
        self,
        *,
        model_name: str,
        sensitivity: float,
        preroll_seconds: float,
        audio_device: str = "",
        event_bus: WakeWordEventBus = wake_word_events,
        engine: WakeWordEngine | None = None,
        audio_source: AudioSource | None = None,
    ) -> None:
        self._model_name = model_name
        self._sensitivity = sensitivity
        self._preroll_seconds = preroll_seconds
        self._audio_device = audio_device
        self._event_bus = event_bus
        self._injected_engine = engine
        self._injected_audio_source = audio_source

        self._enabled = False
        self._listening = False
        self._reason: str | None = "wake-word runtime has not started yet"
        self._task: asyncio.Task[None] | None = None

    @property
    def status(self) -> WakeWordStatus:
        return WakeWordStatus(
            enabled=self._enabled,
            listening=self._listening,
            model=self._model_name if self._listening else None,
            reason=self._reason,
        )

    async def start(self, *, enabled: bool) -> None:
        self._enabled = enabled
        if not enabled:
            self._reason = "disabled via settings (wake_word_enabled=false)"
            logger.info("Wake-word detection is disabled via settings")
            return

        try:
            engine = self._injected_engine or WakeWordEngine(self._model_name, self._sensitivity)
            audio_source = self._injected_audio_source or MicrophoneAudioSource(
                self._audio_device
            )
        except (ModelUnavailable, AudioUnavailable) as exc:
            self._reason = str(exc)
            logger.warning("Wake-word detection unavailable: %s", exc)
            return

        self._task = asyncio.create_task(self._listen_loop(engine, audio_source))
        self._listening = True

    async def stop(self) -> None:
        if self._task is None:
            return
        task = self._task
        self._task = None
        self._listening = False
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task

    async def trigger_manual(self) -> WakeWordEvent:
        """Always works, regardless of `enabled`/`listening` — the
        documented push-to-talk fallback."""
        event = WakeWordEvent(
            model=None,
            confidence=1.0,
            detected_at=datetime.now(UTC),
            trigger="manual",
            audio=None,
        )
        await self._event_bus.publish(event)
        return event

    async def _listen_loop(self, engine: WakeWordEngine, audio_source: AudioSource) -> None:
        preroll_frames = max(1, round(self._preroll_seconds * 1000 / _FRAME_MS))
        buffer: deque[bytes] = deque(maxlen=preroll_frames)
        try:
            async for frame in audio_source.frames():
                buffer.append(frame)
                for detection in engine.detect(frame):
                    event = WakeWordEvent(
                        model=detection.model,
                        confidence=detection.confidence,
                        detected_at=datetime.now(UTC),
                        trigger="audio",
                        audio=b"".join(buffer),
                    )
                    await self._event_bus.publish(event)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Wake-word listen loop crashed; detection stopped")
            self._listening = False
            self._reason = "listen loop crashed — see backend logs"
