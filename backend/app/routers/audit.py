import uuid
from collections import defaultdict
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.audit import AuditPlan, AuditItem, AuditFinding
from app.schemas.audit import (
    AuditPlanCreate, AuditPlanUpdate, AuditPlanRead, AuditPlanSummary,
    AuditItemCreate, AuditItemUpdate, AuditItemRead,
    AuditFindingCreate, AuditFindingUpdate, AuditFindingRead,
    AuditReportRead,
)

router = APIRouter()


# -- Plans ---------------------------------------------------------------------

@router.get("/audits", response_model=List[AuditPlanSummary])
async def list_plans(
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
):
    query = select(AuditPlan).order_by(AuditPlan.created_at.desc())
    if status_filter:
        query = query.where(AuditPlan.status == status_filter)
    result = await db.execute(query)
    plans = result.scalars().all()

    if not plans:
        return []

    plan_ids = [p.id for p in plans]

    all_items_result = await db.execute(
        select(AuditItem).where(AuditItem.plan_id.in_(plan_ids))
    )
    plan_items: dict = defaultdict(list)
    for item in all_items_result.scalars().all():
        plan_items[item.plan_id].append(item)

    open_findings_result = await db.execute(
        select(AuditFinding.plan_id, func.count(AuditFinding.id))
        .where(
            AuditFinding.plan_id.in_(plan_ids),
            AuditFinding.status.in_(["Open", "In Remediation"]),
        )
        .group_by(AuditFinding.plan_id)
    )
    open_findings_map = dict(open_findings_result.all())

    summaries = []
    for plan in plans:
        items = plan_items[plan.id]
        summaries.append(
            AuditPlanSummary(
                **AuditPlanRead.model_validate(plan).model_dump(),
                item_count=len(items),
                pass_count=sum(1 for i in items if i.test_result == "Pass"),
                fail_count=sum(1 for i in items if i.test_result == "Fail"),
                exception_count=sum(1 for i in items if i.test_result == "Exception"),
                not_tested_count=sum(1 for i in items if i.test_result == "Not Tested"),
                open_findings=open_findings_map.get(plan.id, 0),
            )
        )
    return summaries


@router.post("/audits", response_model=AuditPlanRead, status_code=status.HTTP_201_CREATED)
async def create_plan(body: AuditPlanCreate, db: AsyncSession = Depends(get_db)):
    plan = AuditPlan(**body.model_dump())
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    return plan


@router.get("/audits/{plan_id}", response_model=AuditPlanSummary)
async def get_plan(plan_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AuditPlan).where(AuditPlan.id == plan_id))
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Audit plan not found")

    items_result = await db.execute(select(AuditItem).where(AuditItem.plan_id == plan_id))
    items = items_result.scalars().all()

    findings_result = await db.execute(
        select(func.count(AuditFinding.id)).where(
            AuditFinding.plan_id == plan_id,
            AuditFinding.status.in_(["Open", "In Remediation"])
        )
    )
    open_findings = findings_result.scalar() or 0

    return AuditPlanSummary(
        **AuditPlanRead.model_validate(plan).model_dump(),
        item_count=len(items),
        pass_count=sum(1 for i in items if i.test_result == "Pass"),
        fail_count=sum(1 for i in items if i.test_result == "Fail"),
        exception_count=sum(1 for i in items if i.test_result == "Exception"),
        not_tested_count=sum(1 for i in items if i.test_result == "Not Tested"),
        open_findings=open_findings,
    )


@router.put("/audits/{plan_id}", response_model=AuditPlanRead)
async def update_plan(plan_id: uuid.UUID, body: AuditPlanUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AuditPlan).where(AuditPlan.id == plan_id))
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Audit plan not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(plan, field, value)
    await db.commit()
    await db.refresh(plan)
    return plan


