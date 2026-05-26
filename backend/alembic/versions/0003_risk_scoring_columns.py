"""risk scoring columns

Revision ID: 0003
Revises: 0002
Create Date: 2026-05-26
"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("risks", sa.Column("likelihood_score", sa.Integer(), nullable=False, server_default="3"))
    op.add_column("risks", sa.Column("impact_score", sa.Integer(), nullable=False, server_default="3"))
    op.add_column("risks", sa.Column("risk_score", sa.Integer(), nullable=False, server_default="9"))
    op.add_column("risks", sa.Column("residual_likelihood_score", sa.Integer(), nullable=True))
    op.add_column("risks", sa.Column("residual_impact_score", sa.Integer(), nullable=True))
    op.add_column("risks", sa.Column("residual_risk_score", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("risks", "residual_risk_score")
    op.drop_column("risks", "residual_impact_score")
    op.drop_column("risks", "residual_likelihood_score")
    op.drop_column("risks", "risk_score")
    op.drop_column("risks", "impact_score")
    op.drop_column("risks", "likelihood_score")
