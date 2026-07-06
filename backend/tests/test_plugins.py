"""Tests for the Phase 3 plugin SDK and the AWS/MISP/Slack plugins."""
import uuid

import pytest
from httpx import AsyncClient

from app.plugins.base import registry, PluginType, NotificationEvent, dispatch_notification


async def _create_client(client: AsyncClient, name: str) -> str:
    resp = await client.post("/api/v1/clients", json={"name": name, "industry": "Testing"})
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


# -- Registry / SDK ------------------------------------------------------------

def test_builtin_plugins_registered():
    names = {p.name for p in registry.all()}
    assert {"aws_config", "misp", "slack"} <= names
    assert {p.name for p in registry.of_type(PluginType.NOTIFICATION)} == {"slack"}
    assert {p.name for p in registry.of_type(PluginType.RISK_SOURCE)} == {"aws_config", "misp"}


# -- Listing -------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_plugins(client: AsyncClient):
    resp = await client.get("/api/v1/plugins")
    assert resp.status_code == 200
    plugins = {p["name"]: p for p in resp.json()}
    assert set(plugins) >= {"aws_config", "misp", "slack"}
    assert plugins["aws_config"]["type"] == "risk_source"
    assert plugins["slack"]["type"] == "notification"
    # Each reports a status with a mode (demo in the test config).
    assert plugins["aws_config"]["status"]["mode"] == "demo"
    assert plugins["aws_config"]["status"]["healthy"] is True


# -- Risk-source plugins import into the register ------------------------------

@pytest.mark.asyncio
async def test_aws_import_creates_risks_and_dedups(client: AsyncClient):
    cid = await _create_client(client, "AWS Co")

    r1 = await client.post(f"/api/v1/plugins/aws_config/run?client_id={cid}")
    assert r1.status_code == 200
    body1 = r1.json()
    assert body1["ok"] is True
    assert body1["created"] == 5  # bundled sample findings
    assert body1["skipped"] == 0

    # Imported risks show up in the register with the plugin as their source.
    listing = await client.get(f"/api/v1/risks/?client_id={cid}")
    sources = {r["source"] for r in listing.json()}
    assert sources == {"aws_config"}

    # Re-running is idempotent — everything is skipped.
    r2 = await client.post(f"/api/v1/plugins/aws_config/run?client_id={cid}")
    body2 = r2.json()
    assert body2["created"] == 0
    assert body2["skipped"] == 5


@pytest.mark.asyncio
async def test_misp_import_creates_risks(client: AsyncClient):
    cid = await _create_client(client, "MISP Co")
    resp = await client.post(f"/api/v1/plugins/misp/run?client_id={cid}")
    assert resp.status_code == 200
    assert resp.json()["created"] == 4

    listing = await client.get(f"/api/v1/risks/?client_id={cid}")
    risks = listing.json()
    assert all(r["source"] == "misp" for r in risks)
    assert all(r["external_id"].startswith("misp:") for r in risks)


# -- Notification plugin -------------------------------------------------------

@pytest.mark.asyncio
async def test_slack_run_sends_test_notification(client: AsyncClient):
    resp = await client.post("/api/v1/plugins/slack/run")
    assert resp.status_code == 200
    assert resp.json()["ok"] is True  # demo mode logs and returns success


@pytest.mark.asyncio
async def test_run_unknown_plugin_404(client: AsyncClient):
    resp = await client.post("/api/v1/plugins/nope/run")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_viewer_cannot_run_plugin(viewer_client: AsyncClient):
    resp = await viewer_client.post("/api/v1/plugins/aws_config/run")
    assert resp.status_code == 403


# -- Notification dispatch on new high-severity risk ---------------------------

@pytest.mark.asyncio
async def test_high_risk_triggers_notification(client: AsyncClient, monkeypatch):
    sent = []

    async def fake_send(event):
        sent.append(event)
        return True

    monkeypatch.setattr(registry.get("slack"), "send", fake_send)

    resp = await client.post(
        "/api/v1/risks/",
        json={"title": "Critical exposure", "impact": "Critical", "likelihood": "Likely"},
    )
    assert resp.status_code == 201
    assert len(sent) == 1
    assert sent[0].severity == "critical"
    assert "Critical exposure" in sent[0].title


@pytest.mark.asyncio
async def test_low_risk_does_not_trigger_notification(client: AsyncClient, monkeypatch):
    sent = []

    async def fake_send(event):
        sent.append(event)
        return True

    monkeypatch.setattr(registry.get("slack"), "send", fake_send)

    resp = await client.post(
        "/api/v1/risks/",
        json={"title": "Minor typo risk", "impact": "Low", "likelihood": "Rare"},
    )
    assert resp.status_code == 201
    assert sent == []


@pytest.mark.asyncio
async def test_dispatch_is_failsafe(monkeypatch):
    """A raising notification plugin must not propagate out of dispatch."""
    async def boom(event):
        raise RuntimeError("channel down")

    monkeypatch.setattr(registry.get("slack"), "send", boom)
    delivered = await dispatch_notification(
        NotificationEvent(event_type="t", title="t", message="m")
    )
    assert delivered == 0  # error swallowed, nothing delivered, no exception
