"""The STT -> intent-router handoff contract. `015_Intent_Router` subscribes
to `transcription_events` at its own startup and never needs to touch this
module or anything in app/core/voice/stt_runtime.py — same shape as
app/core/voice/events.py's wake-word handoff (see
docs/features/012_Speech_To_Text.md)."""

import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime

from app.core.voice.events import WakeWordEvent

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TranscriptionEvent:
    """A speech-to-text result for one captured utterance.

    `wake_event` is the WakeWordEvent that triggered this capture — carries
    the original trigger type ("audio"/"manual") and timestamp, so a
    consumer doesn't need a second correlation mechanism. `confidence` is
    `None` when the underlying engine doesn't expose a meaningful score."""

    text: str
    confidence: float | None
    transcribed_at: datetime
    wake_event: WakeWordEvent


TranscriptionListener = Callable[[TranscriptionEvent], Awaitable[None]]


class TranscriptionEventBus:
    """A minimal in-process pub/sub, identical in shape to
    app/core/voice/events.py's WakeWordEventBus — one listener raising
    doesn't stop the others from receiving the event."""

    def __init__(self) -> None:
        self._listeners: list[TranscriptionListener] = []

    def subscribe(self, listener: TranscriptionListener) -> None:
        self._listeners.append(listener)

    def unsubscribe(self, listener: TranscriptionListener) -> None:
        self._listeners.remove(listener)

    async def publish(self, event: TranscriptionEvent) -> None:
        for listener in list(self._listeners):
            try:
                await listener(event)
            except Exception:
                logger.exception("Transcription event listener %r failed", listener)


transcription_events = TranscriptionEventBus()
