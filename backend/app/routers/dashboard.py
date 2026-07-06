import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.risk import Risk
from app.models.control_mapping import RiskControl
from app.models.evidence import Evidence
from app.models.tprm import Vendor
from app.models.audit import AuditFinding, AuditPlan
from app.schemas.dashboard import DashboardRead, OpenRisksByImpact, VendorsByTier

router = APIRouter()


@router.get("/dashboard", response_model=DashboardRead)
async def get_dashboard(
    client_id: Optional[uuid.UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    # 1. Open risks by impact
    impact_query = (
        select(Risk.impact, func.count(Risk.id))
        .where(Risk.status == "Open")
        .group_by(Risk.impact)
    )
    if client_id:
        impact_query = impact_query.where(Risk.client_id == client_id)
    impact_result = await db.execute(impact_query)
    open_risks_by_impact = [
        OpenRisksByImpact(impact=impact, count=count)
        for impact, count in impact_result.all()
    ]

    # 2. High risks open (impact_score >= 4)
    high_query = select(func.count(Risk.id)).where(
        Risk.status == "Open", Risk.impact_score >= 4
    )
    if client_id:
        high_query = high_query.where(Risk.client_id == client_id)
    high_risks_open = (await db.execute(high_query)).scalar() or 0

    # 3. Control coverage % -- risks with at least one control mapped / total active risks
    total_risks_query = select(func.count(Risk.id)).where(
        Risk.status.notin_(["Closed", "Accepted"])
    )
    if client_id:
        total_risks_query = total_risks_query.where(Risk.client_id == client_id)
    total_active_risks = (await db.execute(total_risks_query)).scalar() or 0

    # Count distinct risks that have a control mapped; join to Risk so the
    # coverage figure respects the selected client.
    covered_query = select(func.count(func.distinct(RiskControl.risk_id))).select_from(
        RiskControl
    ).join(Risk, Risk.id == RiskControl.risk_id)
    if client_id:
        covered_query = covered_query.where(Risk.client_id == client_id)
    covered_risks = (await db.execute(covered_query)).scalar() or 0
    control_coverage_pct = round((covered_risks / total_active_risks * 100), 1) if total_active_risks > 0 else 0.0

    # 4. Evidence expiry counts (computed in Python from expiry_date)
    evidence_query = select(Evidence).where(Evidence.expiry_date.isnot(None))
    if client_id:
        evidence_query = evidence_query.where(Evidence.client_id == client_id)
    evidence_items = (await db.execute(evidence_query)).scalars().all()
    evidence_expiring_soon = sum(1 for e in evidence_items if e.status == "Expiring")
    evidence_expired = sum(1 for e in evidence_items if e.status == "Expired")

    # 5. Vendors by tier (all non-offboarded)
    tier_query = (
        select(Vendor.tier, func.count(Vendor.id))
        .where(Vendor.status != "Offboarded")
        .group_by(Vendor.tier)
        .order_by(Vendor.tier)
    )
    if client_id:
        tier_query = tier_query.where(Vendor.client_id == client_id)
    tier_result = await db.execute(tier_query)
    vendors_by_tier = [VendorsByTier(tier=tier, count=count) for tier, count in tier_result.all()]

    # 6. Vendors under review
    under_review_query = select(func.count(Vendor.id)).where(
        Vendor.status == "Under Review"
    )
    if client_id:
        under_review_query = under_review_query.where(Vendor.client_id == client_id)
    vendors_under_review = (await db.execute(under_review_query)).scalar() or 0

    # 7. Open findings (scoped via the finding's parent audit plan)
    findings_query = select(func.count(AuditFinding.id)).where(
        AuditFinding.status.in_(["Open", "In Remediation"])
    )
    if client_id:
        findings_query = findings_query.join(
            AuditPlan, AuditPlan.id == AuditFinding.plan_id
        ).where(AuditPlan.client_id == client_id)
    open_findings = (await db.execute(findings_query)).scalar() or 0

    # 8. Active audits
    audits_query = select(func.count(AuditPlan.id)).where(AuditPlan.status == "Active")
    if client_id:
        audits_query = audits_query.where(AuditPlan.client_id == client_id)
    audits_active = (await db.execute(audits_query)).scalar() or 0

    return DashboardRead(
        open_risks_by_impact=open_risks_by_impact,
        high_risks_open=high_risks_open,
        control_coverage_pct=control_coverage_pct,
        evidence_expiring_soon=evidence_expiring_soon,
        evidence_expired=evidence_expired,
        vendors_by_tier=vendors_by_tier,
        vendors_under_review=vendors_under_review,
        open_findings=open_findings,
        audits_active=audits_active,
    )
