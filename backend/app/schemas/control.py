import uuid
from typing import Optional
from pydantic import BaseModel


class FrameworkRead(BaseModel):
    id: uuid.UUID
    slug: str
    name: str
    version: str
    description: Optional[str] = None
    control_count: int = 0

    model_config = {"from_attributes": True}


class ControlRead(BaseModel):
    id: uuid.UUID
    framework_id: uuid.UUID
    ref: str
    domain: str
    title: str
    description: Optional[str] = None

    model_config = {"from_attributes": True}
