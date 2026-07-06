"""Tests for v1.2 hardening: evidence download, upload limits, role
enforcement, and dashboard client scoping."""
import io
import uuid

import pytest
from httpx import AsyncClient

from app.config import settings


async def _create_client(client: AsyncClient, name: str) -> str:
    """Create a real client via the API and return its id. Risks/vendors/etc.
    carry a FK to clients, so scoped tests must reference a client that exists
    (Postgres enforces the constraint; SQLite does not)."""
    resp = await client.post(
        "/api/v1/clients",
        json={"name": name, "industry": "Testing"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


# -- Evidence download ---------------------------------------------------------

@pytest.mark.asyncio
async def test_download_evidence(client: AsyncClient):
    content = b"downloadable policy content"
    upload = await client.post(
        "/api/v1/evidence/",
        data={"title": "Downloadable"},
        files={"file": ("policy.pdf", io.BytesIO(content), "application/pdf")},
    )
    ev_id = upload.json()["id"]

    resp = await client.get(f"/api/v1/evidence/{ev_id}/download")
    assert resp.status_code == 200
    assert resp.content == content
    assert "policy.pdf" in resp.headers.get("content-disposition", "")


@pytest.mark.asyncio
async def test_download_nonexistent_evidence(client: AsyncClient):
    resp = await client.get(f"/api/v1/evidence/{uuid.uuid4()}/download")
    assert resp.status_code == 404


# -- Upload hardening ----------------------------------------------------------

@pytest.mark.asyncio
async def test_upload_rejects_disallowed_extension(client: AsyncClient):
    resp = await client.post(
        "/api/v1/evidence/",
        data={"title": "Bad"},
        files={"file": ("payload.exe", io.BytesIO(b"MZ..."), "application/octet-stream")},
    )
    assert resp.status_code == 415


@pytest.mark.asyncio
async def test_upload_rejects_oversized_file(client: AsyncClient):
    oversize = b"x" * (settings.max_upload_mb * 1024 * 1024 + 1)
    resp = await client.post(
        "/api/v1/evidence/",
        data={"title": "Huge"},
        files={"file": ("big.pdf", io.BytesIO(oversize), "application/pdf")},
    )
    assert resp.status_code == 413


@pytest.mark.asyncio
async def test_upload_sanitizes_filename(client: AsyncClient):
    resp = await client.post(
        "/api/v1/evidence/",
        data={"title": "Traversal"},
        files={"file": ("../../etc/passwd.txt", io.BytesIO(b"x"), "text/plain")},
    )
    assert resp.status_code == 201
    # Directory components are stripped from the stored file name.
    assert resp.json()["file_name"] == "passwd.txt"


# -- Role enforcement ----------------------------------------------------------

@pytest.mark.asyncio
async def test_viewer_can_read(viewer_client: AsyncClient):
    resp = await viewer_client.get("/api/v1/risks/")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_viewer_cannot_create_risk(viewer_client: AsyncClient):
    resp = await viewer_client.post(
        "/api/v1/risks/",
        json={"title": "Blocked", "impact": "High", "likelihood": "High"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_viewer_cannot_delete_risk(viewer_client: AsyncClient):
    resp = await viewer_client.delete(f"/api/v1/risks/{uuid.uuid4()}")
    assert resp.status_code == 403


# -- Pagination ----------------------------------------------------------------

@pytest.mark.asyncio
async def test_risks_pagination(client: AsyncClient):
    page_client = await _create_client(client, "Pagination Co")
    for i in range(5):
        await client.post(
            f"/api/v1/risks/?client_id={page_client}",
            json={"title": f"Paginated risk {i}", "impact": "Medium", "likelihood": "Possible"},
        )

    page1 = await client.get(f"/api/v1/risks/?client_id={page_client}&limit=2&offset=0")
    page2 = await client.get(f"/api/v1/risks/?client_id={page_client}&limit=2&offset=2")
    assert page1.status_code == 200
    assert len(page1.json()) == 2
    assert len(page2.json()) == 2
    # Pages don't overlap.
    ids1 = {r["id"] for r in page1.json()}
    ids2 = {r["id"] for r in page2.json()}
    assert ids1.isdisjoint(ids2)


@pytest.mark.asyncio
async def test_risks_pagination_rejects_bad_limit(client: AsyncClient):
    resp = await client.get("/api/v1/risks/?limit=0")
    assert resp.status_code == 422


# -- Dashboard client scoping --------------------------------------------------

@pytest.mark.asyncio
async def test_dashboard_scopes_by_client(client: AsyncClient):
    client_a = await _create_client(client, "Hospital A")
    client_b = await _create_client(client, "Insurer B")

    # Two open Critical risks for A, one for B.
    for _ in range(2):
        await client.post(
            f"/api/v1/risks/?client_id={client_a}",
            json={"title": "A risk", "impact": "Critical", "likelihood": "High"},
        )
    await client.post(
        f"/api/v1/risks/?client_id={client_b}",
        json={"title": "B risk", "impact": "Critical", "likelihood": "High"},
    )

    resp_a = await client.get(f"/api/v1/dashboard?client_id={client_a}")
    assert resp_a.status_code == 200
    a_high = resp_a.json()["high_risks_open"]

    resp_b = await client.get(f"/api/v1/dashboard?client_id={client_b}")
    b_high = resp_b.json()["high_risks_open"]

    # Client A sees only its own high risks, distinct from B's.
    assert a_high >= 2
    assert b_high >= 1
    assert a_high != b_high
