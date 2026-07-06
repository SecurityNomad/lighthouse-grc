from typing import List, Optional
from pydantic import BaseModel


class PluginStatus(BaseModel):
    """Runtime health of a plugin, surfaced in the UI."""
    configured: bool          # has the operator supplied the needed settings?
    healthy: bool             # is it ready to run right now?
    mode: str                 # "live", "demo", or "disabled"
    message: str              # human-readable status detail


class PluginRead(BaseModel):
    name: str                 # stable id, e.g. "aws_config"
    display_name: str
    type: str                 # "risk_source" | "notification"
    version: str
    description: str
    status: PluginStatus


class PluginRunResult(BaseModel):
    """Outcome of triggering a plugin run."""
    plugin: str
    ok: bool
    created: int = 0          # new records imported
    skipped: int = 0          # duplicates / already present
    message: str = ""
    errors: List[str] = []
