from datetime import UTC, datetime
from typing import Literal

import pytest

from app.core.voice.events import WakeWordEvent, WakeWordEventBus


def _event(trigger: Literal["audio", "manual"] = "manual") -> WakeWordEvent:
    return WakeWordEvent(
        model=None, confidence=1.0, detected_at=datetime.now(UTC), trigger=trigger, audio=None
    )


@pytest.mark.asyncio
async def test_a_subscribed_listener_receives_a_published_event() -> None:
    bus = WakeWordEventBus()
    received: list[WakeWordEvent] = []

    async def listener(event: WakeWordEvent) -> None:
        received.append(event)

    bus.subscribe(listener)
    event = _event()
    await bus.publish(event)

    assert received == [event]


@pytest.mark.asyncio
async def test_an_unsubscribed_listener_no_longer_receives_events() -> None:
    bus = WakeWordEventBus()
    received: list[WakeWordEvent] = []

    async def listener(event: WakeWordEvent) -> None:
        received.append(event)

    bus.subscribe(listener)
    bus.unsubscribe(listener)
    await bus.publish(_event())

    assert received == []


@pytest.mark.asyncio
async def test_one_listener_raising_does_not_stop_others_from_receiving_the_event() -> None:
    bus = WakeWordEventBus()
    received: list[WakeWordEvent] = []

    async def broken_listener(event: WakeWordEvent) -> None:
        raise RuntimeError("boom")

    async def working_listener(event: WakeWordEvent) -> None:
        received.append(event)

    bus.subscribe(broken_listener)
    bus.subscribe(working_listener)
    event = _event()
    await bus.publish(event)

    assert received == [event]


@pytest.mark.asyncio
async def test_publishing_with_no_subscribers_does_not_raise() -> None:
    bus = WakeWordEventBus()

    await bus.publish(_event())
