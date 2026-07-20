# 011 Wake Word

## Status: Done

On-device wake-word detection via [OpenWakeWord](https://github.com/dscripka/openWakeWord)
is implemented as an **opt-in** capability
(`backend/app/core/voice/`): a `Plugin`-style orchestrator
(`WakeWordRuntime`) that always boots safely, degrades to a documented
push-to-talk fallback when the detection dependencies or a microphone
aren't available, and hands wake events off through a small pub/sub
contract the not-yet-built `012_STT` will subscribe to without touching
this code.

## Objective

Give the assistant a way to notice it's being addressed, without requiring
every deployment (including CI, Docker Desktop on Windows, and low-end Pi
hardware) to have a working microphone and ML runtime just to boot.

## Why detection is opt-in, not a default dependency

Two real constraints (see Sources at the bottom, gathered before writing
any code) rule out shipping this always-on by default:

1. **OpenWakeWord ships six pretrained models** (`alexa`, `hey_mycroft`,
   `hey_jarvis`, `hey_rhasspy`, plus two command phrases) — none of them is
   "Chintu," and training a real custom wake word needs an offline pipeline
   (~1hr on Colab, synthetic TTS training data), not something this backend
   can do at request time. So the *spoken/displayed* wake phrase (tied to
   the configurable assistant name — see Configuration below) is
   deliberately decoupled from *which acoustic model* is actually
   listening. `WAKE_WORD_MODEL` picks the model; the phrase text is
   cosmetic until real custom-wake-word training exists (tracked as future
   work, not part of this feature).
2. **Real audio capture and inference are genuinely hardware/OS-constrained**:
   `sounddevice` needs a native PortAudio library and a working input
   device — unavailable in CI, and unavailable through Docker Desktop on
   Windows/Mac (no host mic passthrough). `openwakeword`/`onnxruntime`
   aren't guaranteed prebuilt wheels on every Raspberry Pi architecture.
   Published/community numbers (not benchmarked on real hardware by this
   feature): a Raspberry Pi 3B+ is the practical minimum (one Pi 3 core can
   run 15-20 openWakeWord models in real time; a Pi 4 processes an 80ms
   audio chunk in under 5ms), a Pi Zero 2W has reported issues maxing a
   core, and RAM usage is roughly 50-100MB.

Given both, `openwakeword`/`onnxruntime`/`sounddevice` are a **`voice`
optional dependency group** (`pip install '.[voice]'`), not a base
dependency. The backend always boots and stays healthy without it — the
push-to-talk fallback (`POST /api/v1/wake-word/trigger`) is the
always-available path regardless of hardware.

## User Stories

- As an operator on capable hardware (Pi 3B+ or better, or any desktop
  Linux/Windows dev box with a mic), I install the `voice` extra and get
  real always-on wake-word listening.
- As an operator on constrained hardware, in Docker, or in CI, the backend
  still boots normally, `GET /api/v1/wake-word/status` tells me exactly
  why detection isn't active, and I can still trigger a "wake" via a plain
  REST call (push-to-talk) — nothing about the assistant is unusable.
- As the author of `012_STT`, I subscribe to `app.core.voice.events.wake_word_events`
  at my own startup and receive a `WakeWordEvent` (with a short pre-roll
  audio buffer for audio-driven detections) whenever a wake fires — I never
  need to import or modify anything in `app/core/voice/runtime.py`.

## Functional Requirements

1. `backend/app/core/voice/engine.py` wraps a single OpenWakeWord model
   (`WakeWordEngine`), lazily importing `openwakeword`/`onnxruntime` so
   importing the module never fails without them installed.
2. `backend/app/core/voice/audio.py` abstracts audio capture
   (`AudioSource` protocol + `MicrophoneAudioSource`, lazily importing
   `sounddevice`), 16-bit mono 16kHz PCM in 80ms frames (OpenWakeWord's
   required format).
3. `backend/app/core/voice/runtime.py`'s `WakeWordRuntime` orchestrates
   both: on `start(enabled=...)`, if disabled via settings or either
   dependency is unavailable, it degrades to a `reason`-carrying status
   instead of raising; otherwise it runs the listen loop as a background
   `asyncio.Task` (not APScheduler — that's for discrete/periodic jobs, not
   a continuous stream, confirmed against every other use in this repo).
4. `trigger_manual()` — the push-to-talk fallback — always works,
   regardless of `enabled`/`listening` state.
5. `backend/app/core/voice/events.py`'s `wake_word_events` (a module-level
   `WakeWordEventBus`, mirroring `core/scheduler.py`'s singleton pattern)
   is the STT handoff contract: `subscribe()`/`unsubscribe()`/`publish()`,
   isolating one listener's exception from the others (same fail-soft
   philosophy as `core/plugins.py`).
