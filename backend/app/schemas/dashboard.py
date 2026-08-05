from typing import List
from pydantic import BaseModel


class OpenRisksByImpact(BaseModel):
    impact: str
    count: int


class VendorsByTier(BaseModel):
    tier: int
    count: int


class DashboardRead(BaseModel):
    open_risks_by_impact: List[OpenRisksByImpact]
    high_risks_open: int
    control_coverage_pct: float
    evidence_expiring_soon: int
    evidence_expired: int
    vendors_by_tier: List[VendorsByTier]
    vendors_under_review: int
    open_findings: int
    audits_active: int
    # SOC 2 readiness (WBS 1.5.3) — weighted implementation across the applicable
    # Common Criteria. cc_assessed/cc_total evidence how much of CC is covered.
    soc2_readiness_pct: float = 0.0
    soc2_cc_assessed: int = 0
    soc2_cc_total: int = 0
    # ISO 27001 Statement of Applicability progress (WBS 1.5.2)
    iso_soa_coverage_pct: float = 0.0
    iso_soa_readiness_pct: float = 0.0
