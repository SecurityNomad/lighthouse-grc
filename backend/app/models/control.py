import re
import uuid
from sqlalchemy import String, Text, ForeignKey, Uuid, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


def ref_sort_key(ref: str) -> list:
    """Natural order for control refs: CIS-2 before CIS-10, 5.2 before 5.10.

    re.split with a capture group alternates text/number, so positions always
    compare like with like.
    """
    return [int(p) if p.isdigit() else p for p in re.split(r"(\d+)", ref)]


class Framework(Base):
    __tablename__ = "frameworks"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    controls: Mapped[list["Control"]] = relationship(
        "Control", back_populates="framework", order_by="Control.ref"
    )


class Control(Base):
    __tablename__ = "controls"
    __table_args__ = (UniqueConstraint("framework_id", "ref", name="uq_control_framework_ref"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    framework_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("frameworks.id", ondelete="CASCADE"), nullable=False
    )
    ref: Mapped[str] = mapped_column(String(50), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    framework: Mapped["Framework"] = relationship("Framework", back_populates="controls")
