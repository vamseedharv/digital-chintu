"""Read-only introspection of discovered plugins — which ones were found
under PLUGINS_DIR and whether each is currently enabled. See
docs/architecture/05_PLUGIN_SDK.md."""

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.core.plugins import DiscoveredPlugin

router = APIRouter()


class PluginInfo(BaseModel):
    slug: str
    name: str
    version: str
    enabled: bool


@router.get("/plugins", response_model=list[PluginInfo])
def list_plugins(request: Request) -> list[PluginInfo]:
    discovered: list[DiscoveredPlugin] = getattr(request.app.state, "plugins", [])
    return [
        PluginInfo(
            slug=item.plugin.metadata.slug,
            name=item.plugin.metadata.name,
            version=item.plugin.metadata.version,
            enabled=item.enabled,
        )
        for item in discovered
    ]
