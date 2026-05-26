import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.risk import Risk
from app.models.control import Control
from app.models.control_mapping import RiskControl
from app.schemas.control_mapping import RiskControlCreate, RiskControlRead, ControlWithMappingRead, GapAnalysisRead
from app.schemas.control import ControlRead
from app.schemas.risk import RiskRead

router = APIRouter()


@router.post("/risks/{risk_id}/controls", response_model=RiskControlRead, status_code=status.HTTP_201_CREATED)
async def add_control_mapping(risk_id: uuid.UUID, body: RiskControlCreate, db: AsyncSession = Depends(get_db)):
    # Validate risk exists
    risk = (await db.execute(select(Risk).where(Risk.id == risk_id))).scalar_one_or_none()
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    # Validate control exists
    control = (await db.execute(select(Control).where(Control.id == body.control_id))).scalar_one_or_none()
    if not control:
        raise HTTPException(status_code=404, detail="Control not found")
    # Check not already mapped
    existing = (await db.execute(
        select(RiskControl).where(RiskControl.risk_id == risk_id, RiskControl.control_id == body.control_id)
    )).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Mapping already exists")

    mapping = RiskControl(risk_id=risk_id, control_id=body.control_id, notes=body.notes)
    db.add(mapping)
    await db.commit()
    await db.refresh(mapping)
    return mapping


@router.delete("/risks/{risk_id}/controls/{control_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_control_mapping(risk_id: uuid.UUID, control_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    mapping = (await db.execute(
        select(RiskControl).where(RiskControl.risk_id == risk_id, RiskControl.control_id == control_id)
    )).scalar_one_or_none()
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")
    await db.delete(mapping)
    await db.commit()


@router.get("/risks/{risk_id}/controls", response_model=List[ControlWithMappingRead])
async def list_risk_controls(risk_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    risk = (await db.execute(select(Risk).where(Risk.id == risk_id))).scalar_one_or_none()
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")

    result = await db.execute(
        select(Control, RiskControl.notes, RiskControl.created_at)
        .join(RiskControl, Control.id == RiskControl.control_id)
        .where(RiskControl.risk_id == risk_id)
        .order_by(Control.ref)
    )
    rows = result.all()
    out = []
    for control, notes, mapped_at in rows:
        out.append(ControlWithMappingRead(
            id=control.id,
            framework_id=control.framework_id,
            ref=control.ref,
            domain=control.domain,
            title=control.title,
            description=control.description,
            notes=notes,
            mapped_at=mapped_at,
        ))
    return out


@router.get("/controls/{control_id}/risks", response_model=List[RiskRead])
async def list_control_risks(control_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    control = (await db.execute(select(Control).where(Control.id == control_id))).scalar_one_or_none()
    if not control:
        raise HTTPException(status_code=404, detail="Control not found")

    result = await db.execute(
        select(Risk)
        .join(RiskControl, Risk.id == RiskControl.risk_id)
        .where(RiskControl.control_id == control_id)
        .order_by(Risk.created_at.desc())
    )
    return result.scalars().all()


@router.get("/gap-analysis", response_model=GapAnalysisRead)
async def gap_analysis(db: AsyncSession = Depends(get_db)):
    # Risks with no control mappings
    mapped_risk_ids = select(RiskControl.risk_id).distinct()
    unmapped_risks_result = await db.execute(
        select(Risk).where(Risk.id.not_in(mapped_risk_ids)).order_by(Risk.created_at.desc())
    )
    unmapped_risks = unmapped_risks_result.scalars().all()

    # Controls with no risk mappings
    mapped_control_ids = select(RiskControl.control_id).distinct()
    uncovered_controls_result = await db.execute(
        select(Control).where(Control.id.not_in(mapped_control_ids)).order_by(Control.ref)
    )
    uncovered_controls = uncovered_controls_result.scalars().all()

    return GapAnalysisRead(
        unmapped_risks=[RiskRead.model_validate(r) for r in unmapped_risks],
        uncovered_controls=[ControlRead.model_validate(c) for c in uncovered_controls],
    )
