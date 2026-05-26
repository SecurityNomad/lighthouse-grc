import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, Text, DateTime, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class RiskControl(Base):
    __tablename__ = "risk_controls"

    risk_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("risks.id", ondelete="CASCADE"), primary_key=True
    )
    control_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("controls.id", ondelete="CASCADE"), primary_key=True
    )
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