6. `GET /api/v1/wake-word/status` and `POST /api/v1/wake-word/trigger`
   (`backend/app/api/v1/endpoints/wake_word.py`).
7. `wake_word_enabled` is a fourth DB-managed setting (008_Settings
   pattern, default `True`), read once at startup — not hot-reloaded, same
   as every other startup-decided singleton in this app (scheduler,
   plugins).
8. The effective wake phrase (`GET /api/v1/config`, `GET /api/v1/settings`)
   is derived as `"Hey {app_name}"` from the *effective* (possibly
   DB-overridden) assistant name, unless an operator pins an exact phrase
   via the `WAKE_WORD` env var — closing a gap the `008_Settings`-era tests
   already flagged (renaming the assistant didn't used to change the wake
   phrase).

## Non-goals

No custom wake-word training/model management UI, no Docker audio-device
passthrough (documented as a platform limitation instead), no hot-reload of
`wake_word_enabled`, no frontend UI (a dashboard toggle is natural future
work once a design exists for it — not required by this feature), no STT
implementation itself (`012`) — only the event contract it will consume.

## Non-functional Requirements

- Cross-platform: the backend boots identically on Raspberry Pi, Linux,
  Windows, and Docker whether or not the `voice` extra is installed.
- No paid services required — OpenWakeWord and its models are free (model
  files are Apache-2.0 code / CC-BY-NC-SA-4.0 weights, downloaded once from
  GitHub releases on first real use, not bundled in the pip wheel — see
  Configuration).
- Independently testable without any real audio hardware or ML model (see
  Test Plan) — the `voice` extras are never installed in CI.
- Fails safely: a missing dependency, missing model files, missing mic, or
  a crash inside the listen loop degrades to a `reason`-carrying status,
  never crashes the backend (`main.py`'s lifespan wraps
  `start()`/`stop()` in the same log-and-continue pattern already used for
  plugin lifecycle hooks).

## Backend Design

New package `backend/app/core/voice/` (cross-cutting infra, same tier as
`core/plugins.py`/`core/scheduler.py`):

- `events.py` — `WakeWordEvent` (frozen dataclass: `model`, `confidence`,
  `detected_at`, `trigger: Literal["audio", "manual"]`, `audio: bytes | None`
  — a ~1s PCM16 pre-roll buffer for audio-driven detections, `None` for
  manual triggers) and `WakeWordEventBus`. **This is the `012_STT`
  integration point** — `from app.core.voice.events import wake_word_events;
  wake_word_events.subscribe(my_handler)` at STT's own startup is the
  entire integration surface; nothing here needs to change for `012`.
- `audio.py` — `AudioSource` protocol, `MicrophoneAudioSource`
  (`sounddevice`-backed), `AudioUnavailable`.
- `engine.py` — `WakeWordEngine` (`openwakeword`-backed, downloads model
  files via `openwakeword.utils.download_models()` on construction),
  `ModelUnavailable`.
- `runtime.py` — `WakeWordRuntime`: `engine`/`audio_source` are
  constructor-injectable, so tests drive it with small fakes; when
  omitted, `start()` constructs the real implementations (where import/
  device/download failures surface and are caught). `status` exposes
  `{enabled, listening, model, reason}`.

`main.py` wiring: `create_app()` constructs `WakeWordRuntime` (no DB
access — safe to do unconditionally, mirrors `register_plugins()` setting
`app.state.plugins` early). `lifespan()` resolves `wake_word_enabled`
**through whatever `get_db` dependency override is currently installed**
(`app.dependency_overrides.get(get_db, get_db)`, wrapped via
`contextlib.contextmanager`) rather than opening a raw session directly —
this was a deliberate fix during implementation: an earlier draft read the
DB straight from `SessionLocal()` inside `create_app()`, which would have
made every test silently touch the real `chintu.db`, since
`tests/conftest.py`'s DB override isn't installed until after `create_app()`
returns. Then `await wake_word_runtime.start(enabled=wake_word_enabled)`,
alongside the existing scheduler/plugin startup, each isolated in its own
try/except.

