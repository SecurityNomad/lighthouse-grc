import uuid
from datetime import date, datetime
from sqlalchemy import String, Text, Date, DateTime, JSON, Uuid, Integer, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

IMPACT_SCORE_MAP = {
    "Critical": 5, "High": 4, "Medium": 3, "Low": 2, "Negligible": 1
}
LIKELIHOOD_SCORE_MAP = {
    "Almost Certain": 5, "Likely": 4, "Possible": 3, "Unlikely": 2, "Rare": 1
}


class Risk(Base):
    __tablename__ = "risks"

    # Uuid (capital U) is SQLAlchemy 2's dialect-agnostic UUID type —
    # uses native UUID on Postgres, VARCHAR(36) on SQLite.
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
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
    # JSON works on both Postgres and SQLite (used in tests).
    # Stores a list of tag strings, e.g. ["cloud", "access-control"].
    tags: Mapped[list[str] | None] = mapped_column(JSON)
    review_date: Mapped[date | None] = mapped_column(Date)

    # Integer scoring — auto-derived from string fields in the router
    likelihood_score: Mapped[int] = mapped_column(Integer(), nullable=False, default=3)
    impact_score: Mapped[int] = mapped_column(Integer(), nullable=False, default=3)
    risk_score: Mapped[int] = mapped_column(Integer(), nullable=False, default=9)

    # Residual risk (populated post-treatment)
    residual_likelihood_score: Mapped[int | None] = mapped_column(Integer())
    residual_impact_score: Mapped[int | None] = mapped_column(Integer())
    residual_risk_score: Mapped[int | None] = mapped_column(Integer())

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
