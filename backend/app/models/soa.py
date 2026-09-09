import uuid
from datetime import date, datetime
from sqlalchemy import String, Text, Boolean, Date, DateTime, ForeignKey, Uuid, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

# Implementation maturity for an applicable control. Kept as strings for the
# same reason as the rest of the platform's enum-like fields — readable in the
# database, no migration needed to add a value.
IMPLEMENTATION_STATUSES = (
    "Implemented",
    "Partially Implemented",
    "Planned",
    "Not Implemented",
)

# Weighting used for the readiness percentage. A partially implemented control
# earns half credit; anything else earns none.
READINESS_WEIGHTS = {
    "Implemented": 1.0,
    "Partially Implemented": 0.5,
    "Planned": 0.0,
    "Not Implemented": 0.0,
}


class ControlApplicability(Base):
    """A Statement of Applicability entry — one per control, per client.

    The control library itself stays framework-defined and read-only (ADR-001:
    frameworks are YAML configuration, not application logic). This table holds
    the *organisation's position* on each control: whether it applies, why, and
    how far implementation has progressed.

    Applies to any framework, not just ISO 27001 — the same shape drives the
    ISO Annex A SoA and the SOC 2 Trust Services Criteria readiness view.
    """

    __tablename__ = "control_applicability"
    __table_args__ = (
        UniqueConstraint("control_id", "client_id", name="uq_soa_control_client"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    control_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("controls.id", ondelete="CASCADE"), nullable=False
    )
    client_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("clients.id", ondelete="SET NULL"), nullable=True
    )

    # ISO 27001 requires the SoA to record both inclusion/exclusion and the
    # reasoning behind it, so justification is meaningful for both cases.
    applicable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    justification: Mapped[str | None] = mapped_column(Text)
    implementation_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="Not Implemented"
    )
    owner: Mapped[str | None] = mapped_column(String(255))
    last_reviewed: Mapped[date | None] = mapped_column(Date)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    control: Mapped["Control"] = relationship("Control")  # noqa: F821

    @property
    def readiness_weight(self) -> float:
        """Contribution to a readiness percentage. Excluded controls score 0."""
        if not self.applicable:
            return 0.0
        return READINESS_WEIGHTS.get(self.implementation_status, 0.0)
