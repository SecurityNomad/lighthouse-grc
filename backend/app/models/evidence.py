import uuid
from datetime import date, datetime, timedelta
from sqlalchemy import String, Text, Integer, Date, DateTime, ForeignKey, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    control_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("controls.id", ondelete="SET NULL"), nullable=True
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer(), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(127), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expiry_date: Mapped[date | None] = mapped_column(Date)

    @property
    def status(self) -> str:
        if self.expiry_date is None:
            return "Current"
        today = date.today()
        if self.expiry_date < today:
            return "Expired"
        if self.expiry_date <= today + timedelta(days=30):
            return "Expiring"
        return "Current"
