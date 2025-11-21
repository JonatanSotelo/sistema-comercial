"""add_stock_reservations

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2025-11-21 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6g7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Crear tabla stock_reservations
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS stock_reservations (
            id SERIAL PRIMARY KEY,
            pedido_id INTEGER NOT NULL REFERENCES pedidos(id) ON DELETE CASCADE,
            pedido_item_id INTEGER NOT NULL REFERENCES pedido_items(id) ON DELETE CASCADE,
            producto_id INTEGER NOT NULL REFERENCES productos(id) ON DELETE RESTRICT,
            cantidad INTEGER NOT NULL CHECK (cantidad >= 1),
            estado VARCHAR NOT NULL DEFAULT 'RESERVADA',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        )
        """
    )
    
    # Crear índices
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_stock_reservations_id ON stock_reservations(id)
        """
    )
    
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_stock_reservations_pedido_id ON stock_reservations(pedido_id)
        """
    )
    
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_stock_reservations_pedido_item_id ON stock_reservations(pedido_item_id)
        """
    )
    
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_stock_reservations_producto_id ON stock_reservations(producto_id)
        """
    )
    
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_stock_reservations_estado ON stock_reservations(estado)
        """
    )
    
    # Índice compuesto para consultas de disponibilidad
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_stock_reservations_producto_estado 
        ON stock_reservations(producto_id, estado)
        """
    )
    
    # Índice único parcial: solo una reserva activa por pedido_item
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS ix_stock_reservations_pedido_item_active
        ON stock_reservations(pedido_item_id)
        WHERE estado = 'RESERVADA'
        """
    )


def downgrade() -> None:
    # Eliminar índices
    op.execute("DROP INDEX IF EXISTS ix_stock_reservations_pedido_item_active")
    op.execute("DROP INDEX IF EXISTS ix_stock_reservations_producto_estado")
    op.execute("DROP INDEX IF EXISTS ix_stock_reservations_estado")
    op.execute("DROP INDEX IF EXISTS ix_stock_reservations_producto_id")
    op.execute("DROP INDEX IF EXISTS ix_stock_reservations_pedido_item_id")
    op.execute("DROP INDEX IF EXISTS ix_stock_reservations_pedido_id")
    op.execute("DROP INDEX IF EXISTS ix_stock_reservations_id")
    
    # Eliminar tabla
    op.execute("DROP TABLE IF EXISTS stock_reservations")

