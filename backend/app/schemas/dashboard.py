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
