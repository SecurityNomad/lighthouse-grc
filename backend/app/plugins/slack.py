"""Slack notification plugin.

Pushes domain events (new high-severity risk, evidence expiring, audit finding
raised, TPRM assessment overdue) to a Slack incoming webhook. With no webhook
configured it runs in demo mode: it logs the message instead of posting, so the
notification flow is exercised end-to-end without a live Slack workspace.
"""
from __future__ import annotations

import logging

import httpx

from app.config import settings
from app.plugins.base import NotificationPlugin, NotificationEvent, registry
from app.schemas.plugin import PluginStatus

logger = logging.getLogger("lighthouse.plugins.slack")

_SEVERITY_EMOJI = {"critical": "🔴", "high": "🟠", "info": "🔵"}


class SlackPlugin(NotificationPlugin):
    name = "slack"
    display_name = "Slack Notifications"
    version = "1.0.0"
    description = (
        "Posts alerts (new high risks, expiring evidence, audit findings) to a "
        "Slack incoming webhook."
    )

    def status(self) -> PluginStatus:
        if not settings.slack_plugin_enabled:
            return PluginStatus(configured=False, healthy=False, mode="disabled",
                                message="Plugin disabled via configuration.")
        if not settings.slack_webhook_url:
            return PluginStatus(configured=True, healthy=True, mode="demo",
                                message="Demo mode — messages are logged, not posted.")
        return PluginStatus(configured=True, healthy=True, mode="live",
                            message="Live mode — posting to configured webhook.")

    def _format(self, event: NotificationEvent) -> str:
        emoji = _SEVERITY_EMOJI.get(event.severity, "🔵")
        text = f"{emoji} *{event.title}*\n{event.message}"
        if event.link:
            text += f"\n<{event.link}|View in Lighthouse>"
        return text

    async def send(self, event: NotificationEvent) -> bool:
        if not settings.slack_plugin_enabled:
            return False
        text = self._format(event)
        if not settings.slack_webhook_url:
            logger.info("[slack:demo] %s", text.replace("\n", " | "))
            return True
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(settings.slack_webhook_url, json={"text": text})
            resp.raise_for_status()
        return True


registry.register(SlackPlugin())
