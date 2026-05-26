import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.schemas.control import ControlRead
from app.schemas.risk import RiskRead


class RiskControlCreate(BaseModel):
    control_id: uuid.UUID
    notes: Optional[str] = None


class RiskControlRead(BaseModel):
    risk_id: uuid.UUID
    control_id: uuid.UUID
    notes: Optional[str] = None
    created_at: datetime
    model_config = {"from_attributes": True}


class ControlWithMappingRead(ControlRead):
    notes: Optional[str] = None
    mapped_at: datetime


class GapAnalysisRead(BaseModel):
    unmapped_risks: List[RiskRead]
    uncovered_controls: List[ControlRead]
