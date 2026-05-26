from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.risk import Risk
from app.models.control import Control
from app.models.control_mapping import RiskControl
from app.models.evidence import Evidence
from app.models.tprm import Vendor
from app.models.audit import AuditFinding, AuditPlan
from app.schemas.dashboard import DashboardRead, OpenRisksByImpact, VendorsByTier

router = APIRouter()


@router.get("/dashboard", response_model=DashboardRead)
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    # 1. Open risks by impact
    impact_result = await db.execute(
        select(Risk.impact, func.count(Risk.id))
        .where(Risk.status == "Open")
        .group_by(Risk.impact)
    )
    open_risks_by_impact = [
        OpenRisksByImpact(impact=impact, count=count)
        for impact, count in impact_result.all()
    ]

    # 2. High risks open (impact_score >= 4)
    high_result = await db.execute(
        select(func.count(Risk.id)).where(Risk.status == "Open", Risk.impact_score >= 4)
    )
    high_risks_open = high_result.scalar() or 0

    # 3. Control coverage % -- controls with at least one mapped risk
    total_controls_result = await db.execute(select(func.count(Control.id)))
    total_controls = total_controls_result.scalar() or 0

    mapped_controls_result = await db.execute(
        select(func.count(func.distinct(RiskControl.control_id)))
    )
    mapped_controls = mapped_controls_result.scalar() or 0
    control_coverage_pct = round((mapped_controls / total_controls * 100), 1) if total_controls > 0 else 0.0

    # 4. Evidence expiry counts (computed in Python from expiry_date)
    evidence_result = await db.execute(
        select(Evidence).where(Evidence.expiry_date.isnot(None))
    )
    evidence_items = evidence_result.scalars().all()
    evidence_expiring_soon = sum(1 for e in evidence_items if e.status == "Expiring")
    evidence_expired = sum(1 for e in evidence_items if e.status == "Expired")

    # 5. Vendors by tier
    tier_result = await db.execute(
        select(Vendor.tier, func.count(Vendor.id))
        .where(Vendor.status == "Active")
        .group_by(Vendor.tier)
        .order_by(Vendor.tier)
    )
    vendors_by_tier = [VendorsByTier(tier=tier, count=count) for tier, count in tier_result.all()]

    # 6. Vendors under review
    under_review_result = await db.execute(
        select(func.count(Vendor.id)).where(Vendor.status == "Under Review")
    )
    vendors_under_review = under_review_result.scalar() or 0

    # 7. Open findings
    findings_result = await db.execute(
        select(func.count(AuditFinding.id)).where(
            AuditFinding.status.in_(["Open", "In Remediation"])
        )
    )
    open_findings = findings_result.scalar() or 0

    # 8. Active audits
    audits_result = await db.execute(
        select(func.count(AuditPlan.id)).where(AuditPlan.status == "Active")
    )
    audits_active = audits_result.scalar() or 0

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
