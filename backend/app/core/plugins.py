"""Plugin discovery, contract, and registration — the extension point for
optional features that add their own API surface without editing
api/v1/router.py directly. See docs/architecture/05_PLUGIN_SDK.md."""

import importlib.metadata
import importlib.util
import logging
import re
import sys
from abc import ABC
from dataclasses import dataclass
from pathlib import Path

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel, field_validator

logger = logging.getLogger(__name__)

_SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_CORE_PACKAGE = "digital-chintu-backend"


class PluginMetadata(BaseModel):
    slug: str
    name: str
    version: str
    min_core_version: str

    @field_validator("slug")
    @classmethod
    def _slug_is_url_safe(cls, value: str) -> str:
        if not _SLUG_RE.fullmatch(value):
            raise ValueError(
                "slug must be lowercase alphanumeric with hyphens, e.g. 'home-assistant'"
            )
        return value


class Plugin(ABC):
    """Base class for a plugin. `metadata` is required; everything else is
    optional and defaults to a no-op, so a minimal plugin only needs
    metadata and (usually) a router."""

    metadata: PluginMetadata

    def router(self) -> APIRouter | None:
        return None

    async def on_startup(self) -> None:
        return None

    async def on_shutdown(self) -> None:
        return None


class PluginLoadError(Exception):
    """A deployment-configuration error (e.g. duplicate slugs) that should
    stop the app from starting, as opposed to a single plugin failing to
    load, which is logged and skipped instead."""


@dataclass(frozen=True)
class DiscoveredPlugin:
    plugin: Plugin
    enabled: bool
    source: Path


def _parse_version(raw: str) -> tuple[int, ...]:
    """Lenient major.minor.patch parse — good enough for a floor comparison
    without pulling in a semver dependency (see Coding_Standards.md's "don't
    add abstractions until needed"). Non-numeric segments parse as 0."""
    parts = []
    for segment in raw.split(".")[:3]:
        digits = "".join(ch for ch in segment if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts)


def _core_version() -> str:
    return importlib.metadata.version(_CORE_PACKAGE)


def _load_plugin_module(dir_name: str, plugin_file: Path) -> Plugin | None:
    module_name = f"_digital_chintu_plugin_{dir_name}"
    try:
        spec = importlib.util.spec_from_file_location(module_name, plugin_file)
        if spec is None or spec.loader is None:
            raise ImportError(f"could not load a module spec for {plugin_file}")
        module = importlib.util.module_from_spec(spec)
        # Registered before exec so the plugin's own module-level code (and
        # anything inspecting sys.modules afterward) sees a normal import,
        # not a detached module object.
        sys.modules[module_name] = module
        try:
            spec.loader.exec_module(module)
        except Exception:
            del sys.modules[module_name]
            raise
        plugin = getattr(module, "plugin", None)
        if not isinstance(plugin, Plugin):
            raise TypeError(f"{plugin_file} must define a module-level 'plugin: Plugin' instance")
    except Exception:
        logger.exception("Failed to load plugin from %s — skipping it", plugin_file)
        return None
    return plugin


def discover_plugins(
    plugins_dir: Path, enabled_plugins: set[str] | None = None
) -> list[DiscoveredPlugin]:
    """Scan `plugins_dir` for `<name>/plugin.py` modules exposing a
    module-level `plugin: Plugin` instance.

    A duplicate slug across two discovered plugins raises `PluginLoadError`
    (deployment misconfiguration — the app should fail to start). A single
    plugin failing to import is logged and skipped. A plugin whose
    `min_core_version` exceeds the running core, or whose slug isn't in
    `enabled_plugins` (when that allow-list is non-`None`), is still
    returned but marked `enabled=False` — see
    docs/architecture/05_PLUGIN_SDK.md's "Enabling / disabling".
    """
    if not plugins_dir.is_dir():
        return []

    core_version = _parse_version(_core_version())
    discovered: list[DiscoveredPlugin] = []
    seen_slugs: dict[str, Path] = {}

    for entry in sorted(plugins_dir.iterdir()):
        if not entry.is_dir():
            continue
        plugin_file = entry / "plugin.py"
        if not plugin_file.is_file():
            continue

        plugin = _load_plugin_module(entry.name, plugin_file)
        if plugin is None:
            continue

        slug = plugin.metadata.slug
        if slug in seen_slugs:
            raise PluginLoadError(
                f"duplicate plugin slug '{slug}' ({seen_slugs[slug]} and {entry})"
            )
        seen_slugs[slug] = entry

        version_compatible = _parse_version(plugin.metadata.min_core_version) <= core_version
        if not version_compatible:
            logger.warning(
                "Plugin '%s' requires core >= %s, running %s — discovered but disabled",
                slug,
                plugin.metadata.min_core_version,
                _core_version(),
            )

        allow_listed = enabled_plugins is None or slug in enabled_plugins
        if not allow_listed:
            logger.info("Plugin '%s' is not in ENABLED_PLUGINS — discovered but disabled", slug)

        discovered.append(
            DiscoveredPlugin(
                plugin=plugin, enabled=version_compatible and allow_listed, source=entry
            )
        )

    return discovered


def register_plugins(app: FastAPI, discovered: list[DiscoveredPlugin], api_prefix: str) -> None:
    """Store `discovered` on `app.state.plugins` (all of it, enabled or not —
    used by `GET /api/v1/plugins` and the lifespan hooks) and mount each
    *enabled* plugin's router, if it has one, at
    `{api_prefix}/plugins/{slug}`."""
    app.state.plugins = discovered
    for item in discovered:
        if not item.enabled:
            continue
        router = item.plugin.router()
        if router is not None:
            app.include_router(
                router,
                prefix=f"{api_prefix}/plugins/{item.plugin.metadata.slug}",
                tags=[item.plugin.metadata.slug],
            )
