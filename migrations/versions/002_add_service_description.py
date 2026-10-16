"""Add optional service description."""

from alembic import op
import sqlalchemy as sa


revision = "002_description"
down_revision = "001_baseline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("services", sa.Column("description", sa.String(255), nullable=True))


def downgrade() -> None:
    op.drop_column("services", "description")
