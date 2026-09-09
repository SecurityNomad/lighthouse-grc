"""add control_applicability table (Statement of Applicability)

Supports WBS 1.5.2 (ISO 27001 SoA) and 1.5.3 (SOC 2 readiness). The control
library remains framework-defined and read-only; this table records the
organisation's position on each control — applicability, justification, and
implementation status — scoped per client.

Revision ID: 0012
Revises: 0011
Create Date: 2026-08-05
"""
from alembic import op
import sqlalchemy as sa

revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "control_applicability",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "control_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("controls.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "client_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("clients.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("applicable", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("justification", sa.Text(), nullable=True),
        sa.Column(
            "implementation_status",
            sa.String(length=50),
            nullable=False,
            server_default="Not Implemented",
        ),
        sa.Column("owner", sa.String(length=255), nullable=True),
        sa.Column("last_reviewed", sa.Date(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("control_id", "client_id", name="uq_soa_control_client"),
    )
    # The SoA view is always read framework-first for one client at a time.
    op.create_index(
        "ix_control_applicability_client_control",
        "control_applicability",
        ["client_id", "control_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_control_applicability_client_control", table_name="control_applicability"
    )
    op.drop_table("control_applicability")
