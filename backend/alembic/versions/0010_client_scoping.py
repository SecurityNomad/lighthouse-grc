"""add client_id scoping to data tables

Revision ID: 0010
Revises: 0009
Create Date: 2026-06-29
"""
from alembic import op
import sqlalchemy as sa

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("risks", sa.Column("client_id", sa.Uuid(as_uuid=True), sa.ForeignKey("clients.id", ondelete="SET NULL"), nullable=True))
    op.create_index("ix_risks_client_id", "risks", ["client_id"])

    op.add_column("evidence", sa.Column("client_id", sa.Uuid(as_uuid=True), sa.ForeignKey("clients.id", ondelete="SET NULL"), nullable=True))
    op.create_index("ix_evidence_client_id", "evidence", ["client_id"])

    op.add_column("audit_plans", sa.Column("client_id", sa.Uuid(as_uuid=True), sa.ForeignKey("clients.id", ondelete="SET NULL"), nullable=True))
    op.create_index("ix_audit_plans_client_id", "audit_plans", ["client_id"])

    # vendors: drop old unique constraint on name, add client_id, add composite unique
    op.drop_index("ix_vendors_name", table_name="vendors", if_exists=True)
    # Drop unique constraint — SQLite doesn't support DROP CONSTRAINT, so we recreate the table
    # For PostgreSQL we'd use: op.drop_constraint("vendors_name_key", "vendors", type_="unique")
    # Alembic batch mode handles SQLite
    with op.batch_alter_table("vendors") as batch_op:
        batch_op.add_column(sa.Column("client_id", sa.Uuid(as_uuid=True), sa.ForeignKey("clients.id", ondelete="SET NULL"), nullable=True))
        try:
            batch_op.drop_constraint("vendors_name_key", type_="unique")
        except Exception:
            pass
        batch_op.create_unique_constraint("uq_vendor_name_client", ["name", "client_id"])
    op.create_index("ix_vendors_client_id", "vendors", ["client_id"])


def downgrade() -> None:
    op.drop_index("ix_vendors_client_id", table_name="vendors")
    with op.batch_alter_table("vendors") as batch_op:
        batch_op.drop_constraint("uq_vendor_name_client", type_="unique")
        batch_op.drop_column("client_id")

    op.drop_index("ix_audit_plans_client_id", table_name="audit_plans")
    op.drop_column("audit_plans", "client_id")

    op.drop_index("ix_evidence_client_id", table_name="evidence")
    op.drop_column("evidence", "client_id")

    op.drop_index("ix_risks_client_id", table_name="risks")
    op.drop_column("risks", "client_id")
