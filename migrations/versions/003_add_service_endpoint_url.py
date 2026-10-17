"""Add optional endpoint URL."""

from alembic import op
import sqlalchemy as sa


revision = "003_endpoint"
down_revision = "002_description"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("services", sa.Column("endpoint_url", sa.String(255), nullable=True))


def downgrade() -> None:
    op.drop_column("services", "endpoint_url")
