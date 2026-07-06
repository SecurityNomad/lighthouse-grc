import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator

from app.auth import VALID_ROLES


def _validate_role(value: Optional[str]) -> Optional[str]:
    if value is not None and value not in VALID_ROLES:
        raise ValueError(f"role must be one of {sorted(VALID_ROLES)}")
    return value


class UserBase(BaseModel):
    email: str
    full_name: str
    role: str = "analyst"

    @field_validator("role")
    @classmethod
    def _check_role(cls, v: str) -> str:
        return _validate_role(v)


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

    @field_validator("role")
    @classmethod
    def _check_role(cls, v: Optional[str]) -> Optional[str]:
        return _validate_role(v)


class UserRead(UserBase):
    id: uuid.UUID
    is_active: bool
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
