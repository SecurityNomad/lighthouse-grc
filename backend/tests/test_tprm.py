"""Tests for /api/v1/vendors and vendor assessment endpoints."""
import uuid
import pytest
from httpx import AsyncClient


def _vendor(suffix: str | None = None) -> dict:
    """Return a vendor payload with a unique name to avoid UNIQUE collisions across tests."""
    name = f"Vendor-{suffix or uuid.uuid4().hex[:8]}"
    return {"name": name, "category": "Cloud Infrastructure", "tier": 1, "status": "Active"}


@pytest.mark.asyncio
async def test_list_vendors(client: AsyncClient):
    response = await client.get("/api/v1/vendors")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_vendor(client: AsyncClient):
    payload = _vendor("create")
    response = await client.post("/api/v1/vendors", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["tier"] == 1
    assert "id" in data


@pytest.mark.asyncio
async def test_get_vendor(client: AsyncClient):
    create_resp = await client.post("/api/v1/vendors", json=_vendor())
    vendor_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/vendors/{vendor_id}")
    assert response.status_code == 200
    assert response.json()["id"] == vendor_id


@pytest.mark.asyncio
async def test_update_vendor(client: AsyncClient):
    payload = _vendor()
    create_resp = await client.post("/api/v1/vendors", json=payload)
    vendor_id = create_resp.json()["id"]

    update_resp = await client.put(
        f"/api/v1/vendors/{vendor_id}",
        json={**payload, "status": "Under Review", "tier": 2},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "Under Review"
    assert update_resp.json()["tier"] == 2


@pytest.mark.asyncio
async def test_delete_vendor(client: AsyncClient):
    create_resp = await client.post("/api/v1/vendors", json=_vendor())
    vendor_id = create_resp.json()["id"]

    del_resp = await client.delete(f"/api/v1/vendors/{vendor_id}")
    assert del_resp.status_code == 204

    get_resp = await client.get(f"/api/v1/vendors/{vendor_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_vendor_risk_ratings(client: AsyncClient):
    await client.post("/api/v1/vendors", json=_vendor())
    response = await client.get("/api/v1/vendors/risk-ratings")
    assert response.status_code == 200
    ratings = response.json()
    assert isinstance(ratings, list)
    assert len(ratings) >= 1
    assert "risk_rating" in ratings[0]
    assert "tier" in ratings[0]


@pytest.mark.asyncio
async def test_list_vendor_questions(client: AsyncClient):
    response = await client.get("/api/v1/vendor-questions")
    assert response.status_code == 200
    questions = response.json()
    assert len(questions) > 0
    assert "ref" in questions[0]
    assert "max_score" in questions[0]


@pytest.mark.asyncio
async def test_create_and_complete_assessment(client: AsyncClient):
    # Create vendor
    vendor_resp = await client.post("/api/v1/vendors", json=_vendor())
    vendor_id = vendor_resp.json()["id"]

    # Create assessment
    assessment_resp = await client.post("/api/v1/vendor-assessments", json={"vendor_id": vendor_id})
    assert assessment_resp.status_code == 201
    assessment_id = assessment_resp.json()["id"]
    assert assessment_resp.json()["status"] in ("Draft", "In Progress")

    # Get questions
    questions_resp = await client.get("/api/v1/vendor-questions")
    questions = questions_resp.json()

    # Submit answers
    answers = [{"question_id": q["id"], "score": q["max_score"]} for q in questions[:3]]
    answers_resp = await client.put(
        f"/api/v1/vendor-assessments/{assessment_id}/answers",
        json=answers,
    )
    assert answers_resp.status_code == 200

    # Complete assessment (triggers score computation)
    complete_resp = await client.patch(
        f"/api/v1/vendor-assessments/{assessment_id}",
        json={"status": "Complete"},
    )
    assert complete_resp.status_code == 200
    assert complete_resp.json()["status"] == "Complete"
    assert complete_resp.json()["overall_score"] is not None
