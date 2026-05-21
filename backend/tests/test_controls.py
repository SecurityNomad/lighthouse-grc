"""
Tests for /api/v1/frameworks and /api/v1/controls endpoints.
Frameworks are seeded into the test DB by the engine fixture in conftest.py.
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_frameworks(client: AsyncClient):
    response = await client.get("/api/v1/frameworks")
    assert response.status_code == 200
    data = response.json()
    slugs = {fw["slug"] for fw in data}
    assert {"soc2", "iso27001", "cis_v8"} == slugs
    for fw in data:
        assert fw["control_count"] > 0


@pytest.mark.asyncio
async def test_list_frameworks_have_expected_counts(client: AsyncClient):
    response = await client.get("/api/v1/frameworks")
    counts = {fw["slug"]: fw["control_count"] for fw in response.json()}
    assert counts["soc2"] == 36
    assert counts["iso27001"] == 93
    assert counts["cis_v8"] == 18


@pytest.mark.asyncio
async def test_list_controls_for_framework(client: AsyncClient):
    # Get soc2 framework id
    fw_resp = await client.get("/api/v1/frameworks")
    soc2 = next(fw for fw in fw_resp.json() if fw["slug"] == "soc2")
    fw_id = soc2["id"]

    response = await client.get(f"/api/v1/frameworks/{fw_id}/controls")
    assert response.status_code == 200
    controls = response.json()
    assert len(controls) == 36
    refs = [c["ref"] for c in controls]
    assert "CC6.1" in refs
    assert "A1.1" in refs


@pytest.mark.asyncio
async def test_list_controls_search(client: AsyncClient):
    fw_resp = await client.get("/api/v1/frameworks")
    soc2 = next(fw for fw in fw_resp.json() if fw["slug"] == "soc2")
    fw_id = soc2["id"]

    response = await client.get(f"/api/v1/frameworks/{fw_id}/controls", params={"search": "access"})
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    # All results should mention "access" somewhere
    for c in results:
        combined = (c["title"] + c["domain"] + c["ref"]).lower()
        assert "access" in combined


@pytest.mark.asyncio
async def test_list_controls_domain_filter(client: AsyncClient):
    fw_resp = await client.get("/api/v1/frameworks")
    soc2 = next(fw for fw in fw_resp.json() if fw["slug"] == "soc2")
    fw_id = soc2["id"]

    response = await client.get(
        f"/api/v1/frameworks/{fw_id}/controls",
        params={"domain": "Logical and Physical Access"},
    )
    assert response.status_code == 200
    controls = response.json()
    assert len(controls) == 8
    assert all(c["domain"] == "Logical and Physical Access" for c in controls)


@pytest.mark.asyncio
async def test_get_control(client: AsyncClient):
    fw_resp = await client.get("/api/v1/frameworks")
    iso = next(fw for fw in fw_resp.json() if fw["slug"] == "iso27001")
    fw_id = iso["id"]

    controls_resp = await client.get(f"/api/v1/frameworks/{fw_id}/controls")
    control_id = controls_resp.json()[0]["id"]

    response = await client.get(f"/api/v1/controls/{control_id}")
    assert response.status_code == 200
    assert response.json()["id"] == control_id


@pytest.mark.asyncio
async def test_get_control_not_found(client: AsyncClient):
    response = await client.get("/api/v1/controls/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_controls_framework_not_found(client: AsyncClient):
    response = await client.get(
        "/api/v1/frameworks/00000000-0000-0000-0000-000000000000/controls"
    )
    assert response.status_code == 404
