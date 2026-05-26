"""control mapping

Revision ID: 0004
Revises: 0003
Create Date: 2026-05-26
"""
from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "risk_controls",
        sa.Column("risk_id", sa.Uuid(as_uuid=True), sa.ForeignKey("risks.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("control_id", sa.Uuid(as_uuid=True), sa.ForeignKey("controls.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_risk_controls_risk_id", "risk_controls", ["risk_id"])
    op.create_index("ix_risk_controls_control_id", "risk_controls", ["control_id"])


def downgrade() -> None:
    op.drop_index("ix_risk_controls_control_id", table_name="risk_controls")
    op.drop_index("ix_risk_controls_risk_id", table_name="risk_controls")
    op.drop_table("risk_controls")
