import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.tprm import Vendor, VendorQuestion, VendorAssessment, VendorAnswer
from app.schemas.tprm import (
    VendorCreate, VendorUpdate, VendorRead, VendorRiskRating,
    VendorQuestionRead,
    VendorAssessmentCreate, VendorAssessmentUpdate, VendorAssessmentRead, VendorAssessmentWithAnswers,
    VendorAnswerUpsert, VendorAnswerRead,
)

router = APIRouter()

RISK_RATING_THRESHOLDS = [
    (80, "Low"),
    (60, "Medium"),
    (40, "High"),
    (0,  "Critical"),
]


def _compute_rating(score: Optional[float]) -> str:
    if score is None:
        return "Not Assessed"
    for threshold, label in RISK_RATING_THRESHOLDS:
        if score >= threshold:
            return label
    return "Critical"


async def _compute_overall_score(assessment_id: uuid.UUID, db: AsyncSession) -> float:
    answers_result = await db.execute(
        select(VendorAnswer).where(VendorAnswer.assessment_id == assessment_id)
    )
    answers = answers_result.scalars().all()

    questions_result = await db.execute(select(VendorQuestion))
    questions = {q.id: q for q in questions_result.scalars().all()}

    weighted_score = 0.0
    weighted_max = 0.0
    for answer in answers:
        q = questions.get(answer.question_id)
        if not q or q.max_score == 0:
            continue
        score = answer.score or 0
        weighted_score += (score / q.max_score) * q.weight
        weighted_max += q.weight

    if weighted_max == 0:
        return 0.0
    return round((weighted_score / weighted_max) * 100, 1)


# -- Vendors -------------------------------------------------------------------

@router.get("/vendors/risk-ratings", response_model=List[VendorRiskRating])
async def list_vendor_risk_ratings(db: AsyncSession = Depends(get_db)):
    """Return every vendor with its most recent completed assessment score."""
    vendors_result = await db.execute(select(Vendor).order_by(Vendor.name))
    vendors = vendors_result.scalars().all()

    # Fetch latest Complete assessment per vendor in one query
    from sqlalchemy import func as sqlfunc
    sub = (
        select(
            VendorAssessment.vendor_id,
            sqlfunc.max(VendorAssessment.updated_at).label("latest_at"),
        )
        .where(VendorAssessment.status == "Complete")
        .group_by(VendorAssessment.vendor_id)
        .subquery()
    )
    assessments_result = await db.execute(
        select(VendorAssessment).join(
            sub,
            (VendorAssessment.vendor_id == sub.c.vendor_id)
            & (VendorAssessment.updated_at == sub.c.latest_at),
        )
    )
    assessment_map = {a.vendor_id: a for a in assessments_result.scalars().all()}

    return [
        VendorRiskRating(
            vendor_id=v.id,
            vendor_name=v.name,
            tier=v.tier,
            overall_score=assessment_map[v.id].overall_score if v.id in assessment_map else None,
            risk_rating=_compute_rating(assessment_map[v.id].overall_score if v.id in assessment_map else None),
            assessment_id=assessment_map[v.id].id if v.id in assessment_map else None,
            assessed_at=assessment_map[v.id].updated_at if v.id in assessment_map else None,
        )
        for v in vendors
    ]


