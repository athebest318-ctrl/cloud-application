"""Add data integrity constraints and status history."""

from alembic import op
import sqlalchemy as sa


revision = "004_integrity"
down_revision = "003_endpoint"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("service_types", "name", existing_type=sa.String(50), nullable=False)
    op.create_unique_constraint("uq_service_types_name", "service_types", ["name"])
    op.create_check_constraint(
        "ck_service_types_name_not_empty",
        "service_types",
        "TRIM(name) <> ''",
    )
    op.alter_column("services", "name", existing_type=sa.String(100), nullable=False)
    op.alter_column("services", "type_id", existing_type=sa.Integer(), nullable=False)
    op.alter_column("services", "status", existing_type=sa.String(20), nullable=False)
    op.create_check_constraint(
        "ck_services_status",
        "services",
        "status IN ('running', 'maintenance', 'stopped')",
    )
    op.create_table(
        "service_status_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("service_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column(
            "changed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "status IN ('running', 'maintenance', 'stopped')",
            name="ck_service_status_history_status",
        ),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute(
        "INSERT INTO service_status_history (service_id, status) "
        "SELECT id, status FROM services"
    )


def downgrade() -> None:
    op.drop_table("service_status_history")
    op.drop_constraint("ck_services_status", "services", type_="check")
    op.alter_column("services", "status", existing_type=sa.String(20), nullable=True)
    op.alter_column("services", "type_id", existing_type=sa.Integer(), nullable=True)
    op.alter_column("services", "name", existing_type=sa.String(100), nullable=True)
    op.drop_constraint("ck_service_types_name_not_empty", "service_types", type_="check")
    op.drop_constraint("uq_service_types_name", "service_types", type_="unique")
    op.alter_column("service_types", "name", existing_type=sa.String(50), nullable=True)
