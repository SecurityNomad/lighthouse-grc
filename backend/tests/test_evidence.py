"""Tests for /api/v1/evidence endpoints."""
import io
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_evidence_empty(client: AsyncClient):
    response = await client.get("/api/v1/evidence/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_upload_evidence(client: AsyncClient):
    file_content = b"This is a test policy document."
    response = await client.post(
        "/api/v1/evidence/",
        data={"title": "Access Control Policy"},
        files={"file": ("access_policy.pdf", io.BytesIO(file_content), "application/pdf")},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Access Control Policy"
    assert data["file_name"] == "access_policy.pdf"
    assert data["file_size"] == len(file_content)
    assert "id" in data
    assert data["status"] in ("Current", "Expiring", "Expired")
    return data["id"]


@pytest.mark.asyncio
async def test_list_evidence_after_upload(client: AsyncClient):
    # Upload first
    await client.post(
        "/api/v1/evidence/",
        data={"title": "SOC 2 Report 2025"},
        files={"file": ("soc2.pdf", io.BytesIO(b"report content"), "application/pdf")},
    )
    response = await client.get("/api/v1/evidence/")
    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_get_evidence(client: AsyncClient):
    upload_resp = await client.post(
        "/api/v1/evidence/",
        data={"title": "Pen Test Report"},
        files={"file": ("pentest.pdf", io.BytesIO(b"results"), "application/pdf")},
    )
    ev_id = upload_resp.json()["id"]

    response = await client.get(f"/api/v1/evidence/{ev_id}")
    assert response.status_code == 200
    assert response.json()["id"] == ev_id


@pytest.mark.asyncio
async def test_update_evidence(client: AsyncClient):
    upload_resp = await client.post(
        "/api/v1/evidence/",
        data={"title": "Original Title"},
        files={"file": ("doc.txt", io.BytesIO(b"content"), "text/plain")},
    )
    ev_id = upload_resp.json()["id"]

    update_resp = await client.patch(
        f"/api/v1/evidence/{ev_id}",
        json={"title": "Updated Title", "expiry_date": "2027-12-31"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["title"] == "Updated Title"
    assert update_resp.json()["expiry_date"] == "2027-12-31"


@pytest.mark.asyncio
async def test_delete_evidence(client: AsyncClient):
    upload_resp = await client.post(
        "/api/v1/evidence/",
        data={"title": "To Delete"},
        files={"file": ("delete_me.txt", io.BytesIO(b"bye"), "text/plain")},
    )
    ev_id = upload_resp.json()["id"]

    del_resp = await client.delete(f"/api/v1/evidence/{ev_id}")
    assert del_resp.status_code == 204

    get_resp = await client.get(f"/api/v1/evidence/{ev_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_get_nonexistent_evidence(client: AsyncClient):
    response = await client.get("/api/v1/evidence/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_upload_evidence_with_expiry(client: AsyncClient):
    response = await client.post(
        "/api/v1/evidence/",
        data={"title": "Expiring Doc", "expiry_date": "2026-12-31"},
        files={"file": ("expiring.pdf", io.BytesIO(b"content"), "application/pdf")},
    )
    assert response.status_code == 201
    assert response.json()["expiry_date"] == "2026-12-31"
