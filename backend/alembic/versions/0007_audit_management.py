"""audit management

Revision ID: 0007
Revises: 0006
Create Date: 2026-05-26
"""
from alembic import op
import sqlalchemy as sa

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "audit_plans",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("scope", sa.Text(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="Draft"),
        sa.Column("audit_start", sa.Date(), nullable=True),
        sa.Column("audit_end", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "audit_items",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("plan_id", sa.Uuid(as_uuid=True), sa.ForeignKey("audit_plans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("control_id", sa.Uuid(as_uuid=True), sa.ForeignKey("controls.id", ondelete="SET NULL"), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("test_result", sa.String(50), nullable=False, server_default="Not Tested"),
        sa.Column("notes", sa.Text(), nullable=True),
    )
    op.create_index("ix_audit_items_plan_id", "audit_items", ["plan_id"])
    op.create_index("ix_audit_items_control_id", "audit_items", ["control_id"])
    op.create_table(
        "audit_findings",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("plan_id", sa.Uuid(as_uuid=True), sa.ForeignKey("audit_plans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="Open"),
        sa.Column("owner", sa.String(255), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_audit_findings_plan_id", "audit_findings", ["plan_id"])


def downgrade() -> None:
    op.drop_index("ix_audit_findings_plan_id", table_name="audit_findings")
    op.drop_table("audit_findings")
    op.drop_index("ix_audit_items_control_id", table_name="audit_items")
    op.drop_index("ix_audit_items_plan_id", table_name="audit_items")
    op.drop_table("audit_items")
    op.drop_table("audit_plans")
