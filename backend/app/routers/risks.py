import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.risk import Risk
from app.schemas.risk import RiskCreate, RiskRead, RiskUpdate

router = APIRouter()


@router.get("/", response_model=List[RiskRead])
async def list_risks(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
):
    query = select(Risk).order_by(Risk.created_at.desc())
    if status_filter:
        query = query.where(Risk.status == status_filter)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=RiskRead, status_code=status.HTTP_201_CREATED)
async def create_risk(risk_in: RiskCreate, db: AsyncSession = Depends(get_db)):
    risk = Risk(**risk_in.model_dump())
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
