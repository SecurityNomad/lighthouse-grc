import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.risk import Risk, IMPACT_SCORE_MAP, LIKELIHOOD_SCORE_MAP
from app.schemas.risk import RiskCreate, RiskRead, RiskUpdate

router = APIRouter()


@router.get("/", response_model=List[RiskRead])
async def list_risks(
    status_filter: Optional[str] = Query(None, alias="status"),
    client_id: Optional[uuid.UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Risk).order_by(Risk.created_at.desc())
    if status_filter:
        query = query.where(Risk.status == status_filter)
    if client_id:
        query = query.where(Risk.client_id == client_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=RiskRead, status_code=status.HTTP_201_CREATED)
async def create_risk(
    risk_in: RiskCreate,
    client_id: Optional[uuid.UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    risk = Risk(**risk_in.model_dump(), client_id=client_id)
    risk.impact_score = IMPACT_SCORE_MAP.get(risk_in.impact, 3)
    risk.likelihood_score = LIKELIHOOD_SCORE_MAP.get(risk_in.likelihood, 3)
    risk.risk_score = risk.impact_score * risk.likelihood_score
    if risk.residual_impact_score and risk.residual_likelihood_score:
        risk.residual_risk_score = risk.residual_impact_score * risk.residual_likelihood_score
    db.add(risk)
    await db.commit()
    await db.refresh(risk)
    return risk


@router.get("/{risk_id}", response_model=RiskRead)
async def get_risk(risk_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Risk).where(Risk.id == risk_id))
    risk = result.scalar_one_or_none()
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    return risk


@router.put("/{risk_id}", response_model=RiskRead)
async def update_risk(
    risk_id: uuid.UUID, risk_in: RiskUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Risk).where(Risk.id == risk_id))
    risk = result.scalar_one_or_none()
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    for field, value in risk_in.model_dump(exclude_unset=True).items():
        setattr(risk, field, value)
    risk.impact_score = IMPACT_SCORE_MAP.get(risk.impact, 3)
    risk.likelihood_score = LIKELIHOOD_SCORE_MAP.get(risk.likelihood, 3)
    risk.risk_score = risk.impact_score * risk.likelihood_score
    if risk.residual_impact_score and risk.residual_likelihood_score:
        risk.residual_risk_score = risk.residual_impact_score * risk.residual_likelihood_score
    await db.commit()
    await db.refresh(risk)
    return risk


@router.delete("/{risk_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_risk(risk_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Risk).where(Risk.id == risk_id))
    risk = result.scalar_one_or_none()
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    await db.delete(risk)
    await db.commit()
