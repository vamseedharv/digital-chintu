"""The wake-word -> STT handoff contract. `012_STT` subscribes to
`wake_word_events` at its own startup and never needs to touch this module
or anything in app/core/voice/runtime.py — see docs/features/011_Wake_Word.md.
"""

import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class WakeWordEvent:
    """A wake-word detection, audio-driven or a manual/push-to-talk trigger.

    `audio` is a short PCM16 mono 16kHz pre-roll buffer for audio-driven
    detections (see WakeWordRuntime's `preroll_seconds`), letting a future
    STT stage start transcribing without waiting for more audio. Manual
    triggers carry no audio — the push-to-talk endpoint receives none."""

    model: str | None
    confidence: float
    detected_at: datetime
    trigger: Literal["audio", "manual"]
    audio: bytes | None


WakeWordListener = Callable[[WakeWordEvent], Awaitable[None]]


class WakeWordEventBus:
    """A minimal in-process pub/sub. One listener raising doesn't stop the
    others from receiving the event — the same fail-soft isolation
    app/core/plugins.py applies to plugin lifecycle hooks."""

    def __init__(self) -> None:
        self._listeners: list[WakeWordListener] = []

    def subscribe(self, listener: WakeWordListener) -> None:
        self._listeners.append(listener)

    def unsubscribe(self, listener: WakeWordListener) -> None:
        self._listeners.remove(listener)

    async def publish(self, event: WakeWordEvent) -> None:
        for listener in list(self._listeners):
            try:
                await listener(event)
            except Exception:
                logger.exception("Wake-word event listener %r failed", listener)


wake_word_events = WakeWordEventBus()
