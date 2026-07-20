# 010 Plugin Framework

## Status: Done

The extension point designed in
[docs/architecture/05_PLUGIN_SDK.md](../architecture/05_PLUGIN_SDK.md) is
implemented: `backend/app/core/plugins.py` (`Plugin`, `PluginMetadata`,
`discover_plugins()`, `register_plugins()`), new `PLUGINS_DIR`/
`ENABLED_PLUGINS` settings, lifespan-integrated startup/shutdown hooks in
`main.py`, `GET /api/v1/plugins`, and a `docker-compose.yml` bind mount for
`plugins/`. `plugins/hello-plugin` ships as a trivial reference plugin
proving the mechanism end-to-end (one `GET /hello` route, no real
behavior) — this is the framework `041_Home_Assistant` and
`042_Device_Control` will build on for a real integration, both still not
started.

## Objective

Give plugins a real extension point instead of hand-editing
`backend/app/api/v1/router.py`: a discovery mechanism, a plugin interface,
and a dynamic router-registration hook in `create_app()`. See
[05_PLUGIN_SDK.md](../architecture/05_PLUGIN_SDK.md) for the full design;
this doc covers the feature-level requirements and test/QA plan.

## Claude Code Instructions

You are the lead architect and senior full-stack engineer. Read existing
architecture before coding. Never break previous features.

## User Stories

- As a self-hosted operator, I can drop a plugin's folder into `plugins/`
  and have its API surface come up automatically after a restart, without
  editing core router code.
- As a plugin author, I implement one small interface (metadata + optional
  router + optional startup/shutdown hooks) and don't need to know how core
  wires routers together.
- As the platform maintainer, one broken or version-incompatible plugin
  can't prevent the rest of the assistant — or any other plugin — from
  starting.

## Functional Requirements

1. The backend discovers plugins from a configurable directory
   (`PLUGINS_DIR`) at startup.
2. Each plugin declares metadata (slug, name, version, `min_core_version`)
   and optionally contributes an `APIRouter`, mounted at
   `/api/v1/plugins/{slug}`.
3. Plugins can hook into app startup/shutdown for setup/teardown (e.g.
   opening a connection to a Home Assistant instance).
4. An operator can restrict which discovered plugins are active via
   `ENABLED_PLUGINS` without removing files from disk.
5. Discovery/registration failures are isolated per-plugin and logged,
   degrading gracefully — except configuration errors (duplicate slugs,
   malformed metadata), which fail the app at startup since those indicate a
   broken deployment, not a broken plugin.
6. `GET /api/v1/plugins` lists discovered plugins (slug, name, version,
   enabled state) for future Settings/Admin UI consumption.

## Non-goals

No sandboxing, no plugin marketplace, no hot-reload, no WebSocket hook, no
plugin UI surface, no inter-plugin dependencies — see
[05_PLUGIN_SDK.md](../architecture/05_PLUGIN_SDK.md)'s "Non-goals" for the
full rationale on each.

## Non-functional Requirements

