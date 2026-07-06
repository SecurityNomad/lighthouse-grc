"""Plugin package.

Importing this package registers all built-in plugins with the shared
``registry`` (each plugin module calls ``registry.register(...)`` at import
time). Import the submodules here so a single ``import app.plugins`` wires
everything up.
"""
from app.plugins.base import (  # noqa: F401
    Plugin,
    PluginType,
    RiskSourcePlugin,
    NotificationPlugin,
    NotificationEvent,
    RiskCandidate,
    registry,
    dispatch_notification,
    upsert_risks,
)

# Side-effecting imports: registering the built-in plugins.
from app.plugins import aws_config  # noqa: F401,E402
from app.plugins import misp  # noqa: F401,E402
from app.plugins import slack  # noqa: F401,E402
