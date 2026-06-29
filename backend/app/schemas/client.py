import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ClientBase(BaseModel):
    name: str
    industry: str
    description: Optional[str] = None
    country: Optional[str] = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    country: Optional[str] = None


class ClientRead(ClientBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}