- Cross-platform: works unmodified on Raspberry Pi, Linux, Windows, and
  Docker (Docker needs a bind mount for `plugins/` — see
  [05_PLUGIN_SDK.md](../architecture/05_PLUGIN_SDK.md)'s "Cross-platform /
  Docker").
- No paid services required.
- Independently testable: the framework must work with zero real plugins
  installed (the default/common case until `041`/`042` exist) as well as
  with a fixture plugin.

## Backend Design

New module `backend/app/core/plugins.py` (`Plugin` ABC, `PluginMetadata`,
`discover_plugins()`, `register_plugins()`) — see
[05_PLUGIN_SDK.md](../architecture/05_PLUGIN_SDK.md) for the interface. New
`Settings` fields: `plugins_dir`, `enabled_plugins`. `main.py`'s
`create_app()` calls `register_plugins()` after including `api_router`;
`lifespan()` is extended to call each plugin's `on_startup()`/
`on_shutdown()` alongside the existing scheduler start/stop.

## Database

None. The framework itself is stateless — no plugin registry table.
Individual plugins that need persistence follow the same SQLAlchemy/Alembic
path core features will use once the first model is introduced (Phase 4
backlog item); out of scope here.

## APIs

`GET /api/v1/plugins` — list of `{slug, name, version, enabled}`. Read-only,
the same introspection role `GET /api/v1/config` already plays — runtime
mutation (enabling/disabling without an env var + restart) is a Settings
feature (`008`) concern, not this one.

## WebSocket Events

None. No WebSocket transport exists anywhere in the app yet (see
[01_SYSTEM_ARCHITECTURE.md](../architecture/01_SYSTEM_ARCHITECTURE.md)'s
"Known gaps"); add a plugin WS hook only when a concrete plugin needs push
updates.

## Configuration

New `Settings` fields: `PLUGINS_DIR` (default resolves to the repo-root
`plugins/`), `ENABLED_PLUGINS` (comma-separated slugs; empty means all
discovered plugins are enabled — see
[05_PLUGIN_SDK.md](../architecture/05_PLUGIN_SDK.md)'s "Enabling /
disabling" for why that default differs from `CORS_ORIGINS`'s
deny-by-default).

## Test Plan

- **Unit**: `discover_plugins()` against a temp-directory fixture — valid
  plugin, missing `plugin.py`, a `plugin.py` that raises on import,
  duplicate slugs, invalid metadata.
- **Integration**: `TestClient(create_app())` with `PLUGINS_DIR`
  monkeypatched to a fixture directory, asserting a fixture plugin's router
  is mounted at the right prefix and `GET /api/v1/plugins` reflects it; a
  second case with one intentionally broken plugin asserting the app still
  starts and serves everything else.
- **E2E**: not needed until a real plugin exists.

## Manual QA

1. Run `make backend-dev`, confirm the checked-in `plugins/hello-plugin`
   reference plugin is picked up.
2. Hit its mounted route directly: `GET /api/v1/plugins/hello-plugin/hello`.
3. Confirm `GET /api/v1/plugins` lists it (`enabled: true`).
4. Remove it (or point `PLUGINS_DIR` elsewhere), confirm a clean restart
   with an empty `plugins/` still works — the common case until a real
   integration plugin (`041`/`042`) exists.
5. Repeat steps 1-4 against `docker compose up --build`.

## Acceptance Criteria

- Works on Raspberry Pi, Linux, Windows and Docker.
- No paid services required.
- Feature is independently testable, and does not require an actual plugin
  to exist for the framework itself to be tested.

## Definition of Done

- `backend/app/core/plugins.py`: `Plugin` ABC, `PluginMetadata`,
  `discover_plugins()`, `register_plugins()`, `PluginLoadError`.
- `Settings.plugins_dir` / `Settings.enabled_plugins` (+
  `enabled_plugins_set` property), documented in both `.env.example` files.
- `main.py`: `create_app()` calls `register_plugins()`; `lifespan()` calls
  every enabled plugin's `on_startup()`/`on_shutdown()`, each isolated by
  its own `try`/`except` so one plugin can't take down the app or another
  plugin.
- `GET /api/v1/plugins` (`backend/app/api/v1/endpoints/plugins.py`).
- `docker-compose.yml`: `./plugins:/app/plugins:ro` bind mount,
  `PLUGINS_DIR`/`ENABLED_PLUGINS` env vars.
- `plugins/hello-plugin/plugin.py`: trivial reference plugin (metadata +
  one `GET /hello` route) proving the mechanism end-to-end on disk.
- Backend tests: `tests/unit/test_plugins.py` (discovery, duplicate-slug
  failure, broken/invalid plugins skipped, version and allow-list gating,
  router registration) and `tests/integration/test_plugins_api.py`
  (populated listing against the real `plugins/hello-plugin` reference
  plugin, mounted routing, disabled-plugin gating, a broken plugin not
  blocking startup, and lifespan startup/shutdown hooks including failure
  isolation). 98% backend statement coverage; the remaining gap is the
  `Plugin` base class's no-op default methods and one defensive
  `importlib` guard, the same class of deliberate gap as
  `db/base.py`'s `DeclarativeBase` (see
  [08_TESTING_STRATEGY.md](../architecture/08_TESTING_STRATEGY.md)).
- `make lint && make test` green (backend + frontend; frontend untouched by
  this feature).

## Git

Create feature branch. Use conventional commit. Update CHANGELOG. Push to
GitHub after verification.
