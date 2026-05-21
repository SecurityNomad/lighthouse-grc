"""control framework library

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-21

"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "frameworks",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("slug", sa.String(50), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("version", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
    )

    op.create_table(
        "controls",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column(
            "framework_id",
            sa.Uuid(as_uuid=True),
            sa.ForeignKey("frameworks.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("ref", sa.String(50), nullable=False),
        sa.Column("domain", sa.String(255), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.UniqueConstraint("framework_id", "ref", name="uq_control_framework_ref"),
    )
    op.create_index("ix_controls_framework_id", "controls", ["framework_id"])


def downgrade() -> None:
    op.drop_index("ix_controls_framework_id", table_name="controls")
    op.drop_table("controls")
    op.drop_table("frameworks")
