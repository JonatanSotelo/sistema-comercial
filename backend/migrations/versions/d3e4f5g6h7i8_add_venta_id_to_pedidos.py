"""add_venta_id_to_pedidos

Revision ID: d3e4f5g6h7i8
Revises: c1d2e3f4g5h6
Create Date: 2025-11-21 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd3e4f5g6h7i8'
down_revision = 'c1d2e3f4g5h6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Agregar columna venta_id a pedidos
    op.add_column('pedidos', sa.Column('venta_id', sa.Integer(), nullable=True))
    
    # Agregar FK constraint
    op.create_foreign_key(
        'fk_pedidos_venta_id__ventas_id',
        'pedidos', 'ventas',
        ['venta_id'], ['id'],
        ondelete='SET NULL'
    )
    
    # Agregar índice
    op.create_index('ix_pedidos_venta_id', 'pedidos', ['venta_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_pedidos_venta_id', table_name='pedidos')
    op.drop_constraint('fk_pedidos_venta_id__ventas_id', 'pedidos', type_='foreignkey')
    op.drop_column('pedidos', 'venta_id')