## Database

None. `wake_word_enabled` reuses the existing generic `settings` key/value
table (`008_Settings`) — no new model, no migration. The derived wake
phrase is computed on read, never persisted.

## APIs

- `GET /api/v1/wake-word/status` → `{enabled, listening, model, reason}`.
- `POST /api/v1/wake-word/trigger` → `{model, confidence, trigger, detected_at}`,
  the push-to-talk fallback — always available.
- `GET /api/v1/settings` / `PATCH /api/v1/settings` gain `wake_word`
  (read-only, derived) and `wake_word_enabled` (read/write).
- `GET /api/v1/config`'s `wake_word` field now reflects the DB-overridden
  app_name tie-in instead of a static env default.

## WebSocket Events

None — no WS transport exists anywhere in the app yet (see
[01_SYSTEM_ARCHITECTURE.md](../architecture/01_SYSTEM_ARCHITECTURE.md)'s
"Known gaps"). `012_STT` consumes wake events via the in-process
`wake_word_events` bus, not a client-facing WebSocket.

## Configuration

New env-only, deployment-level `Settings` fields
(`backend/app/core/config.py`), same tier as `plugins_dir`:

| Setting | Env var | Default |
|---|---|---|
| Acoustic model | `WAKE_WORD_MODEL` | `hey_jarvis` |
| Detection sensitivity | `WAKE_WORD_SENSITIVITY` | `0.5` (0.0-1.0) |
| Pre-roll buffer | `WAKE_WORD_PREROLL_SECONDS` | `1.0` |
| Input device | `VOICE_AUDIO_DEVICE` | `""` (system default) |

`WAKE_WORD` (`backend/app/core/config.py`) changed type from
`str = "Hey Chintu"` to `str | None = None` — an optional exact-phrase pin.
Left unset (the default), the *effective* phrase reported by `/config` and
`/settings` is derived as `f"Hey {app_name}"` by
`app/services/settings_service.py`, tracking a renamed assistant. Docker
Compose deliberately doesn't set `WAKE_WORD` at all (see the comment in
`docker-compose.yml`) since Compose can't distinguish "unset" from
"explicitly empty" once a key is listed under `environment:`, which would
have broken the "unset → derive" behavior.

`wake_word_enabled` is DB-managed (`008_Settings` pattern), not an env var
— see APIs above.

Model files aren't bundled in the `openwakeword` pip package; they're
downloaded once from GitHub releases on first real startup with the
`voice` extras installed (cached under `~/.openwakeword/models`). This
means the very first startup with detection enabled needs network access
once; fully air-gapped deployments would need to pre-stage the model files
manually — not automated by this feature.

## Test Plan

- **Unit** (`tests/unit/test_voice_events.py`, `tests/unit/test_voice_runtime.py`):
  event bus subscribe/unsubscribe/publish with listener-exception isolation;
  `WakeWordRuntime` driven by small fake `AudioSource`/engine
  implementations — enabled+available → listening, disabled via settings,
  a crashing listen loop recovering to a `reason`-carrying status without
  raising, pre-roll buffer attached to audio-driven events and absent for
  manual ones, manual trigger working in every state. One test
  (`test_missing_voice_dependencies_degrade_gracefully_instead_of_raising`)
  relies on the `voice` extras being genuinely absent in this venv to
  exercise the real `ImportError` fail-soft path — not a simulated one.
- **Integration** (`tests/integration/test_wake_word_api.py`): status/trigger
  endpoints through `TestClient`, including a real end-to-end check
  (`create_app()` → `lifespan()` → `SettingsService` → `WakeWordRuntime.start()`)
  that the wiring — not just `WakeWordRuntime` in isolation — degrades
  correctly; a subscribed listener receiving an event published through the
  real app lifespan; OpenAPI schema coverage. Existing settings/config
  integration tests updated for the new/changed response fields.
