"""Lighthouse plugin SDK.

Per ADR-001 (#3) integrations implement a common, typed interface and are
optional — the platform runs fully with none installed. Two capability types:

  * RiskSourcePlugin  — pulls findings from an external system into the Risk
                        Register (AWS Config/Security Hub, MISP).
  * NotificationPlugin — pushes events out to an external channel (Slack).

Every plugin reports a PluginStatus so the operator can see whether it is
configured and in "live" or "demo" mode without triggering a run. Plugins
self-register at import time via the module-level ``registry``.
"""
from __future__ import annotations

import abc
import logging
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

logger = logging.getLogger("lighthouse.plugins")

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.risk import Risk, IMPACT_SCORE_MAP, LIKELIHOOD_SCORE_MAP
from app.schemas.plugin import PluginRunResult, PluginStatus


class PluginType(str, Enum):
    RISK_SOURCE = "risk_source"
    NOTIFICATION = "notification"


@dataclass(frozen=True)
class NotificationEvent:
    """A domain event worth notifying about."""
    event_type: str            # e.g. "risk.created", "evidence.expiring"
    title: str
    message: str
    severity: str = "info"     # info | high | critical
    link: Optional[str] = None


class Plugin(abc.ABC):
    """Base class for all plugins."""

    # Subclasses set these.
    name: str = ""
    display_name: str = ""
    version: str = "1.0.0"
    description: str = ""
    plugin_type: PluginType

    @abc.abstractmethod
    def status(self) -> PluginStatus:
        """Report whether the plugin is configured and ready, without side effects."""
        raise NotImplementedError


class RiskSourcePlugin(Plugin):
    plugin_type = PluginType.RISK_SOURCE

    @abc.abstractmethod
    async def collect(
        self, db: AsyncSession, client_id: Optional[uuid.UUID] = None
    ) -> PluginRunResult:
        """Pull findings from the source and upsert them as risks."""
        raise NotImplementedError


class NotificationPlugin(Plugin):
    plugin_type = PluginType.NOTIFICATION

    @abc.abstractmethod
    async def send(self, event: NotificationEvent) -> bool:
        """Deliver a single event. Returns True on success."""
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: Dict[str, Plugin] = {}

    def register(self, plugin: Plugin) -> Plugin:
        if not plugin.name:
            raise ValueError("Plugin must define a non-empty `name`")
        self._plugins[plugin.name] = plugin
        return plugin

    def get(self, name: str) -> Optional[Plugin]:
        return self._plugins.get(name)

    def all(self) -> List[Plugin]:
        return list(self._plugins.values())

    def of_type(self, plugin_type: PluginType) -> List[Plugin]:
        return [p for p in self._plugins.values() if p.plugin_type == plugin_type]

    def clear(self) -> None:  # test helper
        self._plugins.clear()


registry = PluginRegistry()


# ---------------------------------------------------------------------------
# Shared helper for risk-source plugins
# ---------------------------------------------------------------------------

@dataclass
class RiskCandidate:
    """A normalized finding a RiskSourcePlugin wants to import as a risk."""
    external_id: str
    title: str
    description: str = ""
    impact: str = "Medium"
    likelihood: str = "Possible"
    threat: Optional[str] = None
    tags: Optional[List[str]] = None
    owner: Optional[str] = None


async def upsert_risks(
    db: AsyncSession,
    source: str,
    candidates: List[RiskCandidate],
    client_id: Optional[uuid.UUID] = None,
) -> PluginRunResult:
    """Insert each candidate as a Risk, skipping any whose (source, external_id)
    already exists so repeated runs are idempotent. Computes the integer scores
    the same way the risks router does."""
    result = PluginRunResult(plugin=source, ok=True)

    # Existing external_ids for this source (optionally scoped to a client).
    existing_query = select(Risk.external_id).where(Risk.source == source)
    if client_id is not None:
        existing_query = existing_query.where(Risk.client_id == client_id)
    existing_rows = await db.execute(existing_query)
    existing_ids = {row[0] for row in existing_rows.all()}

    seen: set[str] = set()
    for c in candidates:
        if c.external_id in existing_ids or c.external_id in seen:
            result.skipped += 1
            continue
        seen.add(c.external_id)

        impact_score = IMPACT_SCORE_MAP.get(c.impact, 3)
        likelihood_score = LIKELIHOOD_SCORE_MAP.get(c.likelihood, 3)
        risk = Risk(
            title=c.title,
            description=c.description,
            threat=c.threat,
            impact=c.impact,
            likelihood=c.likelihood,
            tags=c.tags,
            owner=c.owner,
            source=source,
            external_id=c.external_id,
            client_id=client_id,
            impact_score=impact_score,
            likelihood_score=likelihood_score,
            risk_score=impact_score * likelihood_score,
        )
        db.add(risk)
        result.created += 1

    await db.commit()
    result.message = f"Imported {result.created} risk(s), skipped {result.skipped} duplicate(s)."
    return result


async def dispatch_notification(event: NotificationEvent) -> int:
    """Deliver an event to every registered notification plugin. Failsafe: a
    misbehaving or unreachable channel is logged and skipped, never raised —
    notifications must not break the domain action that triggered them.
    Returns the number of successful deliveries."""
    delivered = 0
    for plugin in registry.of_type(PluginType.NOTIFICATION):
        try:
            if await plugin.send(event):
                delivered += 1
        except Exception:
            logger.exception("Notification plugin %r failed to send", plugin.name)
    return delivered
