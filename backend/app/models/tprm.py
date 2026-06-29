import uuid
from datetime import date, datetime
from sqlalchemy import String, Text, Integer, Float, Date, DateTime, ForeignKey, Uuid, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Vendor(Base):
    __tablename__ = "vendors"
    __table_args__ = (UniqueConstraint("name", "client_id", name="uq_vendor_name_client"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("clients.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    website: Mapped[str | None] = mapped_column(String(512))
    tier: Mapped[int] = mapped_column(Integer(), nullable=False, default=3)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Active")
    contact_name: Mapped[str | None] = mapped_column(String(255))
    contact_email: Mapped[str | None] = mapped_column(String(255))
    contract_start: Mapped[date | None] = mapped_column(Date)
    contract_end: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    assessments: Mapped[list["VendorAssessment"]] = relationship("VendorAssessment", back_populates="vendor")


class VendorQuestion(Base):
    __tablename__ = "vendor_questions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ref: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String(30), nullable=False)
    max_score: Mapped[int] = mapped_column(Integer(), nullable=False, default=0)
    weight: Mapped[float] = mapped_column(Float(), nullable=False, default=1.0)


class VendorAssessment(Base):
    __tablename__ = "vendor_assessments"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Draft")
    overall_score: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    vendor: Mapped["Vendor"] = relationship("Vendor", back_populates="assessments")
    answers: Mapped[list["VendorAnswer"]] = relationship("VendorAnswer", back_populates="assessment")


class VendorAnswer(Base):
    __tablename__ = "vendor_answers"
    __table_args__ = (UniqueConstraint("assessment_id", "question_id", name="uq_vendor_answer_assessment_question"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("vendor_assessments.id", ondelete="CASCADE"), nullable=False
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("vendor_questions.id", ondelete="RESTRICT"), nullable=False
    )
    score: Mapped[int | None] = mapped_column(Integer)
    text_response: Mapped[str | None] = mapped_column(Text)

    assessment: Mapped["VendorAssessment"] = relationship("VendorAssessment", back_populates="answers")
    question: Mapped["VendorQuestion"] = relationship("VendorQuestion")
