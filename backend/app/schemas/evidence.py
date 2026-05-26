import uuid
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class EvidenceBase(BaseModel):
    title: str
    description: Optional[str] = None
    control_id: Optional[uuid.UUID] = None
    expiry_date: Optional[date] = None


class EvidenceRead(EvidenceBase):
    id: uuid.UUID
    file_name: str
    file_size: int
    mime_type: str
    uploaded_at: datetime
    status: str
    model_config = {"from_attributes": True}


class EvidenceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    control_id: Optional[uuid.UUID] = None
    expiry_date: Optional[date] = None
