# 07 Deployment

Status: **implemented** for Docker Compose (single-host); native process deployment is
supported the same way as local dev (see [docs/guides/Setup_Guide.md](../guides/Setup_Guide.md)).

## Docker Compose (recommended)

```bash
cp .env.example .env
docker compose up --build
```

This builds and runs two services (`docker-compose.yml`):

| Service | Image base | Exposes | Notes |
|---|---|---|---|
| `backend` | `python:3.12-slim` | `${BACKEND_PORT:-8000}` → 8000 | Runs as non-root user `chintu`; SQLite data and logs persisted in named volumes (`backend-data`, `backend-logs`); `CMD` runs `alembic upgrade head` before starting uvicorn — see [03_DATABASE_DESIGN.md](03_DATABASE_DESIGN.md) |
| `frontend-dashboard` | `node:22-alpine` (build) → `nginx:alpine` (runtime) | `${FRONTEND_PORT:-5173}` → 80 | Multi-stage: Vite build, then static files served by Nginx; waits for `backend`'s healthcheck before starting |

All three base images (`python:3.12-slim`, `node:22-alpine`, `nginx:alpine`)
are multi-arch, so the same compose file runs unmodified on Linux, Windows
(Docker Desktop), and Raspberry Pi (arm64/armv7).

### Configuration

Every backend setting is passed through from the repo-root `.env` (loaded
automatically by `docker compose`) — see `.env.example` for the full list
(`APP_NAME`, `APP_ENV`, `DEBUG`, `LOG_LEVEL`, `CORS_ORIGINS`, port overrides).
`VITE_API_BASE_URL` is a **build-time** argument (Vite inlines `VITE_*` vars
at build, not at container start), so it must point at wherever the backend
will be reachable *from the browser* — not from inside the Docker network.

If you change `BACKEND_PORT` or `FRONTEND_PORT`, also update
`VITE_API_BASE_URL` / `CORS_ORIGINS` to match — they aren't derived from the
port variables automatically.

### Image build details worth knowing

- **`backend/Dockerfile`** installs dependencies in a separate layer from
  the application source (against a throwaway placeholder package), so
  editing `app/` code doesn't force a full dependency reinstall on rebuild —
  only `pyproject.toml` changes do.
- **`.dockerignore`** exists for both services — without it, the host's
  `node_modules`/`.venv` would be sent into the build context.
- Both services have a Compose `healthcheck`; `frontend-dashboard` won't
  start serving until `backend` reports healthy
  (`depends_on: condition: service_healthy`).
- Both services have fixed resource limits (`mem_limit: 512m`/`128m`,
  `cpus: 1.0`/`0.5`) — conservative for a Raspberry Pi, edit directly in
  `docker-compose.yml` if your device needs different values. Not templated
  via `.env`: Docker Compose 2.2.x mis-parses a memory-unit string like
  `"512m"` when it comes through `${VAR:-default}` substitution instead of a
  YAML literal. Memory limits are confirmed enforced (`docker inspect`); CPU
  limits depend on the Docker Engine version (not enforced on Engine 20.10 in
  testing, harmless no-op there — should work on newer engines).

### Common operations

```bash
docker compose ps                       # check health status
docker compose logs -f backend          # tail backend logs
docker compose build --no-cache backend # force a full rebuild
docker compose down                     # stop + remove containers/network (keeps volumes)
docker compose down -v                  # also remove the named volumes (destroys SQLite data)
```

## Native (non-Docker) deployment

Same commands as local dev — apply migrations first (`alembic upgrade
head`), then run the backend with a production ASGI process (`uvicorn
app.main:app --host 0.0.0.0 --port 8000`, no `--reload`) behind whatever
reverse proxy/process manager the host provides, and serve
the frontend's `npm run build` output (`frontend-dashboard/dist/`) via any
static file server. Set `DEBUG=false` and `APP_ENV=production` in
`backend/.env` — the code defaults to `debug=False` already, so this only
matters if you're relying on a `.env` file at all; see
[06_SECURITY.md](06_SECURITY.md).

## Voice / Wake Word & Speech-to-Text

