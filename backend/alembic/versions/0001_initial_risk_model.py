"""initial risk model

Revision ID: 0001
Revises:
Create Date: 2026-05-19

"""
from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'risks',
        sa.Column('id', sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('threat', sa.String(255), nullable=True),
        sa.Column('scenario', sa.Text(), nullable=True),
        sa.Column('impact', sa.String(50), nullable=False, server_default='Medium'),
        sa.Column('likelihood', sa.String(50), nullable=False, server_default='Possible'),
        sa.Column('treatment', sa.String(50), nullable=False, server_default='Mitigate'),
        sa.Column('treatment_notes', sa.Text(), nullable=True),
        sa.Column('owner', sa.String(255), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='Open'),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('review_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('risks')
