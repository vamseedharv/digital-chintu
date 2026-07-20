"""Wraps whisper.cpp transcription via `pywhispercpp`. Lazily imports it (an
optional `voice` extra, see backend/pyproject.toml) so importing this module
never fails on a machine without it installed — see
docs/features/012_Speech_To_Text.md. Model sizing trade-off (why "tiny.en"
is the default, not a larger/more accurate model) is documented on
`Settings.stt_model` in app/core/config.py and in
docs/architecture/07_DEPLOYMENT.md."""

import tempfile
import wave
from pathlib import Path

from app.core.voice.audio import SAMPLE_RATE_HZ


class TranscriptionUnavailable(Exception):
    """Raised when the STT engine can't be constructed — library not
    installed, or the model files couldn't be downloaded/loaded (e.g. no
    network on first run). Always caught one level up
    (SttRuntime.start()); must never crash the backend."""


def write_pcm16_wav(pcm: bytes, path: Path) -> None:
    """Writes raw 16-bit mono PCM at SAMPLE_RATE_HZ to a WAV file — whisper.cpp
    (via pywhispercpp) only documents accepting a file path, not a raw
    buffer, so this is how captured audio reaches it. Pure stdlib, so it's
    testable without pywhispercpp installed."""
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(SAMPLE_RATE_HZ)
        wav_file.writeframes(pcm)


class SttEngine:
    """Loads a single whisper.cpp model and transcribes captured utterances."""

    def __init__(self, model_name: str) -> None:
        try:
            from pywhispercpp.model import Model
        except ImportError as exc:
            raise TranscriptionUnavailable(
                "pywhispercpp is not installed — run `pip install '.[voice]'` "
                "to enable speech-to-text"
            ) from exc

        try:
            self._model = Model(model_name, print_realtime=False, print_progress=False)
        except Exception as exc:
            raise TranscriptionUnavailable(
                f"could not load STT model '{model_name}': {exc}"
            ) from exc

    def transcribe(self, pcm: bytes) -> str:
        """Blocking — run via `asyncio.to_thread` from async code."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            wav_path = Path(tmp_dir) / "utterance.wav"
            write_pcm16_wav(pcm, wav_path)
            segments = self._model.transcribe(str(wav_path))
        return " ".join(segment.text.strip() for segment in segments).strip()
