"""add audit_logs

Revision ID: bb1e66f2e0bf
Revises: 5cb3f141eb55
Create Date: 2025-08-12 17:53:03.220432

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bb1e66f2e0bf'
down_revision: Union[str, Sequence[str], None] = '5cb3f141eb55'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
