# 012 Speech To Text

## Status: Done

On-device speech-to-text via [whisper.cpp](https://github.com/ggml-org/whisper.cpp)
(Python bindings: [`pywhispercpp`](https://github.com/absadiki/pywhispercpp))
is implemented the same way `011_Wake_Word` integrated OpenWakeWord: an
**opt-in** capability (`backend/app/core/voice/stt_*.py`) that always boots
safely, subscribes to `011`'s existing wake-word event bus without any
changes to that code, and hands transcribed text off through a small
pub/sub contract the not-yet-built `015_Intent_Router` will subscribe to.

## Objective

Turn a wake event (real detection or push-to-talk) into transcribed text,
entirely on-device, without requiring cloud STT or breaking on hardware
that can't run it.

## Why whisper.cpp, and why "tiny.en" by default

[whisper.cpp](https://github.com/ggml-org/whisper.cpp) is MIT-licensed
(both the code and the underlying Whisper model weights — notably *not*
the CC-BY-NC-SA restriction `011`'s OpenWakeWord models carry), supports
ARM/Raspberry Pi natively, and uses the exact same audio format `011`
already captures in (16-bit mono PCM at 16kHz) — no new audio pipeline
needed, `app/core/voice/audio.py` is reused as-is.

Model sizing is a real, documented trade-off, not an afterthought (source:
whisper.cpp's own README):

| Model | Disk | RAM | Fits `docker-compose.yml`'s 512m backend `mem_limit`? |
|---|---|---|---|
| tiny(.en) | 75 MiB | ~273 MB | Yes, comfortably — **the default** |
| base(.en) | 142 MiB | ~388 MB | Tight — little headroom left for the rest of the app |
| small | 466 MiB | ~852 MB | No — exceeds the limit outright |
| medium/large | 1.5-2.9 GiB | 2.1-3.9 GB | No — desktop/server hardware only |

`tiny.en` is more accurate than the multilingual `tiny` for English (the
only language this app configures today — `DEFAULT_LANGUAGE`/`032_Multilingual`
isn't implemented) and is the only size that doesn't force raising Docker's
existing memory limit or risk starving the rest of the backend on a
Raspberry Pi. `base`/`small` are real, better-accuracy options an operator
with a Pi 4/5 or a beefier host can opt into via `STT_MODEL` — just not the
safe default. Real-time factor on a Pi 4: `tiny` runs comfortably faster
than real-time; `base` runs around real-time with 4 threads (source:
community benchmarks, not measured on physical hardware by this feature —
see Sources below, same honesty standard `011` set).

## User Stories

- As an operator who already has `011`'s `voice` extra installed and a
  working mic, speaking the wake phrase and then a command produces
  transcribed text automatically, on-device, with no cloud dependency.
- As an operator on constrained hardware or without the extra installed,
  the backend still boots normally; `GET /api/v1/stt/status` explains why
  transcription isn't active, and the wake-word push-to-talk endpoint still
  responds — it just won't produce a transcription.
- As the author of `015_Intent_Router`, I subscribe to
  `app.core.voice.stt_events.transcription_events` at my own startup and
  receive a `TranscriptionEvent` (carrying the text and the `WakeWordEvent`
  that triggered it) whenever an utterance is transcribed — I never need to
  import or modify anything in `app/core/voice/stt_runtime.py`.

## Functional Requirements

1. `backend/app/core/voice/stt_engine.py`'s `SttEngine` wraps a single
   whisper.cpp model, lazily importing `pywhispercpp` so importing the
   module never fails without it installed. `write_pcm16_wav()` (pure
   stdlib) converts captured PCM to the WAV file whisper.cpp's documented
   API expects.
2. `backend/app/core/voice/stt_runtime.py`'s `SttRuntime` subscribes to
   `011`'s `wake_word_events` bus on `start()` (only if enabled and the
   engine constructs successfully) — **no changes to `011`'s `runtime.py`,
   `audio.py`, or `events.py`**, satisfying this feature's precondition
   that the wake-word handoff interface be stable before STT consumes it.
3. On any `WakeWordEvent` (audio-triggered or manual/push-to-talk — STT
   doesn't discriminate), it opens a fresh `MicrophoneAudioSource`,
   captures `stt_utterance_seconds` of audio, transcribes it off the event
   loop (`asyncio.to_thread`), and publishes a `TranscriptionEvent`.
4. The wake-word subscription callback returns immediately and does the
   actual capture/transcription in a tracked background task — blocking
   the callback would stall `011`'s listen loop (which awaits each
   subscriber in turn) for the several seconds a capture takes, overflowing
   its audio queue. A capture in progress causes subsequent wake events to
   be dropped (logged), not queued or run concurrently.
5. `GET /api/v1/stt/status` — introspection, no dedicated trigger endpoint:
   `POST /api/v1/wake-word/trigger` (already built in `011`) is what drives
   STT, since `SttRuntime` just subscribes to the same bus that endpoint
   publishes to.
6. `stt_enabled` is a fifth DB-managed setting (`008_Settings` pattern,
   default `True`), read once at startup — not hot-reloaded, same as
   `wake_word_enabled`.

## Non-goals

No intent routing or command execution (`015`, not started), no
multi-language auto-detection UI, no streaming/partial transcription (a
full utterance is captured, then transcribed once), no cloud STT fallback
(explicit constraint — on-device only for core functionality), no frontend
UI, no Docker audio-device passthrough (same platform limitation `011`
already documents).

## Non-functional Requirements

- Cross-platform: the backend boots identically on Raspberry Pi, Linux,
  Windows, and Docker whether or not the `voice` extra (now including
  `pywhispercpp`) is installed.
- No paid services required — whisper.cpp and its models are free and
  MIT-licensed (no non-commercial restriction, unlike `011`'s wake-word
  models).
- Independently testable without any real audio hardware or ML model — see
  Test Plan.
- Fails safely: a missing dependency, missing model, missing mic, or a
  crash mid-transcription degrades to a `reason`-carrying status and resets
  cleanly for the next wake event, never crashes the backend.

## Backend Design

New files in the existing `backend/app/core/voice/` package (not a
separate package — same cross-cutting tier as `011`'s modules, and
`stt_runtime.py` directly depends on `011`'s `audio.py`/`events.py`):

- `stt_events.py` — `TranscriptionEvent` (frozen dataclass: `text`,
  `confidence: float | None` — `None` since `pywhispercpp` doesn't
  document a segment-level confidence score, not fabricated — `transcribed_at`,
  `wake_event: WakeWordEvent`) and `TranscriptionEventBus`, identical shape
  to `011`'s `WakeWordEventBus`. **This is the `015_Intent_Router`
  integration point.**
- `stt_engine.py` — `SttEngine` (lazy `pywhispercpp` import, model
  auto-downloaded on first construction — same one-time-network-access
  caveat as `011`'s model download), `write_pcm16_wav()`, `TranscriptionUnavailable`.
- `stt_runtime.py` — `SttRuntime`: `engine`/`audio_source_factory` are
  constructor-injectable for tests; `start(enabled=...)` mirrors
  `WakeWordRuntime.start()` exactly (same reasoning: no DB access at
  construction time, `enabled` resolved later in `lifespan()`). Subscribes
  `_on_wake` to the wake bus only when available; `_on_wake` is a fast,
  synchronous-looking check-and-dispatch (sets a `_capturing` flag
  *before* scheduling the background task — an early draft set it inside
  the task body instead, which left a race window where two wake events
  published back-to-back could both start a capture; caught by
  `test_overlapping_wake_events_are_ignored_while_already_capturing`).

`main.py` wiring: `create_app()` constructs both `WakeWordRuntime` and
`SttRuntime` (no DB access, always safe). `lifespan()` resolves both
`wake_word_enabled` and `stt_enabled` from one `SettingsService` call
(reusing the dependency-override-respecting session pattern `011`
established), then starts each runtime independently with its own
try/except — a wake-word startup failure must not prevent STT from at
least attempting to start, and vice versa. Shutdown order: STT first (it
depends on the wake bus), then wake-word, then the scheduler.

## Database

None. `stt_enabled` reuses the existing generic `settings` key/value table
(`008_Settings`) — no new model, no migration.

## APIs

- `GET /api/v1/stt/status` → `{enabled, available, model, reason, last_transcription, last_transcribed_at}`.
  `last_transcription`/`last_transcribed_at` exist purely for
  introspection/manual QA before `015` exists to consume transcriptions for
  real — the same role `GET /api/v1/plugins` and `GET /api/v1/wake-word/status`
  already play for their own subsystems.
- `GET /api/v1/settings` / `PATCH /api/v1/settings` gain `stt_enabled`
  (read/write, independent of `wake_word_enabled` — an operator can run
  always-on wake detection without STT, or vice versa via push-to-talk).

## WebSocket Events

None — `015_Intent_Router` consumes transcriptions via the in-process
`transcription_events` bus, not a client-facing WebSocket (no WS transport
exists anywhere in the app yet).

## Configuration

New env-only, deployment-level `Settings` fields (`backend/app/core/config.py`),
same tier as `011`'s wake-word knobs:

| Setting | Env var | Default |
|---|---|---|
| STT model | `STT_MODEL` | `tiny.en` — see the sizing trade-off table above |
| Utterance capture length | `STT_UTTERANCE_SECONDS` | `5.0` (1-30) |

`VOICE_AUDIO_DEVICE` (from `011`) is reused as-is — both wake-word and STT
capture from the same configured input device.

`stt_enabled` is DB-managed (`008_Settings` pattern) — see APIs above.

Model files aren't bundled in the `pywhispercpp` package; like `011`'s
OpenWakeWord models, they're downloaded once on first real use and cached.
The same air-gapped-deployment caveat applies.

## Test Plan

- **Unit**:
  - `tests/unit/test_stt_events.py` — `TranscriptionEventBus` subscribe/
    unsubscribe/publish with listener-exception isolation, mirroring
    `test_voice_events.py`.
  - `tests/unit/test_stt_engine.py` — `write_pcm16_wav()` round-trips PCM
    bytes correctly (pure stdlib `wave`, no `pywhispercpp` needed),
    verified both against arbitrary bytes and against the recorded fixture
    below.
  - `tests/unit/test_stt_runtime.py` — `SttRuntime` driven by a fake engine
    and an `audio_source_factory` reading frames from
    `tests/fixtures/sample_utterance.wav` (a synthetic, checked-in 1-second
    16kHz mono WAV — see `tests/fixtures/README.md` for why it's synthetic,
    not real recorded speech, and why that's fine: the fake engine ignores
    audio content and returns a canned transcription, so the fixture's job
    is exercising the real framing/capture/WAV-writing code paths with
    correctly-shaped audio, not validating transcription accuracy). Covers:
    a wake event (either trigger type) producing a transcription; an empty
    transcription publishing nothing; overlapping wake events being
    dropped, not queued or run concurrently; a crashing engine recovering
    cleanly for the next wake event; an audio-capture failure degrading
    gracefully. One test
    (`test_missing_voice_dependencies_degrade_gracefully_instead_of_raising`)
    relies on `pywhispercpp` being genuinely absent in this venv — not a
    simulated `ImportError`.
- **Integration** (`tests/integration/test_stt_api.py`): status endpoint
  through `TestClient`, including a real end-to-end check
  (`create_app()` → `lifespan()` → `SettingsService` → `SttRuntime.start()`)
  that the wiring degrades correctly; confirms `POST /api/v1/wake-word/trigger`
  still works with `SttRuntime` wired in; OpenAPI schema coverage. Existing
  settings integration tests updated for the new response field.
- **E2E**: not needed until `015_Intent_Router` gives transcriptions
  something real to drive.

## Manual QA

1. `make backend-dev` (no `voice` extras installed) — confirm the app
   boots normally, `GET /api/v1/stt/status` reports `available: false` with
   a clear `reason`, and `POST /api/v1/wake-word/trigger` still returns 200.
2. `pip install '.[voice]'` (now includes `pywhispercpp`) on a machine with
   a working mic — confirm `status` reports `available: true` after a
   restart.
3. `POST /api/v1/wake-word/trigger`, then speak a short phrase within
   `STT_UTTERANCE_SECONDS` — confirm `GET /api/v1/stt/status`'s
   `last_transcription` reflects it.
4. `PATCH /api/v1/settings {"stt_enabled": false}`, restart, confirm
   `status.enabled` is `false` and wake-word detection is unaffected
   (independent toggles).
5. Try `STT_MODEL=base.en` on a Pi 4/5 or desktop-class machine, confirm it
   still works — document any real timing observed back into this file if
   done (this session couldn't; no physical Pi was available).

## Acceptance Criteria

- Works on Raspberry Pi, Linux, Windows, and Docker — with or without the
  `voice` extra installed.
- No paid services required — on-device only, no cloud STT fallback exists
  or is planned for core functionality.
- Feature is independently testable without real audio hardware or a
  downloaded ML model.

## Definition of Done

- `backend/app/core/voice/{stt_events,stt_engine,stt_runtime}.py`.
- `backend/app/api/v1/endpoints/stt.py`, registered in `router.py`.
- `Settings.stt_model`/`stt_utterance_seconds` — documented in both
  `.env.example` files.
- `domain/settings.py`/`services/settings_service.py`: `stt_enabled`
  SettingKey.
- `api/v1/endpoints/settings.py` updated accordingly.
- `backend/pyproject.toml`: `pywhispercpp` added to the existing `voice`
  extras group (not a new group — same "local voice pipeline, opt-in"
  story as `011`).
- `docker-compose.yml`: `STT_MODEL`/`STT_UTTERANCE_SECONDS` passed through.
- `tests/fixtures/sample_utterance.wav` + `README.md`.
- Backend tests: `tests/unit/test_stt_events.py`, `test_stt_engine.py`,
  `test_stt_runtime.py`, `tests/integration/test_stt_api.py`, plus updates
  to `tests/integration/test_settings_api.py` for the new field. 93%
  backend statement coverage; the remaining gap is almost entirely
  `core/voice/{audio,engine,stt_engine}.py`'s real `sounddevice`/
  `openwakeword`/`pywhispercpp` integration lines (untestable without
  those optional dependencies installed — same class of deliberate gap
  `010`/`011` already established) plus a handful of defensive
  catch-blocks in `main.py`'s lifespan.
- `make lint && make test` green (backend + frontend; frontend untouched
  by this feature).

## Sources

- [ggml-org/whisper.cpp (GitHub)](https://github.com/ggml-org/whisper.cpp) — MIT license (code and models), model sizes/RAM table, ARM/Raspberry Pi support, 16-bit 16kHz WAV requirement.
- [absadiki/pywhispercpp (GitHub)](https://github.com/absadiki/pywhispercpp) — Python bindings, `pip install pywhispercpp`, automatic model download, `Model(name).transcribe(path)` API.
- [Real-time transcription on Raspberry Pi 4 — whisper.cpp Discussion #166](https://github.com/ggml-org/whisper.cpp/discussions/166) — tiny/base real-time-factor guidance on Pi 4/5.

## Git

Branch `feature/012-speech-to-text` (on top of `feature/011-wake-word`).
Conventional commits. CHANGELOG updated.
