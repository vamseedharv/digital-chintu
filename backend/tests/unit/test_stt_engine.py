"""write_pcm16_wav is pure stdlib (wave module) — testable without
pywhispercpp installed. SttEngine's constructor is exercised via its real,
genuine absence in this venv in test_stt_runtime.py, the same pattern
011_Wake_Word used for WakeWordEngine."""

import wave
from pathlib import Path

from app.core.voice.audio import SAMPLE_RATE_HZ
from app.core.voice.stt_engine import write_pcm16_wav


def test_write_pcm16_wav_round_trips_to_the_same_samples(tmp_path: Path) -> None:
    pcm = bytes(range(0, 256)) * 4  # arbitrary even-length byte content
    wav_path = tmp_path / "out.wav"

    write_pcm16_wav(pcm, wav_path)

    with wave.open(str(wav_path), "rb") as wav_file:
        assert wav_file.getnchannels() == 1
        assert wav_file.getsampwidth() == 2
        assert wav_file.getframerate() == SAMPLE_RATE_HZ
        assert wav_file.readframes(wav_file.getnframes()) == pcm


def test_write_pcm16_wav_against_the_recorded_sample_fixture(tmp_path: Path) -> None:
    fixture_path = Path(__file__).parent.parent / "fixtures" / "sample_utterance.wav"
    with wave.open(str(fixture_path), "rb") as fixture:
        assert fixture.getframerate() == SAMPLE_RATE_HZ
        assert fixture.getnchannels() == 1
        pcm = fixture.readframes(fixture.getnframes())

    out_path = tmp_path / "roundtrip.wav"
    write_pcm16_wav(pcm, out_path)

    with wave.open(str(out_path), "rb") as roundtripped:
        assert roundtripped.readframes(roundtripped.getnframes()) == pcm
