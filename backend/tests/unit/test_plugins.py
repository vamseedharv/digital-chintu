from pathlib import Path

import pytest
from fastapi import FastAPI

from app.core.plugins import PluginLoadError, discover_plugins, register_plugins

_VALID_PLUGIN_SOURCE = """
from fastapi import APIRouter
from app.core.plugins import Plugin, PluginMetadata

router = APIRouter()


@router.get("/ping")
def ping() -> dict[str, str]:
    return {{"pong": "{slug}"}}


class _TestPlugin(Plugin):
    metadata = PluginMetadata(
        slug="{slug}", name="{name}", version="1.0.0", min_core_version="{min_core_version}"
    )

    def router(self):
        return router


plugin = _TestPlugin()
"""


def _write_plugin(
    plugins_dir: Path,
    dir_name: str,
    *,
    slug: str | None = None,
    name: str = "Test Plugin",
    min_core_version: str = "0.0.1",
    source: str | None = None,
) -> Path:
    plugin_dir = plugins_dir / dir_name
    plugin_dir.mkdir(parents=True)
    contents = (
        source
        if source is not None
        else _VALID_PLUGIN_SOURCE.format(
            slug=slug or dir_name, name=name, min_core_version=min_core_version
        )
    )
    (plugin_dir / "plugin.py").write_text(contents)
    return plugin_dir


def test_discover_plugins_returns_empty_list_when_directory_is_missing(tmp_path: Path) -> None:
    assert discover_plugins(tmp_path / "does-not-exist") == []


def test_discover_plugins_finds_a_valid_plugin(tmp_path: Path) -> None:
    _write_plugin(tmp_path, "example-plugin")

    discovered = discover_plugins(tmp_path)

    assert len(discovered) == 1
    assert discovered[0].plugin.metadata.slug == "example-plugin"
    assert discovered[0].enabled is True


def test_discover_plugins_ignores_a_directory_without_plugin_py(tmp_path: Path) -> None:
    (tmp_path / "not-a-plugin").mkdir()
    (tmp_path / "not-a-plugin" / "README.md").write_text("nothing to see here")

    assert discover_plugins(tmp_path) == []


def test_discover_plugins_ignores_files_at_the_top_level(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("placeholder")

    assert discover_plugins(tmp_path) == []


def test_discover_plugins_skips_a_plugin_that_raises_on_import(tmp_path: Path) -> None:
    _write_plugin(tmp_path, "broken-plugin", source="raise RuntimeError('boom')\n")

    assert discover_plugins(tmp_path) == []


def test_discover_plugins_skips_a_plugin_missing_the_module_level_instance(
    tmp_path: Path,
) -> None:
    _write_plugin(tmp_path, "no-instance", source="x = 1\n")

    assert discover_plugins(tmp_path) == []


def test_discover_plugins_skips_a_plugin_with_invalid_metadata(tmp_path: Path) -> None:
    _write_plugin(tmp_path, "bad-slug", slug="Not A Valid Slug!")

    assert discover_plugins(tmp_path) == []


def test_discover_plugins_raises_on_duplicate_slugs(tmp_path: Path) -> None:
    _write_plugin(tmp_path, "plugin-a", slug="same-slug")
    _write_plugin(tmp_path, "plugin-b", slug="same-slug")

    with pytest.raises(PluginLoadError, match="duplicate plugin slug"):
        discover_plugins(tmp_path)


def test_discover_plugins_disables_a_plugin_requiring_a_newer_core(tmp_path: Path) -> None:
    _write_plugin(tmp_path, "future-plugin", min_core_version="999.0.0")

    discovered = discover_plugins(tmp_path)

    assert len(discovered) == 1
    assert discovered[0].enabled is False


@pytest.mark.parametrize(
    ("enabled_plugins", "expected_enabled"),
    [
        (None, True),
        ({"example-plugin"}, True),
        ({"some-other-plugin"}, False),
        (set(), False),
    ],
)
def test_discover_plugins_respects_enabled_plugins_allow_list(
    tmp_path: Path, enabled_plugins: set[str] | None, expected_enabled: bool
) -> None:
    _write_plugin(tmp_path, "example-plugin")

    discovered = discover_plugins(tmp_path, enabled_plugins)

    assert discovered[0].enabled is expected_enabled


def test_register_plugins_mounts_only_enabled_plugin_routers(tmp_path: Path) -> None:
    _write_plugin(tmp_path, "enabled-plugin", min_core_version="0.0.1")
    _write_plugin(tmp_path, "disabled-plugin", min_core_version="999.0.0")

    discovered = discover_plugins(tmp_path)
    app = FastAPI()
    register_plugins(app, discovered, "/api/v1")

    from fastapi.testclient import TestClient

    client = TestClient(app)
    assert client.get("/api/v1/plugins/enabled-plugin/ping").status_code == 200
    assert client.get("/api/v1/plugins/disabled-plugin/ping").status_code == 404


def test_register_plugins_stores_all_discovered_plugins_on_app_state(tmp_path: Path) -> None:
    _write_plugin(tmp_path, "enabled-plugin", min_core_version="0.0.1")
    _write_plugin(tmp_path, "disabled-plugin", min_core_version="999.0.0")

    discovered = discover_plugins(tmp_path)
    app = FastAPI()
    register_plugins(app, discovered, "/api/v1")

    assert len(app.state.plugins) == 2
