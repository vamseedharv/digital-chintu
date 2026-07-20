"""SttRuntime tests. `test_missing_voice_dependencies_degrade_gracefully...`
relies on pywhispercpp genuinely not being installed in this dev/CI venv to
exercise the real ImportError fail-soft path. Everything else is driven by
a fake engine and audio frames read from the recorded (synthetic) fixture
WAV — see tests/fixtures/README.md — so no real mic or ML model is needed."""

import asyncio
import wave
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.core.voice.audio import FRAME_BYTES, AudioUnavailable
from app.core.voice.events import WakeWordEvent, WakeWordEventBus
from app.core.voice.stt_events import TranscriptionEvent, TranscriptionEventBus
from app.core.voice.stt_runtime import SttRuntime

_FIXTURE_PATH = Path(__file__).parent.parent / "fixtures" / "sample_utterance.wav"


def _load_fixture_frames() -> list[bytes]:
    with wave.open(str(_FIXTURE_PATH), "rb") as wav_file:
        pcm = wav_file.readframes(wav_file.getnframes())
    frame_count = len(pcm) // FRAME_BYTES
    return [pcm[i * FRAME_BYTES : (i + 1) * FRAME_BYTES] for i in range(frame_count)]


_FIXTURE_FRAMES = _load_fixture_frames()


class _FakeAudioSource:
    def __init__(self, frames: list[bytes]) -> None:
        self._frames = frames

    async def frames(self) -> AsyncIterator[bytes]:
        for frame in self._frames:
            yield frame
        await asyncio.Event().wait()  # a real mic stream never ends on its own


class _RaisingAudioSourceFactory:
    def __call__(self) -> _FakeAudioSource:
        raise AudioUnavailable("no usable audio input device: simulated failure")


class _FakeEngine:
    def __init__(self, text: str = "turn on the lights") -> None:
        self.text = text
        self.received_pcm: list[bytes] = []

    def transcribe(self, pcm: bytes) -> str:
        self.received_pcm.append(pcm)
        return self.text


def _wake_event(trigger: str = "audio") -> WakeWordEvent:
    return WakeWordEvent(
        model="hey_jarvis" if trigger == "audio" else None,
        confidence=0.9,
        detected_at=datetime.now(UTC),
        trigger=trigger,  # type: ignore[arg-type]
        audio=None,
    )


def _make_runtime(**overrides: object) -> SttRuntime:
    defaults: dict[str, object] = {"model_name": "tiny.en", "utterance_seconds": 0.5}
    defaults.update(overrides)
    return SttRuntime(**defaults)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_disabled_via_settings_never_subscribes() -> None:
    wake_bus = WakeWordEventBus()
    runtime = _make_runtime(wake_bus=wake_bus)

    await runtime.start(enabled=False)

    assert runtime.status.available is False
    assert runtime.status.enabled is False
    assert "disabled via settings" in (runtime.status.reason or "")
    await runtime.stop()  # must be a safe no-op


@pytest.mark.asyncio
async def test_missing_voice_dependencies_degrade_gracefully_instead_of_raising() -> None:
    # No engine injected, and pywhispercpp genuinely isn't installed in this
    # venv (see backend/pyproject.toml's `voice` extra) — start() must not raise.
    runtime = _make_runtime()

    await runtime.start(enabled=True)

    assert runtime.status.available is False
    assert runtime.status.enabled is True
    assert runtime.status.reason is not None
    await runtime.stop()


@pytest.mark.asyncio
async def test_stop_before_start_is_a_safe_no_op() -> None:
    runtime = _make_runtime()

    await runtime.stop()

    assert runtime.status.available is False


@pytest.mark.asyncio
async def test_a_wake_event_triggers_capture_and_publishes_a_transcription() -> None:
    engine = _FakeEngine(text="turn on the lights")
    wake_bus = WakeWordEventBus()
    transcription_bus = TranscriptionEventBus()
    received: list[TranscriptionEvent] = []
    got_event = asyncio.Event()

    async def listener(event: TranscriptionEvent) -> None:
        received.append(event)
        got_event.set()

    transcription_bus.subscribe(listener)
    runtime = _make_runtime(
        engine=engine,
        wake_bus=wake_bus,
        transcription_bus=transcription_bus,
        audio_source_factory=lambda: _FakeAudioSource(_FIXTURE_FRAMES),
    )
    await runtime.start(enabled=True)
    assert runtime.status.available is True
    assert runtime.status.model == "tiny.en"

    wake_event = _wake_event()
    await wake_bus.publish(wake_event)
    await asyncio.wait_for(got_event.wait(), timeout=1)
    await runtime.stop()

    assert len(received) == 1
    event = received[0]
    assert event.text == "turn on the lights"
    assert event.wake_event is wake_event
    assert engine.received_pcm == [b"".join(_FIXTURE_FRAMES[:6])]  # 0.5s @ 80ms/frame
    assert runtime.status.last_transcription == "turn on the lights"
    assert runtime.status.last_transcribed_at == event.transcribed_at