@router.delete("/audits/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(plan_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AuditPlan).where(AuditPlan.id == plan_id))
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Audit plan not found")
    await db.delete(plan)
    await db.commit()


@router.get("/audits/{plan_id}/report", response_model=AuditReportRead)
async def get_report(plan_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AuditPlan).where(AuditPlan.id == plan_id))
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Audit plan not found")

    items_result = await db.execute(select(AuditItem).where(AuditItem.plan_id == plan_id))
    items = items_result.scalars().all()

    findings_result = await db.execute(select(AuditFinding).where(AuditFinding.plan_id == plan_id))
    findings = findings_result.scalars().all()

    item_summary = {
        "pass": sum(1 for i in items if i.test_result == "Pass"),
        "fail": sum(1 for i in items if i.test_result == "Fail"),
        "exception": sum(1 for i in items if i.test_result == "Exception"),
        "not_tested": sum(1 for i in items if i.test_result == "Not Tested"),
    }
    finding_summary = {
        "open": sum(1 for f in findings if f.status == "Open"),
        "in_remediation": sum(1 for f in findings if f.status == "In Remediation"),
        "closed": sum(1 for f in findings if f.status == "Closed"),
        "critical": sum(1 for f in findings if f.severity == "Critical"),
        "high": sum(1 for f in findings if f.severity == "High"),
        "medium": sum(1 for f in findings if f.severity == "Medium"),
        "low": sum(1 for f in findings if f.severity == "Low"),
    }

    return AuditReportRead(
        plan=AuditPlanRead.model_validate(plan),
        item_summary=item_summary,
        findings=[AuditFindingRead.model_validate(f) for f in findings],
        finding_summary=finding_summary,
    )


# -- Items ---------------------------------------------------------------------

@router.get("/audits/{plan_id}/items", response_model=List[AuditItemRead])
async def list_items(plan_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AuditItem).where(AuditItem.plan_id == plan_id))
    return result.scalars().all()


@router.post("/audits/{plan_id}/items", response_model=AuditItemRead, status_code=status.HTTP_201_CREATED)
async def create_item(plan_id: uuid.UUID, body: AuditItemCreate, db: AsyncSession = Depends(get_db)):
    plan = (await db.execute(select(AuditPlan).where(AuditPlan.id == plan_id))).scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Audit plan not found")
    item = AuditItem(**{**body.model_dump(), "plan_id": plan_id})
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.put("/audits/{plan_id}/items/{item_id}", response_model=AuditItemRead)
async def update_item(plan_id: uuid.UUID, item_id: uuid.UUID, body: AuditItemUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AuditItem).where(AuditItem.id == item_id, AuditItem.plan_id == plan_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Audit item not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/audits/{plan_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(plan_id: uuid.UUID, item_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AuditItem).where(AuditItem.id == item_id, AuditItem.plan_id == plan_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Audit item not found")
    await db.delete(item)
    await db.commit()


# -- Findings ------------------------------------------------------------------

@router.get("/audits/{plan_id}/findings", response_model=List[AuditFindingRead])
async def list_findings(
    plan_id: uuid.UUID,
    status_filter: Optional[str] = Query(None, alias="status"),
    severity: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(AuditFinding).where(AuditFinding.plan_id == plan_id).order_by(AuditFinding.created_at.desc())
    if status_filter:
        query = query.where(AuditFinding.status == status_filter)
    if severity:
        query = query.where(AuditFinding.severity == severity)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/audits/{plan_id}/findings", response_model=AuditFindingRead, status_code=status.HTTP_201_CREATED)
async def create_finding(plan_id: uuid.UUID, body: AuditFindingCreate, db: AsyncSession = Depends(get_db)):
    plan = (await db.execute(select(AuditPlan).where(AuditPlan.id == plan_id))).scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Audit plan not found")
    finding = AuditFinding(**{**body.model_dump(), "plan_id": plan_id})
    db.add(finding)
    await db.commit()
    await db.refresh(finding)
    return finding


@router.put("/audits/{plan_id}/findings/{finding_id}", response_model=AuditFindingRead)
async def update_finding(plan_id: uuid.UUID, finding_id: uuid.UUID, body: AuditFindingUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AuditFinding).where(AuditFinding.id == finding_id, AuditFinding.plan_id == plan_id)
    )
    finding = result.scalar_one_or_none()
    if not finding:
        raise HTTPException(status_code=404, detail="Audit finding not found")

    # Auto-set closed_at when transitioning to Closed
    if body.status == "Closed" and finding.closed_at is None:
        finding.closed_at = datetime.now(timezone.utc)

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(finding, field, value)
    await db.commit()
    await db.refresh(finding)
    return finding


@router.delete("/audits/{plan_id}/findings/{finding_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_finding(plan_id: uuid.UUID, finding_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(AuditFinding).where(AuditFinding.id == finding_id, AuditFinding.plan_id == plan_id)
    )
    finding = result.scalar_one_or_none()
    if not finding:
        raise HTTPException(status_code=404, detail="Audit finding not found")
    await db.delete(finding)
    await db.commit()
