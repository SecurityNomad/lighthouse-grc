"""Tests for /api/v1/audits (plans, items, findings) endpoints."""
import pytest
from httpx import AsyncClient

PLAN_PAYLOAD = {
    "title": "SOC 2 Type II Audit 2025",
    "scope": "Security and Availability criteria",
    "status": "Draft",
}


@pytest.mark.asyncio
async def test_list_audit_plans_empty(client: AsyncClient):
    response = await client.get("/api/v1/audits")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_audit_plan(client: AsyncClient):
    response = await client.post("/api/v1/audits", json=PLAN_PAYLOAD)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == PLAN_PAYLOAD["title"]
    assert data["status"] == "Draft"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_plans_returns_summary_counts(client: AsyncClient):
    # Create plan
    plan_resp = await client.post("/api/v1/audits", json=PLAN_PAYLOAD)
    plan_id = plan_resp.json()["id"]

    # Add items
    await client.post(f"/api/v1/audits/{plan_id}/items", json={"plan_id": plan_id, "description": "Check MFA"})
    await client.post(f"/api/v1/audits/{plan_id}/items", json={"plan_id": plan_id, "description": "Check backups"})

    # List plans — must include counts
    list_resp = await client.get("/api/v1/audits")
    plans = list_resp.json()
    matching = [p for p in plans if p["id"] == plan_id]
    assert len(matching) == 1
    plan = matching[0]
    assert plan["item_count"] == 2
    assert "pass_count" in plan
    assert "fail_count" in plan
    assert "open_findings" in plan


@pytest.mark.asyncio
async def test_update_audit_plan(client: AsyncClient):
    create_resp = await client.post("/api/v1/audits", json=PLAN_PAYLOAD)
    plan_id = create_resp.json()["id"]

    update_resp = await client.put(f"/api/v1/audits/{plan_id}", json={"status": "Active"})
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "Active"


@pytest.mark.asyncio
async def test_delete_audit_plan(client: AsyncClient):
    create_resp = await client.post("/api/v1/audits", json=PLAN_PAYLOAD)
    plan_id = create_resp.json()["id"]

    del_resp = await client.delete(f"/api/v1/audits/{plan_id}")
    assert del_resp.status_code == 204

    get_resp = await client.get(f"/api/v1/audits/{plan_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_audit_items_crud(client: AsyncClient):
    plan_resp = await client.post("/api/v1/audits", json=PLAN_PAYLOAD)
    plan_id = plan_resp.json()["id"]

    # Create item
    item_resp = await client.post(
        f"/api/v1/audits/{plan_id}/items",
        json={"plan_id": plan_id, "description": "Verify encryption at rest", "test_result": "Not Tested"},
    )
    assert item_resp.status_code == 201
    item_id = item_resp.json()["id"]
    assert item_resp.json()["test_result"] == "Not Tested"

    # List items
    list_resp = await client.get(f"/api/v1/audits/{plan_id}/items")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1

    # Update result
    update_resp = await client.put(
        f"/api/v1/audits/{plan_id}/items/{item_id}",
        json={"test_result": "Pass"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["test_result"] == "Pass"

    # Delete
    del_resp = await client.delete(f"/api/v1/audits/{plan_id}/items/{item_id}")
    assert del_resp.status_code == 204


@pytest.mark.asyncio
async def test_audit_findings_crud(client: AsyncClient):
    plan_resp = await client.post("/api/v1/audits", json=PLAN_PAYLOAD)
    plan_id = plan_resp.json()["id"]

    # Create finding
    finding_resp = await client.post(
        f"/api/v1/audits/{plan_id}/findings",
        json={
            "plan_id": plan_id,
            "title": "MFA not enforced",
            "description": "Admin accounts lack MFA.",
            "severity": "High",
            "status": "Open",
        },
    )
    assert finding_resp.status_code == 201
    finding_id = finding_resp.json()["id"]
    assert finding_resp.json()["severity"] == "High"

    # List findings
    list_resp = await client.get(f"/api/v1/audits/{plan_id}/findings")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1

    # Update status to In Remediation
    update_resp = await client.put(
        f"/api/v1/audits/{plan_id}/findings/{finding_id}",
        json={"status": "In Remediation"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "In Remediation"

    # Close finding — closed_at should be set
    close_resp = await client.put(
        f"/api/v1/audits/{plan_id}/findings/{finding_id}",
        json={"status": "Closed"},
    )
    assert close_resp.status_code == 200
    assert close_resp.json()["status"] == "Closed"
    assert close_resp.json()["closed_at"] is not None

    # Delete
    del_resp = await client.delete(f"/api/v1/audits/{plan_id}/findings/{finding_id}")
    assert del_resp.status_code == 204


@pytest.mark.asyncio
async def test_audit_report(client: AsyncClient):
    plan_resp = await client.post("/api/v1/audits", json=PLAN_PAYLOAD)
    plan_id = plan_resp.json()["id"]

    await client.post(
        f"/api/v1/audits/{plan_id}/items",
        json={"plan_id": plan_id, "description": "Check logs", "test_result": "Pass"},
    )
    await client.post(
        f"/api/v1/audits/{plan_id}/findings",
        json={"plan_id": plan_id, "title": "Issue", "description": "Detail", "severity": "Medium", "status": "Open"},
    )

    report_resp = await client.get(f"/api/v1/audits/{plan_id}/report")
    assert report_resp.status_code == 200
    report = report_resp.json()
    assert "plan" in report
    assert "item_summary" in report
    assert "findings" in report
    assert "finding_summary" in report
    assert report["item_summary"]["pass"] == 1
