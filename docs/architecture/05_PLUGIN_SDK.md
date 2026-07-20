# 05 Plugin SDK

Status: **Implemented** (`010_Plugin_Framework`, see
[docs/features/010_Plugin_Framework.md](../features/010_Plugin_Framework.md)
for the feature-level spec and Definition of Done). This contract is now
real code in `backend/app/core/plugins.py`; every design decision below
reflects what's actually built, not a plan. `plugins/` itself is still
empty — no real plugin exists yet — this is the extension point
`041_Home_Assistant`/`042_Device_Control` will use once they start.

## Why, and why now

Today, adding a plugin would mean hand-editing `backend/app/api/v1/router.py`
directly — there's no seam between core and plugin code. The two features
that will actually consume this (`041_Home_Assistant`, `042_Device_Control`,
both Phase 8) are far off, but the extension point has to exist *before*
either can start, so it's designed now while nothing depends on it yet.

## Design goals

- A plugin is a folder dropped into a directory — no separate install/build
  step, no package registry, consistent with "no paid services required."
- One broken or incompatible plugin must not stop the assistant from
  starting, or take down any other plugin.
- Fits the conventions already established in `backend/app/core/config.py`
  (env-driven `Settings`) and `main.py`'s `lifespan()` (start/stop hooks
  alongside the existing scheduler) rather than inventing new patterns.
- Identical behavior native and in Docker.

## Non-goals (explicitly deferred — YAGNI)

- No plugin marketplace/registry or remote distribution.
- No sandboxing or permission system — see Trust model below.
- No hot-reload; picking up a new/changed plugin requires an app restart.
- No out-of-process/subprocess isolation.
- No plugin-to-plugin dependency graph or communication.
- No WebSocket registration hook — no WS transport exists anywhere in the
  app yet (see [01_SYSTEM_ARCHITECTURE.md](01_SYSTEM_ARCHITECTURE.md)'s
  "Known gaps"); add this only when a concrete plugin needs push updates.
- No frontend/UI extension point — a plugin can serve a REST API; a
  dashboard surface for plugin-contributed UI is future scope (likely
  `048_Admin_Panel`), not `010`.

Revisit any of these only when a real, concrete feature needs them — not
speculatively.

## Trust model

Digital Chintu is self-hosted by a single operator, and nothing under
`/api/v1` has authentication yet (see [06_SECURITY.md](06_SECURITY.md)). A
plugin runs in-process, as the same Python interpreter, with the same
filesystem and network access as core code — equivalent trust to core code,
not a security boundary. The only "gate" is filesystem placement into
`PLUGINS_DIR`, which already requires the same access as editing `.env`.
This is deliberate, not an oversight: revisit only if third-party/untrusted
plugin distribution ever becomes a goal, which is not currently on the
roadmap.

## Plugin contract

```python
# backend/app/core/plugins.py

class PluginMetadata(BaseModel):
    slug: str              # URL-safe, unique, kebab-case -> /api/v1/plugins/{slug}/...
    name: str               # display name, for a future admin/settings UI
    version: str            # plugin author's own version string
    min_core_version: str   # lowest digital-chintu-backend version this plugin supports

class Plugin(ABC):
    metadata: PluginMetadata

    def router(self) -> APIRouter | None:
        """Routes this plugin contributes, or None if it has no HTTP API."""

    async def on_startup(self) -> None:
        """Optional. Called once during app lifespan startup, after discovery."""

    async def on_shutdown(self) -> None:
        """Optional. Called once during app lifespan shutdown."""
```

`on_startup`/`on_shutdown` default to no-ops, so a minimal plugin only needs
`metadata` and `router()`.

## Discovery mechanism

- A new `plugins_dir` field on `Settings` (same env-driven pattern as every
  other setting in `core/config.py`), env var `PLUGINS_DIR`. Defaults to the
  repo-root `plugins/` directory in native dev.
- Every immediate subdirectory of `PLUGINS_DIR` containing a `plugin.py`
  module that exposes a module-level `plugin: Plugin` instance is a
  candidate — convention over configuration, no packaging step.
