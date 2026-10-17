"""Add object storage metadata."""

from alembic import op
import sqlalchemy as sa


revision = "005_objects"
down_revision = "004_integrity"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "stored_objects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("original_name", sa.String(255), nullable=False),
        sa.Column("storage_name", sa.String(255), nullable=False),
        sa.Column("content_type", sa.String(100), nullable=True),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("storage_path", sa.String(500), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("storage_name", name="uq_stored_objects_storage_name"),
    )


def downgrade() -> None:
    op.drop_table("stored_objects")
