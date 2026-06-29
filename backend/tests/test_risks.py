"""
Smoke tests for the /api/v1/risks endpoints.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_list_risks(client: AsyncClient):
    response = await client.get("/api/v1/risks/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_risk(client: AsyncClient):
    payload = {
        "title": "SQL Injection via public API",
        "description": "Unsanitised inputs in the search endpoint.",
        "impact": "High",
        "likelihood": "Possible",
        "treatment": "Mitigate",
        "status": "Open",
    }
    response = await client.post("/api/v1/risks/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert "id" in data
    assert data["impact"] == "High"
    return data["id"]


@pytest.mark.asyncio
async def test_get_risk(client: AsyncClient):
    # Create first
    payload = {"title": "Test risk for GET", "impact": "Low", "likelihood": "Rare", "treatment": "Accept", "status": "Open"}
    create_resp = await client.post("/api/v1/risks/", json=payload)
    risk_id = create_resp.json()["id"]

    # Then retrieve
    response = await client.get(f"/api/v1/risks/{risk_id}")
    assert response.status_code == 200
    assert response.json()["id"] == risk_id


@pytest.mark.asyncio
async def test_update_risk(client: AsyncClient):
    payload = {"title": "Risk to update", "impact": "Medium", "likelihood": "Possible", "treatment": "Mitigate", "status": "Open"}
    create_resp = await client.post("/api/v1/risks/", json=payload)
    risk_id = create_resp.json()["id"]

    update_resp = await client.put(f"/api/v1/risks/{risk_id}", json={"status": "In Treatment"})
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "In Treatment"


@pytest.mark.asyncio
async def test_delete_risk(client: AsyncClient):
    payload = {"title": "Risk to delete", "impact": "Low", "likelihood": "Rare", "treatment": "Accept", "status": "Open"}
    create_resp = await client.post("/api/v1/risks/", json=payload)
    risk_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/api/v1/risks/{risk_id}")
    assert delete_resp.status_code == 204

    get_resp = await client.get(f"/api/v1/risks/{risk_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_get_nonexistent_risk(client: AsyncClient):
    response = await client.get("/api/v1/risks/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
