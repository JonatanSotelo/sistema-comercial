"""create users table

Revision ID: cb43e5ad5571
Revises: aa79513f596d
Create Date: 2025-08-30 18:07:18.923069

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cb43e5ad5571'
down_revision: Union[str, Sequence[str], None] = 'aa79513f596d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="consulta"),
    )
    op.create_unique_constraint("uq_users_username", "users", ["username"])
    op.create_index("ix_users_username", "users", ["username"])

def downgrade():
    op.drop_index("ix_users_username", table_name="users")
    op.drop_constraint("uq_users_username", "users", type_="unique")
    op.drop_table("users")