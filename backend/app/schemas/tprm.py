import uuid
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel


class VendorBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    website: Optional[str] = None
    tier: int = 3
    status: str = "Active"
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contract_start: Optional[date] = None
    contract_end: Optional[date] = None


class VendorCreate(VendorBase):
    pass


class VendorUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    website: Optional[str] = None
    tier: Optional[int] = None
    status: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contract_start: Optional[date] = None
    contract_end: Optional[date] = None


class VendorRead(VendorBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class VendorRiskRating(BaseModel):
    vendor_id: uuid.UUID
    vendor_name: str
    tier: int
    overall_score: Optional[float]
    risk_rating: str
    assessment_id: Optional[uuid.UUID]
    assessed_at: Optional[datetime]


class VendorQuestionRead(BaseModel):
    id: uuid.UUID
    ref: str
    category: str
    text: str
    question_type: str
    max_score: int
    weight: float
    model_config = {"from_attributes": True}


class VendorAssessmentCreate(BaseModel):
    vendor_id: uuid.UUID


class VendorAssessmentUpdate(BaseModel):
    status: Optional[str] = None


class VendorAssessmentRead(BaseModel):
    id: uuid.UUID
    vendor_id: uuid.UUID
    status: str
    overall_score: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class VendorAnswerUpsert(BaseModel):
    question_id: uuid.UUID
    score: Optional[int] = None
    text_response: Optional[str] = None


class VendorAnswerRead(BaseModel):
    id: uuid.UUID
    assessment_id: uuid.UUID
    question_id: uuid.UUID
    score: Optional[int] = None
    text_response: Optional[str] = None
    model_config = {"from_attributes": True}


class VendorAssessmentWithAnswers(VendorAssessmentRead):
    answers: List[VendorAnswerRead] = []
