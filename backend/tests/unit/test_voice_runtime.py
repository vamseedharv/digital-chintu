"""WakeWordRuntime tests. `test_missing_voice_dependencies_...` relies on
the `voice` extras genuinely not being installed in this dev/CI venv to
exercise the real fail-soft path — everything else uses small injected
fakes so no real audio hardware or ML model is ever needed."""

import asyncio
from collections.abc import AsyncIterator

import pytest

from app.core.voice.engine import Detection
from app.core.voice.events import WakeWordEvent, WakeWordEventBus
from app.core.voice.runtime import WakeWordRuntime


class _FakeAudioSource:
    def __init__(self, frames: list[bytes]) -> None:
        self._frames = frames

    async def frames(self) -> AsyncIterator[bytes]:
        for frame in self._frames:
            yield frame
        # A real mic stream never ends on its own — block so the listen
        # loop only stops via cancellation (runtime.stop()), same as prod.
        await asyncio.Event().wait()


class _FakeEngine:
    def __init__(self, hits_on: set[bytes]) -> None:
        self._hits_on = hits_on

    def detect(self, frame: bytes) -> list[Detection]:
        if frame in self._hits_on:
            return [Detection(model="fake-model", confidence=0.9)]
        return []


def _make_runtime(**overrides: object) -> WakeWordRuntime:
    defaults: dict[str, object] = {
        "model_name": "hey_jarvis",
        "sensitivity": 0.5,
        "preroll_seconds": 1.0,
    }
    defaults.update(overrides)
    return WakeWordRuntime(**defaults)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_disabled_via_settings_never_starts_listening() -> None:
    runtime = _make_runtime()

    await runtime.start(enabled=False)

    assert runtime.status.listening is False
    assert runtime.status.enabled is False
    assert "disabled via settings" in (runtime.status.reason or "")
    await runtime.stop()  # must be a safe no-op


@pytest.mark.asyncio
async def test_missing_voice_dependencies_degrade_gracefully_instead_of_raising() -> None:
    # No engine/audio_source injected, and openwakeword/sounddevice genuinely
    # aren't installed in this venv (see backend/pyproject.toml's `voice`
    # extra) — start() must not raise.
    runtime = _make_runtime()

    await runtime.start(enabled=True)

    assert runtime.status.listening is False
    assert runtime.status.enabled is True
    assert runtime.status.reason is not None
    await runtime.stop()


@pytest.mark.asyncio
async def test_stop_before_start_is_a_safe_no_op() -> None:
    runtime = _make_runtime()

    await runtime.stop()

    assert runtime.status.listening is False


@pytest.mark.asyncio
async def test_a_detection_publishes_an_event_with_the_preroll_buffer() -> None:
    frames = [b"A" * 2560, b"B" * 2560, b"C" * 2560]
    engine = _FakeEngine(hits_on={frames[-1]})
    audio_source = _FakeAudioSource(frames)
    bus = WakeWordEventBus()
    received: list[WakeWordEvent] = []
    got_event = asyncio.Event()

    async def listener(event: WakeWordEvent) -> None:
        received.append(event)
        got_event.set()

    bus.subscribe(listener)
    runtime = _make_runtime(event_bus=bus, engine=engine, audio_source=audio_source)

    await runtime.start(enabled=True)
    assert runtime.status.listening is True
    assert runtime.status.model == "hey_jarvis"

    await asyncio.wait_for(got_event.wait(), timeout=1)
    await runtime.stop()

    assert len(received) == 1
    event = received[0]
    assert event.trigger == "audio"
    assert event.model == "fake-model"
    assert event.confidence == 0.9
    assert event.audio == b"".join(frames)


@pytest.mark.asyncio
async def test_no_detection_publishes_nothing() -> None:
    frames = [b"A" * 2560, b"B" * 2560]
    engine = _FakeEngine(hits_on=set())
    audio_source = _FakeAudioSource(frames)
    bus = WakeWordEventBus()
    received: list[WakeWordEvent] = []

    async def listener(event: WakeWordEvent) -> None:
        received.append(event)

    bus.subscribe(listener)
    runtime = _make_runtime(event_bus=bus, engine=engine, audio_source=audio_source)
    await runtime.start(enabled=True)
    await asyncio.sleep(0.05)
    await runtime.stop()

    assert received == []


@pytest.mark.asyncio
async def test_a_crashing_engine_stops_listening_without_raising() -> None:
    class _CrashingEngine:
        def detect(self, frame: bytes) -> list[Detection]:
            raise RuntimeError("boom")

    audio_source = _FakeAudioSource([b"A" * 2560])
    runtime = _make_runtime(engine=_CrashingEngine(), audio_source=audio_source)

    await runtime.start(enabled=True)
    assert runtime.status.listening is True

    # Give the listen loop a turn to run, hit the crash, and update status.
    for _ in range(50):
        if runtime.status.listening is False:
            break
        await asyncio.sleep(0.01)

    assert runtime.status.listening is False
    assert runtime.status.reason == "listen loop crashed — see backend logs"
    await runtime.stop()  # still a safe no-op afterward


@pytest.mark.asyncio
async def test_manual_trigger_works_regardless_of_listening_state() -> None:
    bus = WakeWordEventBus()
    received: list[WakeWordEvent] = []

    async def listener(event: WakeWordEvent) -> None:
        received.append(event)

    bus.subscribe(listener)
    runtime = _make_runtime(event_bus=bus)  # no engine/audio_source -> unavailable
    await runtime.start(enabled=True)
    assert runtime.status.listening is False

    event = await runtime.trigger_manual()

    assert received == [event]
    assert event.trigger == "manual"
    assert event.model is None
    assert event.audio is None


@pytest.mark.asyncio
async def test_manual_trigger_works_when_disabled_via_settings() -> None:
    bus = WakeWordEventBus()
    runtime = _make_runtime(event_bus=bus)
    await runtime.start(enabled=False)

    event = await runtime.trigger_manual()

    assert event.trigger == "manual"
