import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.control import Control, Framework
from app.models.soa import ControlApplicability, READINESS_WEIGHTS
from app.schemas.soa import SoARead, SoARow, SoASummary, SoAEntryUpdate

router = APIRouter()


def _summarise(slug: str, name: str, rows: list[SoARow]) -> SoASummary:
    total = len(rows)
    assessed = sum(1 for r in rows if r.entry_id is not None)
    applicable = [r for r in rows if r.applicable]
    excluded = total - len(applicable)

    counts = {s: 0 for s in READINESS_WEIGHTS}
    for r in applicable:
        counts[r.implementation_status] = counts.get(r.implementation_status, 0) + 1

    # Readiness is weighted across applicable controls only — excluding a
    # control with documented justification should not depress the score.
    weighted = sum(READINESS_WEIGHTS.get(r.implementation_status, 0.0) for r in applicable)
    readiness = round(weighted / len(applicable) * 100, 1) if applicable else 0.0

    return SoASummary(
        framework_slug=slug,
        framework_name=name,
        total_controls=total,
        assessed=assessed,
        applicable=len(applicable),
        excluded=excluded,
        implemented=counts.get("Implemented", 0),
        partially_implemented=counts.get("Partially Implemented", 0),
        planned=counts.get("Planned", 0),
        not_implemented=counts.get("Not Implemented", 0),
        coverage_pct=round(assessed / total * 100, 1) if total else 0.0,
        readiness_pct=readiness,
    )


@router.get("/soa/{framework_slug}", response_model=SoARead)
async def get_soa(
    framework_slug: str,
    client_id: Optional[uuid.UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Full Statement of Applicability for a framework.

    Every control in the framework is returned whether or not it has been
    assessed — ISO 27001 requires the SoA to account for all Annex A controls,
    so an unassessed control is a meaningful row, not an absent one.
    """
    framework = (
        await db.execute(select(Framework).where(Framework.slug == framework_slug))
    ).scalar_one_or_none()
    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")

    controls = (
        await db.execute(
            select(Control)
            .where(Control.framework_id == framework.id)
            .order_by(Control.ref)
        )
    ).scalars().all()

    entry_query = select(ControlApplicability).where(
        ControlApplicability.control_id.in_([c.id for c in controls])
    )
    entry_query = entry_query.where(ControlApplicability.client_id == client_id)
    entries = {
        e.control_id: e for e in (await db.execute(entry_query)).scalars().all()
    }

    rows = []
    for c in controls:
        e = entries.get(c.id)
        rows.append(
            SoARow(
                control_id=c.id,
                ref=c.ref,
                domain=c.domain,
                title=c.title,
                description=c.description,
                entry_id=e.id if e else None,
                applicable=e.applicable if e else True,
                justification=e.justification if e else None,
                implementation_status=e.implementation_status if e else "Not Implemented",
                owner=e.owner if e else None,
                last_reviewed=e.last_reviewed if e else None,
            )
        )

    return SoARead(summary=_summarise(framework.slug, framework.name, rows), rows=rows)


@router.put("/soa/control/{control_id}", response_model=SoARow)
async def upsert_soa_entry(
    control_id: uuid.UUID,
    payload: SoAEntryUpdate,
    client_id: Optional[uuid.UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Create or update the SoA position for one control."""
    control = (
        await db.execute(select(Control).where(Control.id == control_id))
    ).scalar_one_or_none()
    if not control:
        raise HTTPException(status_code=404, detail="Control not found")

    entry = (
        await db.execute(
            select(ControlApplicability).where(
                ControlApplicability.control_id == control_id,
                ControlApplicability.client_id == client_id,
            )
        )
    ).scalar_one_or_none()

    if entry is None:
        entry = ControlApplicability(control_id=control_id, client_id=client_id)
        db.add(entry)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(entry, field, value)

    await db.commit()
    await db.refresh(entry)

    return SoARow(
        control_id=control.id,
        ref=control.ref,
        domain=control.domain,
        title=control.title,
        description=control.description,
        entry_id=entry.id,
        applicable=entry.applicable,
        justification=entry.justification,
        implementation_status=entry.implementation_status,
        owner=entry.owner,
        last_reviewed=entry.last_reviewed,
    )