- **E2E**: not needed until `012_STT` gives wake events something real to
  drive.

## Manual QA

1. `make backend-dev` (no `voice` extras installed) — confirm the app
   boots normally, `GET /api/v1/wake-word/status` reports
   `listening: false` with a clear `reason`.
2. `POST /api/v1/wake-word/trigger` — confirm 200 and an event payload,
   with no microphone involved.
3. `pip install '.[voice]'` on a machine with a working mic (not required
   to be a Pi) — confirm `status` now reports `listening: true` after a
   restart, and speaking the configured model's phrase (e.g. "hey jarvis"
   with the default model) triggers a real detection observable in logs.
4. `PATCH /api/v1/settings {"wake_word_enabled": false}`, restart, confirm
   `status.enabled` is `false` and the `reason` mentions being disabled via
   settings — trigger still works.
5. Rename the assistant via `PATCH /api/v1/settings {"app_name": "..."}`,
   confirm `GET /api/v1/config`'s `wake_word` field updates to match.

## Acceptance Criteria

- Works on Raspberry Pi, Linux, Windows, and Docker — with or without the
  `voice` extra installed.
- No paid services required.
- Feature is independently testable without real audio hardware or a
  downloaded ML model.

## Definition of Done

- `backend/app/core/voice/{events,audio,engine,runtime}.py`.
- `backend/app/api/v1/endpoints/wake_word.py`, registered in `router.py`.
- `Settings.wake_word_model`/`wake_word_sensitivity`/`wake_word_preroll_seconds`/
  `voice_audio_device`, `Settings.wake_word` now optional — documented in
  both `.env.example` files.
- `domain/settings.py`/`services/settings_service.py`: `wake_word_enabled`
  SettingKey, derived `wake_word` on `EffectiveSettings`.
- `api/v1/endpoints/settings.py`/`config.py` updated accordingly.
- `backend/pyproject.toml`: `[project.optional-dependencies] voice`
  (openwakeword, onnxruntime, sounddevice, numpy) — deliberately not a base
  or `dev` dependency; `pytest-asyncio` added to `dev` (needed to test the
  new async runtime/event-bus code — no prior async test infrastructure
  existed in this repo).
- `docker-compose.yml`: new voice env vars passed through with real
  defaults; `WAKE_WORD` deliberately not listed (see Configuration).
- Backend tests: `tests/unit/test_voice_events.py`,
  `tests/unit/test_voice_runtime.py`, `tests/integration/test_wake_word_api.py`,
  plus updates to `tests/unit/test_config.py`,
  `tests/integration/test_settings_api.py`, and
  `tests/integration/test_config_api.py` for the changed/new fields. 94%
  backend statement coverage; the remaining gap is almost entirely
  `core/voice/audio.py`/`engine.py`'s real `sounddevice`/`openwakeword`
  integration lines (untestable without those optional dependencies
  installed — same class of deliberate gap as `010`'s `Plugin` base-class
  no-ops) plus two defensive catch-blocks in `main.py`'s lifespan around
  calls that `WakeWordRuntime` itself already guarantees won't raise.
- `make lint && make test` green (backend + frontend; frontend untouched by
  this feature).

## Sources

- [dscripka/openWakeWord (GitHub)](https://github.com/dscripka/openWakeWord) — pretrained model list, audio format (16-bit 16kHz PCM, 80ms frames), Apache-2.0 code / CC-BY-NC-SA-4.0 model license, "15-20 models on one Pi 3 core," custom-training pipeline.
- [Wake Word Detection on Raspberry Pi — Outspoken](https://outspoken.cloud/blog/raspberry-pi-wake-word-detection) — Pi 3B+ minimum, <5ms per 80ms chunk on Pi 4.
- [rhasspy/wyoming-openwakeword#47](https://github.com/rhasspy/wyoming-openwakeword/issues/47) / [#30](https://github.com/rhasspy/wyoming-openwakeword/issues/30) — Pi Zero 2W CPU issues.
- [Installation and Setup — DeepWiki](https://deepwiki.com/dscripka/openWakeWord/2-installation-and-setup) — platform-specific deps, `download_models()`, model cache location.

## Git

Branch `feature/011-wake-word`. Conventional commits. CHANGELOG updated.
