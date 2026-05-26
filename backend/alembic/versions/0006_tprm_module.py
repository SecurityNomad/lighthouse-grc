"""tprm module

Revision ID: 0006
Revises: 0005
Create Date: 2026-05-26
"""
from alembic import op
import sqlalchemy as sa

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "vendors",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("website", sa.String(512), nullable=True),
        sa.Column("tier", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("status", sa.String(50), nullable=False, server_default="Active"),
        sa.Column("contact_name", sa.String(255), nullable=True),
        sa.Column("contact_email", sa.String(255), nullable=True),
        sa.Column("contract_start", sa.Date(), nullable=True),
        sa.Column("contract_end", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "vendor_questions",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("ref", sa.String(10), nullable=False, unique=True),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("question_type", sa.String(30), nullable=False),
        sa.Column("max_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("weight", sa.Float(), nullable=False, server_default="1.0"),
    )
    op.create_table(
        "vendor_assessments",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("vendor_id", sa.Uuid(as_uuid=True), sa.ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="Draft"),
        sa.Column("overall_score", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_vendor_assessments_vendor_id", "vendor_assessments", ["vendor_id"])
    op.create_table(
        "vendor_answers",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("assessment_id", sa.Uuid(as_uuid=True), sa.ForeignKey("vendor_assessments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question_id", sa.Uuid(as_uuid=True), sa.ForeignKey("vendor_questions.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("text_response", sa.Text(), nullable=True),
        sa.UniqueConstraint("assessment_id", "question_id", name="uq_vendor_answer_assessment_question"),
    )
    op.create_index("ix_vendor_answers_assessment_id", "vendor_answers", ["assessment_id"])


def downgrade() -> None:
    op.drop_index("ix_vendor_answers_assessment_id", table_name="vendor_answers")
    op.drop_table("vendor_answers")
    op.drop_index("ix_vendor_assessments_vendor_id", table_name="vendor_assessments")
    op.drop_table("vendor_assessments")
    op.drop_table("vendor_questions")
    op.drop_table("vendors")