@router.get("/vendors", response_model=List[VendorRead])
async def list_vendors(
    status_filter: Optional[str] = Query(None, alias="status"),
    tier: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    client_id: Optional[uuid.UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Vendor).order_by(Vendor.name)
    if status_filter:
        query = query.where(Vendor.status == status_filter)
    if tier:
        query = query.where(Vendor.tier == tier)
    if category:
        query = query.where(Vendor.category == category)
    if client_id:
        query = query.where(Vendor.client_id == client_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/vendors", response_model=VendorRead, status_code=status.HTTP_201_CREATED)
async def create_vendor(
    body: VendorCreate,
    client_id: Optional[uuid.UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    vendor = Vendor(**body.model_dump(), client_id=client_id)
    db.add(vendor)
    await db.commit()
    await db.refresh(vendor)
    return vendor


@router.get("/vendors/{vendor_id}", response_model=VendorRead)
async def get_vendor(vendor_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Vendor).where(Vendor.id == vendor_id))
    vendor = result.scalar_one_or_none()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor


@router.put("/vendors/{vendor_id}", response_model=VendorRead)
async def update_vendor(vendor_id: uuid.UUID, body: VendorUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Vendor).where(Vendor.id == vendor_id))
    vendor = result.scalar_one_or_none()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(vendor, field, value)
    await db.commit()
    await db.refresh(vendor)
    return vendor


@router.delete("/vendors/{vendor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vendor(vendor_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Vendor).where(Vendor.id == vendor_id))
    vendor = result.scalar_one_or_none()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    await db.delete(vendor)
    await db.commit()


@router.get("/vendors/{vendor_id}/risk-rating", response_model=VendorRiskRating)
async def get_vendor_risk_rating(vendor_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Vendor).where(Vendor.id == vendor_id))
    vendor = result.scalar_one_or_none()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    assessment_result = await db.execute(
        select(VendorAssessment)
        .where(VendorAssessment.vendor_id == vendor_id, VendorAssessment.status == "Complete")
        .order_by(VendorAssessment.updated_at.desc())
        .limit(1)
    )
    assessment = assessment_result.scalar_one_or_none()

    return VendorRiskRating(
        vendor_id=vendor.id,
        vendor_name=vendor.name,
        tier=vendor.tier,
        overall_score=assessment.overall_score if assessment else None,
        risk_rating=_compute_rating(assessment.overall_score if assessment else None),
        assessment_id=assessment.id if assessment else None,
        assessed_at=assessment.updated_at if assessment else None,
    )


# -- Questions -----------------------------------------------------------------

@router.get("/vendor-questions", response_model=List[VendorQuestionRead])
async def list_vendor_questions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(VendorQuestion).order_by(VendorQuestion.ref))
    return result.scalars().all()


# -- Assessments ---------------------------------------------------------------

@router.post("/vendor-assessments", response_model=VendorAssessmentRead, status_code=status.HTTP_201_CREATED)
async def create_assessment(body: VendorAssessmentCreate, db: AsyncSession = Depends(get_db)):
    vendor = (await db.execute(select(Vendor).where(Vendor.id == body.vendor_id))).scalar_one_or_none()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    assessment = VendorAssessment(vendor_id=body.vendor_id)
    db.add(assessment)
    await db.commit()
    await db.refresh(assessment)
    return assessment


@router.get("/vendor-assessments/{assessment_id}", response_model=VendorAssessmentWithAnswers)
async def get_assessment(assessment_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(VendorAssessment).where(VendorAssessment.id == assessment_id))
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    answers_result = await db.execute(
        select(VendorAnswer).where(VendorAnswer.assessment_id == assessment_id)
    )
    answers = answers_result.scalars().all()
    return VendorAssessmentWithAnswers(
        **VendorAssessmentRead.model_validate(assessment).model_dump(),
        answers=[VendorAnswerRead.model_validate(a) for a in answers],
    )


@router.patch("/vendor-assessments/{assessment_id}", response_model=VendorAssessmentRead)
async def update_assessment(assessment_id: uuid.UUID, body: VendorAssessmentUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(VendorAssessment).where(VendorAssessment.id == assessment_id))
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    if body.status == "Complete":
        # Compute and persist overall_score
        assessment.overall_score = await _compute_overall_score(assessment_id, db)

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(assessment, field, value)

    await db.commit()
    await db.refresh(assessment)
    return assessment


@router.delete("/vendor-assessments/{assessment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assessment(assessment_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(VendorAssessment).where(VendorAssessment.id == assessment_id))
    assessment = result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    await db.delete(assessment)
    await db.commit()


@router.put("/vendor-assessments/{assessment_id}/answers", response_model=List[VendorAnswerRead])
async def upsert_answers(assessment_id: uuid.UUID, body: List[VendorAnswerUpsert], db: AsyncSession = Depends(get_db)):
    assessment = (await db.execute(select(VendorAssessment).where(VendorAssessment.id == assessment_id))).scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    existing_result = await db.execute(
        select(VendorAnswer).where(VendorAnswer.assessment_id == assessment_id)
    )
    existing_map = {a.question_id: a for a in existing_result.scalars().all()}

    for item in body:
        if item.question_id in existing_map:
            ans = existing_map[item.question_id]
            ans.score = item.score
            ans.text_response = item.text_response
        else:
            ans = VendorAnswer(
                assessment_id=assessment_id,
                question_id=item.question_id,
                score=item.score,
                text_response=item.text_response,
            )
            db.add(ans)

    await db.commit()
    result = await db.execute(select(VendorAnswer).where(VendorAnswer.assessment_id == assessment_id))
    return result.scalars().all()
