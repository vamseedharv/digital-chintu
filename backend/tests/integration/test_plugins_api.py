import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import create_app
from tests.conftest import make_test_client

_STARTUP_PLUGIN_SOURCE = """
from fastapi import APIRouter
from app.core.plugins import Plugin, PluginMetadata

router = APIRouter()

startup_calls: list[str] = []
shutdown_calls: list[str] = []


@router.get("/ping")
def ping() -> dict[str, str]:
    return {"pong": "lifecycle-plugin"}


class _LifecyclePlugin(Plugin):
    metadata = PluginMetadata(
        slug="lifecycle-plugin", name="Lifecycle Plugin", version="1.0.0", min_core_version="0.0.1"
    )

    def router(self):
        return router

    async def on_startup(self) -> None:
        startup_calls.append("started")

    async def on_shutdown(self) -> None:
        shutdown_calls.append("stopped")


plugin = _LifecyclePlugin()
"""

_FAILING_LIFECYCLE_PLUGIN_SOURCE = """
from fastapi import APIRouter
from app.core.plugins import Plugin, PluginMetadata

router = APIRouter()


@router.get("/ping")
def ping() -> dict[str, str]:
    return {"pong": "failing-lifecycle-plugin"}


class _FailingLifecyclePlugin(Plugin):
    metadata = PluginMetadata(
        slug="failing-lifecycle-plugin",
        name="Failing Lifecycle Plugin",
        version="1.0.0",
        min_core_version="0.0.1",
    )

    def router(self):
        return router

    async def on_startup(self) -> None:
        raise RuntimeError("startup boom")

    async def on_shutdown(self) -> None:
        raise RuntimeError("shutdown boom")


plugin = _FailingLifecyclePlugin()
"""

_DISABLED_LIFECYCLE_PLUGIN_SOURCE = """
from fastapi import APIRouter
from app.core.plugins import Plugin, PluginMetadata

router = APIRouter()

startup_calls: list[str] = []


class _DisabledLifecyclePlugin(Plugin):
    metadata = PluginMetadata(
        slug="disabled-lifecycle-plugin",
        name="Disabled Lifecycle Plugin",
        version="1.0.0",
        # Deliberately unsatisfiable, so this plugin is discovered but disabled.
        min_core_version="999.0.0",
    )

    def router(self):
        return router

    async def on_startup(self) -> None:
        startup_calls.append("should not run")


plugin = _DisabledLifecyclePlugin()
"""

_SIMPLE_PLUGIN_SOURCE = """
from fastapi import APIRouter
from app.core.plugins import Plugin, PluginMetadata

router = APIRouter()


@router.get("/ping")
def ping() -> dict[str, str]:
    return {{"pong": "{slug}"}}


class _SimplePlugin(Plugin):
    metadata = PluginMetadata(
        slug="{slug}", name="{name}", version="1.0.0", min_core_version="0.0.1"
    )

    def router(self):
        return router


plugin = _SimplePlugin()
"""


def _write_plugin(plugins_dir: Path, dir_name: str, source: str) -> None:
    plugin_dir = plugins_dir / dir_name
    plugin_dir.mkdir(parents=True)
    (plugin_dir / "plugin.py").write_text(source)


def _client_with_plugins_dir(
    monkeypatch: pytest.MonkeyPatch, plugins_dir: Path, enabled_plugins: str | None = None
) -> TestClient:
    monkeypatch.setenv("PLUGINS_DIR", str(plugins_dir))
    if enabled_plugins is not None:
        monkeypatch.setenv("ENABLED_PLUGINS", enabled_plugins)
    get_settings.cache_clear()
    return make_test_client(create_app())


def test_plugins_endpoint_lists_the_reference_hello_plugin(
    client: TestClient,
) -> None:
    # Default PLUGINS_DIR (repo-root plugins/) contains only the trivial
    # hello-plugin reference implementation today — see plugins/README.md.
    response = client.get("/api/v1/plugins")

    assert response.status_code == 200
    assert response.json() == [
        {"slug": "hello-plugin", "name": "Hello Plugin", "version": "0.1.0", "enabled": True}
    ]


def test_the_reference_hello_plugins_router_is_reachable(client: TestClient) -> None:
    response = client.get("/api/v1/plugins/hello-plugin/hello")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello from the reference plugin!"}


