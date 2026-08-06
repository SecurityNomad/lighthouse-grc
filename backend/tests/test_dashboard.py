"""Tests for /api/v1/dashboard endpoint."""
import io
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_dashboard_returns_all_fields(client: AsyncClient):
    response = await client.get("/api/v1/dashboard")
    assert response.status_code == 200
    data = response.json()

    required_fields = [
        "open_risks_by_impact",
        "high_risks_open",
        "control_coverage_pct",
        "evidence_expiring_soon",
        "evidence_expired",
        "vendors_by_tier",
        "vendors_under_review",
        "open_findings",
        "audits_active",
    ]
    for field in required_fields:
        assert field in data, f"Missing field: {field}"


@pytest.mark.asyncio
async def test_dashboard_types(client: AsyncClient):
    response = await client.get("/api/v1/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["open_risks_by_impact"], list)
    assert isinstance(data["vendors_by_tier"], list)
    assert isinstance(data["high_risks_open"], int)
    assert isinstance(data["control_coverage_pct"], float)
    assert isinstance(data["open_findings"], int)
    assert isinstance(data["audits_active"], int)
    assert data["high_risks_open"] >= 0
    assert 0.0 <= data["control_coverage_pct"] <= 100.0


@pytest.mark.asyncio
async def test_dashboard_reflects_created_risks(client: AsyncClient):
    # Create one High risk
    await client.post(
        "/api/v1/risks/",
        json={"title": "High risk", "impact": "High", "likelihood": "Possible", "treatment": "Mitigate", "status": "Open"},
    )
    response = await client.get("/api/v1/dashboard")
    data = response.json()
    assert data["high_risks_open"] >= 1
    total_open = sum(r["count"] for r in data["open_risks_by_impact"])
    assert total_open >= 1


@pytest.mark.asyncio
async def test_dashboard_reflects_active_audit(client: AsyncClient):
    await client.post(
        "/api/v1/audits",
        json={"title": "Active Audit", "status": "Active"},
    )
    response = await client.get("/api/v1/dashboard")
    assert response.json()["audits_active"] >= 1


@pytest.mark.asyncio
async def test_dashboard_reflects_vendor(client: AsyncClient):
    await client.post(
        "/api/v1/vendors",
        json={"name": "Cloudflare", "category": "CDN", "tier": 2, "status": "Active"},
    )
    response = await client.get("/api/v1/dashboard")
    vendors_by_tier = response.json()["vendors_by_tier"]
    tier_2 = next((v for v in vendors_by_tier if v["tier"] == 2), None)
    assert tier_2 is not None
    assert tier_2["count"] >= 1


@pytest.mark.asyncio
async def test_dashboard_control_coverage_pct(client: AsyncClient):
    # Create a risk and map a control to it
    risk_resp = await client.post(
        "/api/v1/risks/",
        json={"title": "Coverage risk", "impact": "Medium", "likelihood": "Possible", "treatment": "Mitigate", "status": "Open"},
    )
    risk_id = risk_resp.json()["id"]

    fw_resp = await client.get("/api/v1/frameworks")
    soc2 = next(fw for fw in fw_resp.json() if fw["slug"] == "soc2")
    ctrl_resp = await client.get(f"/api/v1/frameworks/{soc2['id']}/controls")
    control_id = ctrl_resp.json()[0]["id"]

    await client.post(f"/api/v1/risks/{risk_id}/controls", json={"control_id": control_id})

    response = await client.get("/api/v1/dashboard")
    assert response.json()["control_coverage_pct"] > 0


@pytest.mark.asyncio
async def test_control_coverage_never_exceeds_100_percent(client: AsyncClient):
    """Regression: a Closed or Accepted risk with a control mapped used to count
    toward the numerator while being excluded from the denominator, producing a
    coverage figure above 100%."""
    controls = (await client.get("/api/v1/soa/iso27001")).json()["rows"]
    control_id = controls[0]["control_id"]

    # An active population is required first: with no active risks the endpoint
    # short-circuits to 0.0 and the bug cannot surface.
    mapped = await client.post("/api/v1/risks/", json={
        "title": "Active mapped risk", "impact": "High", "likelihood": "Possible",
        "treatment": "Mitigate", "owner": "CISO", "status": "Open",
    })
    await client.post(
        f"/api/v1/risks/{mapped.json()['id']}/controls",
        json={"control_id": control_id},
    )
    await client.post("/api/v1/risks/", json={
        "title": "Active unmapped risk", "impact": "Low", "likelihood": "Rare",
        "treatment": "Mitigate", "owner": "CISO", "status": "Open",
    })

    # Not asserted as an exact figure: tests in this module share a database, so
    # the active population is whatever earlier tests left behind plus these two.
    before = (await client.get("/api/v1/dashboard")).json()["control_coverage_pct"]
    assert before > 0.0, "setup failed to produce an active, covered population"

    # Inactive risks that DO have a control mapped. Each one used to add to the
    # numerator while being excluded from the denominator.
    for status in ("Closed", "Accepted"):
        r = await client.post("/api/v1/risks/", json={
            "title": f"{status} mapped risk", "impact": "Low", "likelihood": "Rare",
            "treatment": "Accept", "owner": "CISO", "status": status,
        })
        await client.post(
            f"/api/v1/risks/{r.json()['id']}/controls",
            json={"control_id": control_id},
        )

    after = (await client.get("/api/v1/dashboard")).json()["control_coverage_pct"]

    # Closed and Accepted risks are outside the active population entirely, so
    # mapping controls to them must not move coverage at all.
    assert after == before, f"coverage moved {before}% -> {after}%"
    assert after <= 100.0, f"coverage was {after}%"
