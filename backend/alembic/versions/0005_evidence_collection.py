"""evidence collection

Revision ID: 0005
Revises: 0004
Create Date: 2026-05-26
"""
from alembic import op
import sqlalchemy as sa

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "evidence",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("control_id", sa.Uuid(as_uuid=True), sa.ForeignKey("controls.id", ondelete="SET NULL"), nullable=True),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_path", sa.String(1024), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("mime_type", sa.String(127), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("expiry_date", sa.Date(), nullable=True),
    )
    op.create_index("ix_evidence_control_id", "evidence", ["control_id"])


def downgrade() -> None:
    op.drop_index("ix_evidence_control_id", table_name="evidence")
    op.drop_table("evidence")
