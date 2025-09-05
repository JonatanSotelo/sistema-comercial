"""merge heads (audit_logs + usuarios)

Revision ID: cac8bc67b8a7
Revises: bb1e66f2e0bf, 815b9ee8b57a
Create Date: 2025-08-30 17:40:21.267285

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cac8bc67b8a7'
down_revision: Union[str, Sequence[str], None] = ('bb1e66f2e0bf', 'f30b2f7abe0e')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
