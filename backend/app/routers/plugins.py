import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.plugins.base import (
    registry,
    RiskSourcePlugin,
    NotificationPlugin,
    NotificationEvent,
    PluginType,
)
from app.schemas.plugin import PluginRead, PluginRunResult

router = APIRouter()


def _to_read(plugin) -> PluginRead:
    return PluginRead(
        name=plugin.name,
        display_name=plugin.display_name,
        type=plugin.plugin_type.value,
        version=plugin.version,
        description=plugin.description,
        status=plugin.status(),
    )


@router.get("/plugins", response_model=List[PluginRead])
async def list_plugins():
    return [_to_read(p) for p in registry.all()]


@router.post("/plugins/{name}/run", response_model=PluginRunResult)
async def run_plugin(
    name: str,
    client_id: Optional[uuid.UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    plugin = registry.get(name)
    if plugin is None:
        raise HTTPException(status_code=404, detail="Plugin not found")

    status = plugin.status()
    if not status.healthy:
        raise HTTPException(status_code=409, detail=f"Plugin not ready: {status.message}")

    if isinstance(plugin, RiskSourcePlugin):
        return await plugin.collect(db, client_id=client_id)

    if isinstance(plugin, NotificationPlugin):
        # "Running" a notification plugin sends a test message.
        event = NotificationEvent(
            event_type="plugin.test",
            title="Lighthouse test notification",
            message=f"This is a test message from the {plugin.display_name} plugin.",
            severity="info",
        )
        ok = await plugin.send(event)
        return PluginRunResult(
            plugin=plugin.name,
            ok=ok,
            message="Test notification sent." if ok else "Failed to send test notification.",
        )

    raise HTTPException(status_code=400, detail="Plugin type cannot be run")