- **Rejected alternative**: `importlib.metadata` entry points (the standard
  pip-installable-plugin pattern). Deferred — it adds a packaging/publishing
  step disproportionate to a single self-hosted box; reconsider only if
  plugins are ever meant to be distributed outside this monorepo.

## Registration

- Runs inside `create_app()`, after `api_router` is built and included.
- For each enabled, valid plugin: `app.include_router(plugin.router(),
  prefix=f"{settings.api_v1_prefix}/plugins/{slug}", tags=[slug])` when
  `router()` is not `None`.
- Discovered instances are stored on `app.state.plugins: list[Plugin]`, used
  by the lifespan hooks below and by a `GET /api/v1/plugins` introspection
  endpoint (part of `010`'s own deliverables).
- `main.py`'s existing `lifespan()` is extended to call every plugin's
  `on_startup()`/`on_shutdown()` alongside the existing
  `scheduler.start()`/`scheduler.shutdown()` calls — same lifecycle-managed
  resource pattern already in place, not a new one.

## Validation and failure handling

**Fail-fast** (raise; app refuses to start) — these indicate a broken
deployment configuration, the same philosophy as `Settings`' own
`model_validator`s:
- Duplicate slugs across discovered plugins.
- A slug that isn't a valid URL path segment.
- Missing required metadata fields.

**Fail-soft** (log and skip that one plugin; the app still starts) — these
are a single plugin's problem, not the deployment's:
- `plugin.py` raising on import.
- `on_startup()` raising.
- `min_core_version` incompatible with the running core version.

The asymmetry is deliberate: this runs unattended on a Raspberry Pi with no
ops team watching for a crash loop, so the assistant coming up with N-1
working plugins beats it refusing to start over one bad one — but a
misconfigured deployment (duplicate slugs) should be loud and immediate.

## Enabling / disabling

- New `enabled_plugins` setting, env var `ENABLED_PLUGINS`: comma-separated
  slugs, same list-parsing pattern as `cors_origins_list`.
- Unlike `CORS_ORIGINS` (deny-by-default empty list), an empty/unset
  `ENABLED_PLUGINS` means **enable everything discovered**. This isn't an
  inconsistency: placing a plugin's files into `PLUGINS_DIR` already
  requires filesystem/deployment access (see Trust model), so auto-enabling
  on discovery doesn't cross a new trust boundary the way an open CORS
  origin would. `ENABLED_PLUGINS` exists so an operator can stage a plugin
  on disk without activating it, or temporarily disable one without
  deleting its files.

## Cross-platform / Docker

- Native dev, Linux, Raspberry Pi, Windows: `PLUGINS_DIR` defaults to the
  repo-root `plugins/` — no configuration needed.
- Docker: the backend's build context is `./backend` only, so `plugins/`
  isn't baked into the image. `docker-compose.yml` bind-mounts it instead —
  `./plugins:/app/plugins:ro` — alongside the existing `backend-data`/
  `backend-logs` volumes, with `PLUGINS_DIR=/app/plugins` set in the
  backend service's environment, mirroring how `DATABASE_URL` is already
  overridden per-environment. Net effect: dropping a plugin into the host's
  `plugins/` and restarting the container picks it up without an image
  rebuild. The mount is read-only — the container only needs to read plugin
  code, never write to it.

## Versioning / compatibility

`min_core_version` is compared against the running core's own version
(`backend/pyproject.toml`'s `[project] version`, read via
`importlib.metadata.version("digital-chintu-backend")` rather than
duplicating the string) using plain tuple comparison — no new semver
dependency, per [Coding_Standards.md](../guides/Coding_Standards.md)'s "don't
add abstractions until needed." An incompatible plugin fails soft (logged,
skipped) per the Validation section above.

## What's explicitly out of scope for `010`

See Non-goals above. In particular: no persistence helpers — a plugin
needing its own tables follows whatever SQLAlchemy/Alembic path core
features use once the first model is introduced (Phase 4 backlog item), not
a bespoke plugin-only mechanism.

## Consumers

`041_Home_Assistant` and `042_Device_Control` (Phase 8) are the first two
features expected to implement this contract for real. Neither has started;
this document exists so the extension point is ready when they do.
