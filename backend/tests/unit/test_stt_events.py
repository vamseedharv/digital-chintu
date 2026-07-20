from datetime import UTC, datetime

import pytest

from app.core.voice.events import WakeWordEvent
from app.core.voice.stt_events import TranscriptionEvent, TranscriptionEventBus


def _wake_event() -> WakeWordEvent:
    return WakeWordEvent(
        model=None, confidence=1.0, detected_at=datetime.now(UTC), trigger="manual", audio=None
    )


def _transcription_event(text: str = "turn on the lights") -> TranscriptionEvent:
    return TranscriptionEvent(
        text=text, confidence=None, transcribed_at=datetime.now(UTC), wake_event=_wake_event()
    )


@pytest.mark.asyncio
async def test_a_subscribed_listener_receives_a_published_event() -> None:
    bus = TranscriptionEventBus()
    received: list[TranscriptionEvent] = []

    async def listener(event: TranscriptionEvent) -> None:
        received.append(event)

    bus.subscribe(listener)
    event = _transcription_event()
    await bus.publish(event)

    assert received == [event]


@pytest.mark.asyncio
async def test_an_unsubscribed_listener_no_longer_receives_events() -> None:
    bus = TranscriptionEventBus()
    received: list[TranscriptionEvent] = []

    async def listener(event: TranscriptionEvent) -> None:
        received.append(event)

    bus.subscribe(listener)
    bus.unsubscribe(listener)
    await bus.publish(_transcription_event())

    assert received == []


@pytest.mark.asyncio
async def test_one_listener_raising_does_not_stop_others_from_receiving_the_event() -> None:
    bus = TranscriptionEventBus()
    received: list[TranscriptionEvent] = []

    async def broken_listener(event: TranscriptionEvent) -> None:
        raise RuntimeError("boom")

    async def working_listener(event: TranscriptionEvent) -> None:
        received.append(event)

    bus.subscribe(broken_listener)
    bus.subscribe(working_listener)
    event = _transcription_event()
    await bus.publish(event)

    assert received == [event]


def test_transcription_event_carries_the_triggering_wake_event() -> None:
    wake_event = _wake_event()
    event = TranscriptionEvent(
        text="hello", confidence=None, transcribed_at=datetime.now(UTC), wake_event=wake_event
    )

    assert event.wake_event is wake_event
