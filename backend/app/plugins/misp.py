"""MISP threat-intelligence plugin.

Ingests MISP events and surfaces them as risks in the register, so threat
intel feeds directly into risk identification. Runs in demo mode (bundled
sample events) or live mode (queries a MISP instance's REST API with an API
key). MISP threat levels map to Lighthouse impact; likelihood is set high
because these are active, observed threats.
"""
from __future__ import annotations

import uuid
from typing import List, Optional

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.plugins.base import (
    RiskSourcePlugin,
    RiskCandidate,
    PluginRunResult,
    registry,
)
from app.schemas.plugin import PluginStatus

# MISP threat_level_id → Lighthouse impact.
_THREAT_LEVEL_TO_IMPACT = {
    "1": "Critical",   # High
    "2": "High",       # Medium
    "3": "Medium",     # Low
    "4": "Low",        # Undefined
}

_SAMPLE_EVENTS = [
    {
        "uuid": "5f3a1b2c-aaaa-bbbb-cccc-000000000001",
        "info": "Ransomware campaign targeting healthcare (LockBit affiliate)",
        "threat_level_id": "1",
        "tags": ["ransomware", "healthcare", "tlp:amber"],
    },
    {
        "uuid": "5f3a1b2c-aaaa-bbbb-cccc-000000000002",
        "info": "Phishing kit impersonating Microsoft 365 login",
        "threat_level_id": "2",
        "tags": ["phishing", "credential-theft", "tlp:green"],
    },
    {
        "uuid": "5f3a1b2c-aaaa-bbbb-cccc-000000000003",
        "info": "Cobalt Strike C2 infrastructure observed in sector",
        "threat_level_id": "1",
        "tags": ["c2", "cobalt-strike", "apt"],
    },
    {
        "uuid": "5f3a1b2c-aaaa-bbbb-cccc-000000000004",
        "info": "Exploitation of unpatched VPN appliances (CVE-2024-XXXX)",
        "threat_level_id": "2",
        "tags": ["vulnerability", "exploitation", "vpn"],
    },
]


class MISPPlugin(RiskSourcePlugin):
    name = "misp"
    display_name = "MISP Threat Intelligence"
    version = "1.0.0"
    description = (
        "Ingests MISP threat-intelligence events and surfaces them as risks in "
        "the register."
    )

    def status(self) -> PluginStatus:
        if not settings.misp_plugin_enabled:
            return PluginStatus(configured=False, healthy=False, mode="disabled",
                                message="Plugin disabled via configuration.")
        if settings.misp_demo_mode:
            return PluginStatus(configured=True, healthy=True, mode="demo",
                                message="Demo mode — using bundled sample events.")
        if not settings.misp_url or not settings.misp_api_key:
            return PluginStatus(configured=False, healthy=False, mode="live",
                                message="Live mode requires misp_url and misp_api_key.")
        return PluginStatus(configured=True, healthy=True, mode="live",
                            message=f"Live mode — {settings.misp_url}.")

    def _fetch_events(self) -> List[dict]:
        if settings.misp_demo_mode:
            return list(_SAMPLE_EVENTS)
        return self._fetch_live_events()

    def _fetch_live_events(self) -> List[dict]:  # pragma: no cover - needs MISP
        headers = {
            "Authorization": settings.misp_api_key,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        resp = httpx.post(
            f"{settings.misp_url.rstrip('/')}/events/restSearch",
            headers=headers,
            json={"returnFormat": "json", "limit": 100, "published": True},
            verify=settings.misp_verify_ssl,
            timeout=30.0,
        )
        resp.raise_for_status()
        payload = resp.json()
        events = []
        for item in payload.get("response", []):
            ev = item.get("Event", item)
            events.append({
                "uuid": ev.get("uuid"),
                "info": ev.get("info", "MISP event"),
                "threat_level_id": str(ev.get("threat_level_id", "3")),
                "tags": [t.get("name") for t in ev.get("Tag", []) if t.get("name")],
            })
        return events

    async def collect(
        self, db: AsyncSession, client_id: Optional[uuid.UUID] = None
    ) -> PluginRunResult:
        from app.plugins.base import upsert_risks

        events = self._fetch_events()
        candidates = [
            RiskCandidate(
                external_id=f"misp:{e['uuid']}",
                title=f"Threat intel: {e['info']}",
                description=(
                    f"Imported from MISP (event {e['uuid']}). "
                    f"Tags: {', '.join(e.get('tags') or []) or 'none'}."
                ),
                impact=_THREAT_LEVEL_TO_IMPACT.get(str(e.get("threat_level_id")), "Medium"),
                likelihood="Likely",
                threat="External threat actor",
                tags=["threat-intel", "misp", *(e.get("tags") or [])],
                owner="Threat Intelligence",
            )
            for e in events
        ]
        return await upsert_risks(db, self.name, candidates, client_id)


registry.register(MISPPlugin())