@pytest.mark.asyncio
async def test_a_manual_trigger_wake_event_also_produces_a_transcription() -> None:
    engine = _FakeEngine(text="what's the weather")
    wake_bus = WakeWordEventBus()
    transcription_bus = TranscriptionEventBus()
    received: list[TranscriptionEvent] = []
    got_event = asyncio.Event()

    async def listener(event: TranscriptionEvent) -> None:
        received.append(event)
        got_event.set()

    transcription_bus.subscribe(listener)
    runtime = _make_runtime(
        engine=engine,
        wake_bus=wake_bus,
        transcription_bus=transcription_bus,
        audio_source_factory=lambda: _FakeAudioSource(_FIXTURE_FRAMES),
    )
    await runtime.start(enabled=True)

    await wake_bus.publish(_wake_event(trigger="manual"))
    await asyncio.wait_for(got_event.wait(), timeout=1)
    await runtime.stop()

    assert received[0].text == "what's the weather"
    assert received[0].wake_event.trigger == "manual"


@pytest.mark.asyncio
async def test_an_empty_transcription_publishes_nothing() -> None:
    engine = _FakeEngine(text="")
    wake_bus = WakeWordEventBus()
    transcription_bus = TranscriptionEventBus()
    received: list[TranscriptionEvent] = []

    async def listener(event: TranscriptionEvent) -> None:
        received.append(event)

    transcription_bus.subscribe(listener)
    runtime = _make_runtime(
        engine=engine,
        wake_bus=wake_bus,
        transcription_bus=transcription_bus,
        audio_source_factory=lambda: _FakeAudioSource(_FIXTURE_FRAMES),
    )
    await runtime.start(enabled=True)

    await wake_bus.publish(_wake_event())
    await asyncio.sleep(0.2)
    await runtime.stop()

    assert received == []
    assert runtime.status.last_transcription is None


@pytest.mark.asyncio
async def test_overlapping_wake_events_are_ignored_while_already_capturing() -> None:
    engine = _FakeEngine(text="hello")
    wake_bus = WakeWordEventBus()
    transcription_bus = TranscriptionEventBus()
    received: list[TranscriptionEvent] = []

    async def listener(event: TranscriptionEvent) -> None:
        received.append(event)

    transcription_bus.subscribe(listener)
    runtime = _make_runtime(
        engine=engine,
        wake_bus=wake_bus,
        transcription_bus=transcription_bus,
        audio_source_factory=lambda: _FakeAudioSource(_FIXTURE_FRAMES),
    )
    await runtime.start(enabled=True)

    await wake_bus.publish(_wake_event())
    await wake_bus.publish(_wake_event())  # should be dropped — already capturing
    await asyncio.sleep(0.3)
    await runtime.stop()

    assert len(received) == 1


@pytest.mark.asyncio
async def test_a_crashing_engine_does_not_raise_and_resets_for_the_next_wake() -> None:
    class _CrashingEngine:
        def __init__(self) -> None:
            self.call_count = 0

        def transcribe(self, pcm: bytes) -> str:
            self.call_count += 1
            raise RuntimeError("boom")

    engine = _CrashingEngine()
    wake_bus = WakeWordEventBus()
    runtime = _make_runtime(
        engine=engine,
        wake_bus=wake_bus,
        audio_source_factory=lambda: _FakeAudioSource(_FIXTURE_FRAMES),
    )
    await runtime.start(enabled=True)

    await wake_bus.publish(_wake_event())
    await asyncio.sleep(0.1)
    assert engine.call_count == 1
    assert runtime.status.last_transcription is None

    # The crash must have reset _capturing (not left it stuck True), so a
    # second wake event still triggers a new capture attempt.
    await wake_bus.publish(_wake_event())
    await asyncio.sleep(0.1)
    await runtime.stop()

    assert engine.call_count == 2


@pytest.mark.asyncio
async def test_audio_capture_failure_degrades_gracefully_without_raising() -> None:
    engine = _FakeEngine()
    wake_bus = WakeWordEventBus()
    runtime = _make_runtime(
        engine=engine, wake_bus=wake_bus, audio_source_factory=_RaisingAudioSourceFactory()
    )
    await runtime.start(enabled=True)

    await wake_bus.publish(_wake_event())
    await asyncio.sleep(0.1)

    assert runtime.status.last_transcription is None
    await runtime.stop()
