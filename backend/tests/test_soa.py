"""
Tests for /api/v1/soa — the Statement of Applicability (WBS 1.5.2) and the
SOC 2 readiness figures it feeds to the dashboard (WBS 1.5.3).

Frameworks are seeded into the test DB by the engine fixture in conftest.py.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_soa_returns_every_control_even_when_unassessed(client: AsyncClient):
    """ISO 27001 requires the SoA to account for all 93 Annex A controls, so an
    unassessed control must still appear as a row."""
    response = await client.get("/api/v1/soa/iso27001")
    assert response.status_code == 200
    data = response.json()

    assert data["summary"]["total_controls"] == 93
    assert len(data["rows"]) == 93
    # Nothing seeded yet in the test DB, so every row is a default.
    assert data["summary"]["assessed"] == 0
    assert all(r["entry_id"] is None for r in data["rows"])
    assert all(r["applicable"] is True for r in data["rows"])
    assert all(r["implementation_status"] == "Not Implemented" for r in data["rows"])


@pytest.mark.asyncio
async def test_soa_unknown_framework_404(client: AsyncClient):
    response = await client.get("/api/v1/soa/not-a-framework")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_upsert_creates_then_updates_single_entry(client: AsyncClient):
    rows = (await client.get("/api/v1/soa/iso27001")).json()["rows"]
    control = next(r for r in rows if r["ref"] == "8.8")

    created = await client.put(
        f"/api/v1/soa/control/{control['control_id']}",
        json={
            "implementation_status": "Partially Implemented",
            "justification": "Scanning in place; remediation SLA breached in April.",
            "owner": "Head of Infrastructure",
        },
    )
    assert created.status_code == 200
    body = created.json()
    assert body["entry_id"] is not None
    assert body["implementation_status"] == "Partially Implemented"
    assert body["ref"] == "8.8"

    # A second PUT must update in place rather than violating the unique
    # (control_id, client_id) constraint.
    updated = await client.put(
        f"/api/v1/soa/control/{control['control_id']}",
        json={"implementation_status": "Implemented"},
    )
    assert updated.status_code == 200
    assert updated.json()["entry_id"] == body["entry_id"]
    assert updated.json()["implementation_status"] == "Implemented"
    # Unset fields are preserved, not blanked.
    assert updated.json()["owner"] == "Head of Infrastructure"

    summary = (await client.get("/api/v1/soa/iso27001")).json()["summary"]
    assert summary["assessed"] == 1
    assert summary["implemented"] == 1


@pytest.mark.asyncio
async def test_excluded_control_does_not_depress_readiness(client: AsyncClient):
    """A control excluded with justification is out of scope, so it should not
    count against the readiness percentage."""
    rows = (await client.get("/api/v1/soa/cis_v8")).json()["rows"]

    # Implement one control, exclude another, leave the rest untouched.
    await client.put(
        f"/api/v1/soa/control/{rows[0]['control_id']}",
        json={"implementation_status": "Implemented"},
    )
    await client.put(
        f"/api/v1/soa/control/{rows[1]['control_id']}",
        json={"applicable": False, "justification": "Out of ISMS scope."},
    )

    summary = (await client.get("/api/v1/soa/cis_v8")).json()["summary"]
    assert summary["excluded"] == 1
    assert summary["applicable"] == summary["total_controls"] - 1
    # 1 implemented out of 17 applicable (18 controls - 1 excluded).
    expected = round(1 / summary["applicable"] * 100, 1)
    assert summary["readiness_pct"] == expected


@pytest.mark.asyncio
async def test_partial_implementation_earns_half_weight(client: AsyncClient):
    rows = (await client.get("/api/v1/soa/cis_v8")).json()["rows"]
    await client.put(
        f"/api/v1/soa/control/{rows[0]['control_id']}",
        json={"implementation_status": "Partially Implemented"},
    )
    summary = (await client.get("/api/v1/soa/cis_v8")).json()["summary"]
    assert summary["partially_implemented"] == 1
    assert summary["readiness_pct"] == round(0.5 / summary["applicable"] * 100, 1)


@pytest.mark.asyncio
async def test_upsert_unknown_control_404(client: AsyncClient):
    import uuid
    response = await client.put(
        f"/api/v1/soa/control/{uuid.uuid4()}",
        json={"implementation_status": "Implemented"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_invalid_implementation_status_rejected(client: AsyncClient):
    rows = (await client.get("/api/v1/soa/cis_v8")).json()["rows"]
    response = await client.put(
        f"/api/v1/soa/control/{rows[0]['control_id']}",
        json={"implementation_status": "Mostly Done"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_dashboard_exposes_framework_readiness(client: AsyncClient):
    """WBS 1.5.3 requires the SOC 2 readiness percentage on the dashboard."""
    baseline = (await client.get("/api/v1/dashboard")).json()
    assert baseline["soc2_cc_total"] == 33      # CC criteria only, excludes A1.x
    assert baseline["soc2_cc_assessed"] == 0
    assert baseline["soc2_readiness_pct"] == 0.0

    rows = (await client.get("/api/v1/soa/soc2")).json()["rows"]
    cc = [r for r in rows if r["ref"].startswith("CC")]
    for r in cc[:17]:
        await client.put(
            f"/api/v1/soa/control/{r['control_id']}",
            json={"implementation_status": "Implemented"},
        )

    data = (await client.get("/api/v1/dashboard")).json()
    assert data["soc2_cc_assessed"] == 17
    # 17 of 17 applicable-and-assessed are implemented.
    assert data["soc2_readiness_pct"] == 100.0
    # Comfortably past the WBS 1.5.3 bar of 50% of CC criteria mapped.
    assert data["soc2_cc_assessed"] / data["soc2_cc_total"] >= 0.5
