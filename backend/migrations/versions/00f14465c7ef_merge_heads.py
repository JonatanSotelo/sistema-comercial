"""merge heads

Revision ID: 00f14465c7ef
Revises: b2c3d4e5f6g7, c5e5b9f2d3c5
Create Date: 2025-11-21 12:59:43.000364

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '00f14465c7ef'
down_revision: Union[str, Sequence[str], None] = ('b2c3d4e5f6g7', 'c5e5b9f2d3c5')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
