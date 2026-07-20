# plugins

Drop-in location for Digital Chintu plugins (e.g. Home Assistant
integration, custom plugins — see `docs/SDS/08_Plugins/`).

The extension point itself is implemented
([docs/features/010_Plugin_Framework.md](../docs/features/010_Plugin_Framework.md),
[docs/architecture/05_PLUGIN_SDK.md](../docs/architecture/05_PLUGIN_SDK.md)):
the backend discovers any `<name>/plugin.py` here that exposes a
module-level `plugin: Plugin` instance (`backend/app/core/plugins.py`) at
startup and mounts its routes under `/api/v1/plugins/{slug}`. This
directory is still empty — no real plugin has been built yet; that's
`041_Home_Assistant`/`042_Device_Control`, both not started.
