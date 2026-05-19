import uuid
from datetime import date, datetime
from sqlalchemy import String, Text, Date, DateTime, func, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Risk(Base):
    __tablename__ = "risks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    threat: Mapped[str | None] = mapped_column(String(255))
    scenario: Mapped[str | None] = mapped_column(Text)
    impact: Mapped[str] = mapped_column(
        String(50), nullable=False, default="Medium"
    )  # Critical / High / Medium / Low
    likelihood: Mapped[str] = mapped_column(
        String(50), nullable=False, default="Possible"
    )  # Likely / Possible / Unlikely / Rare
    treatment: Mapped[str] = mapped_column(
        String(50), nullable=False, default="Mitigate"
    )  # Accept / Mitigate / Transfer / Avoid
    treatment_notes: Mapped[str | None] = mapped_column(Text)
    owner: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="Open"
    )  # Open / In Treatment / Closed / Accepted
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    review_date: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
