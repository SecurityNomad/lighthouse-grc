import uuid
from datetime import date
from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict

ImplementationStatus = Literal[
    "Implemented", "Partially Implemented", "Planned", "Not Implemented"
]


class SoAEntryUpdate(BaseModel):
    """Upsert payload for a single SoA row."""

    applicable: Optional[bool] = None
    justification: Optional[str] = None
    implementation_status: Optional[ImplementationStatus] = None
    owner: Optional[str] = None
    last_reviewed: Optional[date] = None


class SoARow(BaseModel):
    """One control plus the organisation's position on it.

    Controls with no applicability record yet are still returned, with
    `entry_id` null and defaults applied, so the SoA is complete by
    construction — ISO 27001 requires every Annex A control to be accounted for.
    """

    model_config = ConfigDict(from_attributes=True)

    control_id: uuid.UUID
    ref: str
    domain: str
    title: str
    description: Optional[str] = None

    entry_id: Optional[uuid.UUID] = None
    applicable: bool = True
    justification: Optional[str] = None
    implementation_status: ImplementationStatus = "Not Implemented"
    owner: Optional[str] = None
    last_reviewed: Optional[date] = None


class SoASummary(BaseModel):
    framework_slug: str
    framework_name: str
    total_controls: int
    assessed: int
    applicable: int
    excluded: int
    implemented: int
    partially_implemented: int
    planned: int
    not_implemented: int
    coverage_pct: float   # % of controls with an SoA entry recorded
    readiness_pct: float  # weighted implementation across applicable controls


class SoARead(BaseModel):
    summary: SoASummary
    rows: List[SoARow]
