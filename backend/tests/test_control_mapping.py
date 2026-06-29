"""Tests for risk↔control mapping and gap analysis endpoints."""
import pytest
from httpx import AsyncClient


async def _create_risk(client: AsyncClient, title: str = "Test risk") -> str:
    resp = await client.post(
        "/api/v1/risks/",
        json={"title": title, "impact": "High", "likelihood": "Possible", "treatment": "Mitigate", "status": "Open"},
    )
    return resp.json()["id"]


async def _get_soc2_control(client: AsyncClient) -> dict:
    fw_resp = await client.get("/api/v1/frameworks")
    soc2 = next(fw for fw in fw_resp.json() if fw["slug"] == "soc2")
    controls_resp = await client.get(f"/api/v1/frameworks/{soc2['id']}/controls")
    return controls_resp.json()[0]


@pytest.mark.asyncio
async def test_add_control_to_risk(client: AsyncClient):
    risk_id = await _create_risk(client)
    control = await _get_soc2_control(client)

    response = await client.post(
        f"/api/v1/risks/{risk_id}/controls",
        json={"control_id": control["id"]},
    )
    assert response.status_code == 201
    data = response.json()
    assert str(data["risk_id"]) == risk_id
    assert str(data["control_id"]) == control["id"]


@pytest.mark.asyncio
async def test_add_control_with_notes(client: AsyncClient):
    risk_id = await _create_risk(client)
    control = await _get_soc2_control(client)

    response = await client.post(
        f"/api/v1/risks/{risk_id}/controls",
        json={"control_id": control["id"], "notes": "Primary mitigating control"},
    )
    assert response.status_code == 201
    assert response.json()["notes"] == "Primary mitigating control"


@pytest.mark.asyncio
async def test_duplicate_mapping_rejected(client: AsyncClient):
    risk_id = await _create_risk(client)
    control = await _get_soc2_control(client)
    payload = {"control_id": control["id"]}

    await client.post(f"/api/v1/risks/{risk_id}/controls", json=payload)
    response = await client.post(f"/api/v1/risks/{risk_id}/controls", json=payload)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_list_risk_controls(client: AsyncClient):
    risk_id = await _create_risk(client)
    control = await _get_soc2_control(client)
    await client.post(f"/api/v1/risks/{risk_id}/controls", json={"control_id": control["id"]})

    response = await client.get(f"/api/v1/risks/{risk_id}/controls")
    assert response.status_code == 200
    controls = response.json()
    assert len(controls) == 1
    assert controls[0]["id"] == control["id"]


@pytest.mark.asyncio
async def test_remove_control_from_risk(client: AsyncClient):
    risk_id = await _create_risk(client)
    control = await _get_soc2_control(client)
    await client.post(f"/api/v1/risks/{risk_id}/controls", json={"control_id": control["id"]})

    del_resp = await client.delete(f"/api/v1/risks/{risk_id}/controls/{control['id']}")
    assert del_resp.status_code == 204

    list_resp = await client.get(f"/api/v1/risks/{risk_id}/controls")
    assert list_resp.json() == []


@pytest.mark.asyncio
async def test_list_control_risks(client: AsyncClient):
    risk_id = await _create_risk(client, "Risk A")
    control = await _get_soc2_control(client)
    await client.post(f"/api/v1/risks/{risk_id}/controls", json={"control_id": control["id"]})

    response = await client.get(f"/api/v1/controls/{control['id']}/risks")
    assert response.status_code == 200
    risk_ids = [r["id"] for r in response.json()]
    assert risk_id in risk_ids


@pytest.mark.asyncio
async def test_gap_analysis(client: AsyncClient):
    response = await client.get("/api/v1/gap-analysis")
    assert response.status_code == 200
    data = response.json()
    assert "unmapped_risks" in data
    assert "uncovered_controls" in data
    assert isinstance(data["unmapped_risks"], list)
    assert isinstance(data["uncovered_controls"], list)
