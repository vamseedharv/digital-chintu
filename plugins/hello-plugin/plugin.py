"""Reference plugin proving the extension point end-to-end. Not a real
integration — see docs/architecture/05_PLUGIN_SDK.md for the contract this
implements, and docs/features/010_Plugin_Framework.md for why it exists.

Mounted at /api/v1/plugins/hello-plugin when PLUGINS_DIR includes this
directory (the repo-root plugins/ by default) and it isn't excluded by
ENABLED_PLUGINS.
"""

from fastapi import APIRouter

from app.core.plugins import Plugin, PluginMetadata

router = APIRouter()


@router.get("/hello")
def hello() -> dict[str, str]:
    return {"message": "Hello from the reference plugin!"}


class HelloPlugin(Plugin):
    metadata = PluginMetadata(
        slug="hello-plugin",
        name="Hello Plugin",
        version="0.1.0",
        min_core_version="0.1.0",
    )

    def router(self) -> APIRouter | None:
        return router


plugin = HelloPlugin()