`011_Wake_Word` and `012_Speech_To_Text` (`backend/app/core/voice/`)
integrate [OpenWakeWord](https://github.com/dscripka/openWakeWord) and
[whisper.cpp](https://github.com/ggml-org/whisper.cpp) (via `pywhispercpp`)
as a single **opt-in** capability — `pip install '.[voice]'`
(`openwakeword`, `onnxruntime`, `sounddevice`, `numpy`, `pywhispercpp`; see
`backend/pyproject.toml`), never installed by default or in CI. Without it,
the backend still boots and serves everything else;
`GET /api/v1/wake-word/status` / `GET /api/v1/stt/status` report why
detection/transcription are inactive, and `POST /api/v1/wake-word/trigger`
(push-to-talk) always works regardless — it just won't produce a
transcription if STT isn't available.

**Resource footprint** — published/community numbers, not benchmarked on
real hardware by this feature (no physical device was available; see
Sources below):

| Device | Guidance |
|---|---|
| Raspberry Pi 3B+ | Practical minimum. One Pi 3 core can run 15-20 openWakeWord models simultaneously in real time. |
| Raspberry Pi 4/5 | Recommended — an 80ms audio chunk processes in under 5ms, leaving headroom for the rest of the assistant. |
| Raspberry Pi Zero 2W | Reported issues maxing a CPU core running `openwakeword` (see linked GitHub issues) — install the `voice` extra here only after testing on your actual unit, and use `WAKE_WORD_ENABLED=false` (via `PATCH /api/v1/settings`) or skip the extra entirely if it doesn't keep up. |
| RAM | Roughly 50-100MB including the Python process. |

**Model files aren't bundled** in the pip package — `openwakeword`
downloads them from GitHub releases on first real startup
(`openwakeword.utils.download_models()`, cached under
`~/.openwakeword/models`). The first startup with detection enabled needs
network access once; a fully air-gapped deployment needs to pre-stage the
model files manually.

### Speech-to-Text

`012_Speech_To_Text` reuses the same audio format/capture code and the
same "opt-in, fails soft" philosophy — see
[docs/features/012_Speech_To_Text.md](../features/012_Speech_To_Text.md)
for the full design rationale, including why STT doesn't require any
changes to `011`'s wake-word code. Model sizing is the concrete Pi
trade-off (source: whisper.cpp's own README, not measured on physical
hardware by this feature):

| Model | Disk | RAM | Fits the 512m backend `mem_limit` below? |
|---|---|---|---|
| tiny(.en) | 75 MiB | ~273 MB | Yes — **the default** (`STT_MODEL=tiny.en`) |
| base(.en) | 142 MiB | ~388 MB | Tight — little headroom for the rest of the app |
| small | 466 MiB | ~852 MB | No — exceeds the limit outright |
| medium/large | 1.5-2.9 GiB | 2.1-3.9 GB | No — desktop/server hardware only |

On a Raspberry Pi 4, `tiny` runs comfortably faster than real-time; `base`
runs around real-time using 4 threads. Raise `docker-compose.yml`'s
backend `mem_limit` (see below) before trying `base`/`small` — the default
512m only has headroom for `tiny`. Whisper.cpp/its models are **MIT
licensed** (unlike OpenWakeWord's CC-BY-NC-SA-4.0 models above) — no
non-commercial restriction. Model files are likewise downloaded once on
first real use, not bundled in the pip package — same one-time-network
caveat as wake-word's models.

**Docker**: the default image does **not** install the `voice` extra or
`libportaudio2`, and `docker-compose.yml` doesn't bind-mount `/dev/snd` —
real microphone capture from inside a container (needed by both wake-word
detection and STT's utterance capture) needs a Linux host with `/dev/snd`
passed through and PortAudio installed in a custom image, and does **not**
work through Docker Desktop on Windows/Mac at all (no host mic
passthrough). For always-on listening, run the backend natively on the
Pi/Linux box rather than in Docker; push-to-talk via the API is the
portable fallback everywhere, including Docker (though without a working
mic, STT still can't produce a transcription from it).

**Wake phrase vs. acoustic model**: OpenWakeWord ships six pretrained
models (`alexa`, `hey_mycroft`, `hey_jarvis`, `hey_rhasspy`, plus two
command phrases) — none matches an arbitrary assistant name. `WAKE_WORD_MODEL`
picks which model actually listens; the *displayed/spoken* phrase
(`GET /api/v1/config`'s `wake_word`, derived from the assistant name) is
cosmetic until real custom-wake-word training exists. See
[docs/features/011_Wake_Word.md](../features/011_Wake_Word.md) for the
full design rationale.

### Sources

- [dscripka/openWakeWord (GitHub)](https://github.com/dscripka/openWakeWord)
- [Wake Word Detection on Raspberry Pi — Outspoken](https://outspoken.cloud/blog/raspberry-pi-wake-word-detection)
- [rhasspy/wyoming-openwakeword#47](https://github.com/rhasspy/wyoming-openwakeword/issues/47), [#30](https://github.com/rhasspy/wyoming-openwakeword/issues/30)
- [Installation and Setup — DeepWiki](https://deepwiki.com/dscripka/openWakeWord/2-installation-and-setup)
- [ggml-org/whisper.cpp (GitHub)](https://github.com/ggml-org/whisper.cpp)
- [absadiki/pywhispercpp (GitHub)](https://github.com/absadiki/pywhispercpp)
- [Real-time transcription on Raspberry Pi 4 — whisper.cpp Discussion #166](https://github.com/ggml-org/whisper.cpp/discussions/166)

## Not yet implemented

- No CI/CD pipeline publishes images or deploys anywhere — `.github/workflows/ci.yml`
  only runs lint/type-check/tests on push and PR.
- No orchestration beyond Compose (no Kubernetes manifests, no multi-host setup).
- No backup/restore tooling for the SQLite volume (tracked as a future feature,
  see `docs/features/036_Backup_Restore.md`).
