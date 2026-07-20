"""Orchestrates speech-to-text: subscribes to the wake-word event bus (no
changes to app/core/voice/runtime.py or events.py needed — that interface
is treated as stable, per docs/features/012_Speech_To_Text.md's
precondition), captures a short utterance via its own AudioSource instance
after each wake, transcribes it off the event loop, and publishes a
TranscriptionEvent for 015_Intent_Router to consume."""

import asyncio
import contextlib
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime

from app.core.voice.audio import AudioSource, AudioUnavailable, MicrophoneAudioSource
from app.core.voice.events import WakeWordEvent, WakeWordEventBus, wake_word_events
from app.core.voice.stt_engine import SttEngine, TranscriptionUnavailable
from app.core.voice.stt_events import (
    TranscriptionEvent,
    TranscriptionEventBus,
    transcription_events,
)

logger = logging.getLogger(__name__)

_FRAME_MS = 80


@dataclass(frozen=True)
class SttStatus:
    enabled: bool
    available: bool
    model: str | None
    reason: str | None
    last_transcription: str | None
    last_transcribed_at: datetime | None


class SttRuntime:
    """`engine`/`audio_source_factory` are injectable so tests can drive
    this with small fakes — no real pywhispercpp/sounddevice needed. When
    omitted, `start()` constructs the real engine (where an ImportError or
    model-load failure surfaces and is caught) and each capture opens a
    fresh real `MicrophoneAudioSource`.

    Construction takes no DB-dependent state (`stt_enabled` lives in the
    settings DB) — `enabled` is a parameter of `start()` instead, mirroring
    WakeWordRuntime exactly (see its docstring for why)."""

    def __init__(
        self,
        *,
        model_name: str,
        utterance_seconds: float,
        audio_device: str = "",
        wake_bus: WakeWordEventBus = wake_word_events,
        transcription_bus: TranscriptionEventBus = transcription_events,
        engine: SttEngine | None = None,
        audio_source_factory: Callable[[], AudioSource] | None = None,
    ) -> None:
        self._model_name = model_name
        self._utterance_seconds = utterance_seconds
        self._audio_device = audio_device
        self._wake_bus = wake_bus
        self._transcription_bus = transcription_bus
        self._injected_engine = engine
        self._audio_source_factory = audio_source_factory or self._default_audio_source_factory

        self._enabled = False
        self._available = False
        self._reason: str | None = "STT runtime has not started yet"
        self._engine: SttEngine | None = None
        self._capturing = False
        self._last_transcription: str | None = None
        self._last_transcribed_at: datetime | None = None
        self._tasks: set[asyncio.Task[None]] = set()

    def _default_audio_source_factory(self) -> AudioSource:
        return MicrophoneAudioSource(self._audio_device)

    @property
    def status(self) -> SttStatus:
        return SttStatus(
            enabled=self._enabled,
            available=self._available,
            model=self._model_name if self._available else None,
            reason=self._reason,
            last_transcription=self._last_transcription,
            last_transcribed_at=self._last_transcribed_at,
        )

    async def start(self, *, enabled: bool) -> None:
        self._enabled = enabled
        if not enabled:
            self._reason = "disabled via settings (stt_enabled=false)"
            logger.info("Speech-to-text is disabled via settings")
            return

        try:
            engine = self._injected_engine or SttEngine(self._model_name)
        except TranscriptionUnavailable as exc:
            self._reason = str(exc)
            logger.warning("Speech-to-text unavailable: %s", exc)
            return

        self._engine = engine
        self._available = True
        self._reason = None
        self._wake_bus.subscribe(self._on_wake)

    async def stop(self) -> None:
        if self._available:
            self._wake_bus.unsubscribe(self._on_wake)
            self._available = False
        self._engine = None

        tasks = list(self._tasks)
        for task in tasks:
            task.cancel()
        for task in tasks:
            with contextlib.suppress(asyncio.CancelledError):
                await task

    async def _on_wake(self, event: WakeWordEvent) -> None:
        # Fire-and-forget: must return immediately. WakeWordEventBus.publish()
        # awaits each listener in turn, so blocking here for the several
        # seconds a capture takes would stall the wake-word listen loop
        # itself and overflow its audio queue.
        #
        # _capturing is set here, synchronously, rather than at the top of
        # _capture_and_transcribe — that task body doesn't actually start
        # running until the next event-loop iteration, which left a window
        # where two wake events published back-to-back (no `await` between
        # them yielding control) could both see _capturing as False and both
        # start a capture.
        if self._capturing:
            logger.info("Ignoring wake event — already capturing an utterance")
            return
        self._capturing = True
        task = asyncio.create_task(self._capture_and_transcribe(event))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    async def _capture_and_transcribe(self, wake_event: WakeWordEvent) -> None:
        try:
            engine = self._engine
            assert engine is not None  # only subscribed to wake_bus while set
            audio_source = self._audio_source_factory()
            pcm = await self._capture_utterance(audio_source)
            text = await asyncio.to_thread(engine.transcribe, pcm)
            if not text:
                return
            transcribed_at = datetime.now(UTC)
            self._last_transcription = text
            self._last_transcribed_at = transcribed_at
            await self._transcription_bus.publish(
                TranscriptionEvent(
                    text=text, confidence=None, transcribed_at=transcribed_at, wake_event=wake_event
                )
            )
        except AudioUnavailable as exc:
            logger.warning("STT couldn't capture audio for an utterance: %s", exc)
        except Exception:
            logger.exception("STT failed to transcribe an utterance")
        finally:
            self._capturing = False

    async def _capture_utterance(self, audio_source: AudioSource) -> bytes:
        frame_count = max(1, round(self._utterance_seconds * 1000 / _FRAME_MS))
        frames: list[bytes] = []
        frame_source = audio_source.frames()
        try:
            async for frame in frame_source:
                frames.append(frame)
                if len(frames) >= frame_count:
                    break
        finally:
            aclose = getattr(frame_source, "aclose", None)
            if aclose is not None:
                await aclose()
        return b"".join(frames)
