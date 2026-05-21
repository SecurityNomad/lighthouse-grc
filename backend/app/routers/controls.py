import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.control import Control, Framework
from app.schemas.control import ControlRead, FrameworkRead

router = APIRouter()


@router.get("/frameworks", response_model=List[FrameworkRead])
async def list_frameworks(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Framework).order_by(Framework.name))
    frameworks = result.scalars().all()

    # attach control counts
    counts_result = await db.execute(
        select(Control.framework_id, func.count(Control.id)).group_by(Control.framework_id)
    )
    counts = dict(counts_result.all())

    out = []
    for fw in frameworks:
        fw_dict = {
            "id": fw.id,
            "slug": fw.slug,
            "name": fw.name,
            "version": fw.version,
            "description": fw.description,
            "control_count": counts.get(fw.id, 0),
        }
        out.append(FrameworkRead(**fw_dict))
    return out


@router.get("/frameworks/{framework_id}/controls", response_model=List[ControlRead])
async def list_controls(
    framework_id: uuid.UUID,
    search: Optional[str] = Query(None, description="Filter by ref, title, or domain"),
    domain: Optional[str] = Query(None, description="Filter by exact domain"),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Framework).where(Framework.id == framework_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Framework not found")

    query = select(Control).where(Control.framework_id == framework_id).order_by(Control.ref)

    if domain:
        query = query.where(Control.domain == domain)

    if search:
        term = f"%{search}%"
        query = query.where(
            Control.title.ilike(term)
            | Control.ref.ilike(term)
            | Control.domain.ilike(term)
        )

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/controls/{control_id}", response_model=ControlRead)
async def get_control(control_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Control).where(Control.id == control_id))
    control = result.scalar_one_or_none()
    if not control:
        raise HTTPException(status_code=404, detail="Control not found")
    return control
