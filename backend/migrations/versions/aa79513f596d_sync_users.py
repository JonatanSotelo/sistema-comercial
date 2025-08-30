"""sync users

Revision ID: aa79513f596d
Revises: cac8bc67b8a7
Create Date: 2025-08-30 17:40:56.236396

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aa79513f596d'
down_revision: Union[str, Sequence[str], None] = 'cac8bc67b8a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
