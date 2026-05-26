import uuid
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel


class RiskBase(BaseModel):
    title: str
    description: Optional[str] = None
    threat: Optional[str] = None
    scenario: Optional[str] = None
    impact: str = "Medium"
    likelihood: str = "Possible"
    treatment: str = "Mitigate"
    treatment_notes: Optional[str] = None
    owner: Optional[str] = None
    status: str = "Open"
    tags: Optional[List[str]] = None
    review_date: Optional[date] = None
    likelihood_score: int = 3
    impact_score: int = 3
    risk_score: int = 9
    residual_likelihood_score: Optional[int] = None
    residual_impact_score: Optional[int] = None
    residual_risk_score: Optional[int] = None


class RiskCreate(RiskBase):
    pass


class RiskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    threat: Optional[str] = None
    scenario: Optional[str] = None
    impact: Optional[str] = None
    likelihood: Optional[str] = None
    treatment: Optional[str] = None
    treatment_notes: Optional[str] = None
    owner: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    review_date: Optional[date] = None


class RiskRead(RiskBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
