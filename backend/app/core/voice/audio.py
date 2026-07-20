"""Audio capture abstraction. `MicrophoneAudioSource` lazily imports
`sounddevice` (an optional `voice` extra, see backend/pyproject.toml) so
importing this module never fails on a machine without it installed or
without a working input device — see docs/features/011_Wake_Word.md."""

from collections.abc import AsyncIterator
from typing import Protocol

# openWakeWord expects 16-bit mono PCM at 16kHz, in multiples of 80ms
# (see https://github.com/dscripka/openWakeWord). 80ms @ 16kHz, 16-bit mono:
SAMPLE_RATE_HZ = 16_000
FRAME_MS = 80
FRAME_SAMPLES = SAMPLE_RATE_HZ * FRAME_MS // 1_000
FRAME_BYTES = FRAME_SAMPLES * 2  # 16-bit samples


class AudioUnavailable(Exception):
    """Raised when no usable audio input exists — missing dependency, no
    input device, or the device failed to open. Always caught one level up
    (WakeWordRuntime.start()); must never crash the backend."""


class AudioSource(Protocol):
    def frames(self) -> AsyncIterator[bytes]:
        """Yield consecutive FRAME_BYTES-sized 16kHz mono PCM16 chunks."""
        ...


class MicrophoneAudioSource:
    """Captures from the system's default (or configured) input device via
    `sounddevice`. Construction raises `AudioUnavailable` if the `voice`
    extra isn't installed or no matching device exists — never at import
    time, only when actually instantiated."""

    def __init__(self, device: str = "") -> None:
        try:
            import sounddevice  # noqa: F401
        except ImportError as exc:
            raise AudioUnavailable(
                "sounddevice is not installed — run `pip install '.[voice]'` "
                "to enable microphone capture"
            ) from exc

        self._sounddevice = sounddevice
        self._device = device or None
        try:
            # Raises sounddevice.PortAudioError (subclass of Exception) if
            # the device doesn't exist or can't be opened.
            sounddevice.check_input_settings(
                device=self._device, samplerate=SAMPLE_RATE_HZ, channels=1, dtype="int16"
            )
        except Exception as exc:
            raise AudioUnavailable(f"no usable audio input device: {exc}") from exc

    async def frames(self) -> AsyncIterator[bytes]:
        import asyncio

        loop = asyncio.get_running_loop()
        queue: asyncio.Queue[bytes] = asyncio.Queue(maxsize=32)

        def _callback(indata: object, frame_count: int, time_info: object, status: object) -> None:
            data = bytes(indata)  # type: ignore[call-overload]
            loop.call_soon_threadsafe(queue.put_nowait, data)

        stream = self._sounddevice.RawInputStream(
            samplerate=SAMPLE_RATE_HZ,
            blocksize=FRAME_SAMPLES,
            device=self._device,
            channels=1,
            dtype="int16",
            callback=_callback,
        )
        with stream:
            while True:
                yield await queue.get()
