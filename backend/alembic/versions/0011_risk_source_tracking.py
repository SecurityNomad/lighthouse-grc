"""add source/external_id provenance columns to risks

Supports Phase 3 plugins (AWS Config, MISP) that import findings as risks.
`source` records the origin ("Manual" or a plugin name); `external_id` is the
source system's identifier, used to deduplicate re-imports.

Revision ID: 0011
Revises: 0010
Create Date: 2026-07-06
"""
from alembic import op
import sqlalchemy as sa

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "risks",
        sa.Column("source", sa.String(length=50), nullable=False, server_default="Manual"),
    )
    op.add_column("risks", sa.Column("external_id", sa.String(length=255), nullable=True))
    # Fast lookup for dedup checks by (source, external_id).
    op.create_index("ix_risks_source_external_id", "risks", ["source", "external_id"])


def downgrade() -> None:
    op.drop_index("ix_risks_source_external_id", table_name="risks")
    op.drop_column("risks", "external_id")
    op.drop_column("risks", "source")
