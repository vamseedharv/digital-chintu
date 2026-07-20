# tests/fixtures

`sample_utterance.wav` — a synthetic 1-second, 16kHz mono 16-bit PCM tone
standing in for a recorded utterance (see
`backend/tests/unit/test_stt_runtime.py`). It's the correctly-shaped audio
format whisper.cpp/openWakeWord both require, not real speech — tests that
use it inject a fake STT engine that ignores audio content and returns a
canned transcription. It exists to exercise the real audio-loading/framing/
WAV-writing code paths without a live microphone or the optional
`pywhispercpp` dependency (see docs/features/012_Speech_To_Text.md).