def test_plugins_endpoint_lists_a_discovered_and_enabled_plugin(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_plugin(
        tmp_path,
        "example-plugin",
        _SIMPLE_PLUGIN_SOURCE.format(slug="example-plugin", name="Example"),
    )
    client = _client_with_plugins_dir(monkeypatch, tmp_path)

    response = client.get("/api/v1/plugins")

    assert response.status_code == 200
    assert response.json() == [
        {"slug": "example-plugin", "name": "Example", "version": "1.0.0", "enabled": True}
    ]


def test_an_enabled_plugins_router_is_reachable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_plugin(
        tmp_path,
        "example-plugin",
        _SIMPLE_PLUGIN_SOURCE.format(slug="example-plugin", name="Example"),
    )
    client = _client_with_plugins_dir(monkeypatch, tmp_path)

    response = client.get("/api/v1/plugins/example-plugin/ping")

    assert response.status_code == 200
    assert response.json() == {"pong": "example-plugin"}


def test_a_plugin_excluded_by_enabled_plugins_is_listed_but_not_mounted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_plugin(
        tmp_path,
        "example-plugin",
        _SIMPLE_PLUGIN_SOURCE.format(slug="example-plugin", name="Example"),
    )
    client = _client_with_plugins_dir(monkeypatch, tmp_path, enabled_plugins="some-other-plugin")

    list_response = client.get("/api/v1/plugins")
    ping_response = client.get("/api/v1/plugins/example-plugin/ping")

    assert list_response.json() == [
        {"slug": "example-plugin", "name": "Example", "version": "1.0.0", "enabled": False}
    ]
    assert ping_response.status_code == 404


def test_a_broken_plugin_does_not_prevent_the_app_from_starting(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_plugin(tmp_path, "broken-plugin", "raise RuntimeError('boom')\n")
    _write_plugin(
        tmp_path,
        "working-plugin",
        _SIMPLE_PLUGIN_SOURCE.format(slug="working-plugin", name="Working"),
    )
    client = _client_with_plugins_dir(monkeypatch, tmp_path)

    health_response = client.get("/api/v1/health")
    list_response = client.get("/api/v1/plugins")

    assert health_response.status_code == 200
    assert [item["slug"] for item in list_response.json()] == ["working-plugin"]


def test_plugin_startup_and_shutdown_hooks_run_with_the_app_lifespan(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_plugin(tmp_path, "lifecycle-plugin", _STARTUP_PLUGIN_SOURCE)
    monkeypatch.setenv("PLUGINS_DIR", str(tmp_path))
    get_settings.cache_clear()

    app = create_app()
    plugin_module = sys.modules["_digital_chintu_plugin_lifecycle-plugin"]

    with make_test_client(app) as client:
        response = client.get("/api/v1/plugins/lifecycle-plugin/ping")
        assert response.status_code == 200
        assert plugin_module.startup_calls == ["started"]
        assert plugin_module.shutdown_calls == []

    assert plugin_module.shutdown_calls == ["stopped"]


def test_a_plugin_raising_in_on_startup_or_on_shutdown_does_not_crash_the_app(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_plugin(tmp_path, "failing-lifecycle-plugin", _FAILING_LIFECYCLE_PLUGIN_SOURCE)
    monkeypatch.setenv("PLUGINS_DIR", str(tmp_path))
    get_settings.cache_clear()

    # Neither on_startup nor on_shutdown raising should propagate out of the
    # lifespan context — the rest of the app (and other plugins) must still
    # come up and serve requests normally.
    with make_test_client(create_app()) as client:
        response = client.get("/api/v1/health")
        assert response.status_code == 200


def test_a_disabled_plugins_lifecycle_hooks_are_not_invoked(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_plugin(tmp_path, "lifecycle-plugin", _STARTUP_PLUGIN_SOURCE)
    _write_plugin(tmp_path, "disabled-lifecycle-plugin", _DISABLED_LIFECYCLE_PLUGIN_SOURCE)
    monkeypatch.setenv("PLUGINS_DIR", str(tmp_path))
    get_settings.cache_clear()

    with make_test_client(create_app()) as client:
        response = client.get("/api/v1/plugins")
        assert response.status_code == 200

    disabled_module = sys.modules["_digital_chintu_plugin_disabled-lifecycle-plugin"]
    assert disabled_module.startup_calls == []
    enabled_module = sys.modules["_digital_chintu_plugin_lifecycle-plugin"]
    assert enabled_module.startup_calls == ["started"]


def test_openapi_schema_documents_the_plugins_endpoint(client: TestClient) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/api/v1/plugins" in response.json()["paths"]
