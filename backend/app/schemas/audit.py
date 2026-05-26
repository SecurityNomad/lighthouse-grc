import uuid
from datetime import date, datetime
from typing import Optional, List, Dict
from pydantic import BaseModel


class AuditPlanBase(BaseModel):
    title: str
    scope: Optional[str] = None
    status: str = "Draft"
    audit_start: Optional[date] = None
    audit_end: Optional[date] = None


class AuditPlanCreate(AuditPlanBase):
    pass


class AuditPlanUpdate(BaseModel):
    title: Optional[str] = None
    scope: Optional[str] = None
    status: Optional[str] = None
    audit_start: Optional[date] = None
    audit_end: Optional[date] = None


class AuditPlanRead(AuditPlanBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class AuditPlanSummary(AuditPlanRead):
    item_count: int = 0
    pass_count: int = 0
    fail_count: int = 0
    exception_count: int = 0
    not_tested_count: int = 0
    open_findings: int = 0


class AuditItemBase(BaseModel):
    plan_id: uuid.UUID
    control_id: Optional[uuid.UUID] = None
    description: str
    test_result: str = "Not Tested"
    notes: Optional[str] = None


class AuditItemCreate(AuditItemBase):
    pass


class AuditItemUpdate(BaseModel):
    control_id: Optional[uuid.UUID] = None
    description: Optional[str] = None
    test_result: Optional[str] = None
    notes: Optional[str] = None


class AuditItemRead(AuditItemBase):
    id: uuid.UUID
    model_config = {"from_attributes": True}


class AuditFindingBase(BaseModel):
    plan_id: uuid.UUID
    title: str
    description: str
    severity: str
    status: str = "Open"
    owner: Optional[str] = None
    due_date: Optional[date] = None
    closed_at: Optional[datetime] = None


class AuditFindingCreate(AuditFindingBase):
    pass


class AuditFindingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    owner: Optional[str] = None
    due_date: Optional[date] = None
    closed_at: Optional[datetime] = None


class AuditFindingRead(AuditFindingBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class AuditReportRead(BaseModel):
    plan: AuditPlanRead
    item_summary: Dict[str, int]
    findings: List[AuditFindingRead]
    finding_summary: Dict[str, int]
