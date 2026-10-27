"""Hash existing passwords while renaming the column.

Revision ID: 008_password_hash
Revises: 007_access
"""
from alembic import op
import sqlalchemy as sa
from pwdlib import PasswordHash


revision = "008_password_hash"
down_revision = "007_access"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "users", "password", new_column_name="password_hash",
        existing_type=sa.String(255), existing_nullable=False,
    )
    connection = op.get_bind()
    users = sa.table("users", sa.column("id", sa.Integer), sa.column("password_hash", sa.String))
    hasher = PasswordHash.recommended()
    for row in connection.execute(sa.select(users.c.id, users.c.password_hash)):
        if not row.password_hash.startswith("$argon2"):
            connection.execute(
                users.update().where(users.c.id == row.id).values(
                    password_hash=hasher.hash(row.password_hash)
                )
            )


def downgrade() -> None:
    raise RuntimeError("Password hashes cannot be converted back to plaintext")
