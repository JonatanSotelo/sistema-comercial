"""add_pedidos_module

Revision ID: a1b2c3d4e5f6
Revises: 410587ef6e56
Create Date: 2025-11-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '410587ef6e56'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Crear tabla pedidos
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS pedidos (
            id SERIAL PRIMARY KEY,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            cliente_id INTEGER NULL REFERENCES clientes(id) ON DELETE RESTRICT,
            estado VARCHAR NOT NULL DEFAULT 'NUEVO',
            origen VARCHAR NOT NULL DEFAULT 'MANUAL',
            telefono VARCHAR NULL,
            nota TEXT NULL,
            total NUMERIC(12,2) NOT NULL DEFAULT 0,
            created_by INTEGER NULL REFERENCES users(id) ON DELETE SET NULL,
            external_ref VARCHAR NULL
        )
        """
    )
    
    # Crear índices en pedidos
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_pedidos_id ON pedidos(id)
        """
    )
    
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_pedidos_estado_created_at ON pedidos(estado, created_at)
        """
    )
    
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_pedidos_cliente_id_created_at ON pedidos(cliente_id, created_at)
        """
    )
    
    # Crear tabla pedido_items
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS pedido_items (
            id SERIAL PRIMARY KEY,
            pedido_id INTEGER NOT NULL REFERENCES pedidos(id) ON DELETE CASCADE,
            producto_id INTEGER NOT NULL REFERENCES productos(id) ON DELETE RESTRICT,
            cantidad INTEGER NOT NULL,
            precio_unitario NUMERIC(12,2) NOT NULL,
            subtotal NUMERIC(12,2) NOT NULL
        )
        """
    )
    
    # Crear índices en pedido_items
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_pedido_items_id ON pedido_items(id)
        """
    )
    
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_pedido_items_pedido_id ON pedido_items(pedido_id)
        """
    )
    
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_pedido_items_producto_id ON pedido_items(producto_id)
        """
    )
    
    # Agregar constraints
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'ck_pedido_items_cantidad_pos'
            ) THEN
                ALTER TABLE pedido_items
                ADD CONSTRAINT ck_pedido_items_cantidad_pos CHECK (cantidad >= 1);
            END IF;
        END
        $$
        """
    )
    
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'ck_pedido_items_precio_pos'
            ) THEN
                ALTER TABLE pedido_items
                ADD CONSTRAINT ck_pedido_items_precio_pos CHECK (precio_unitario >= 0);
            END IF;
        END
        $$
        """
    )


def downgrade() -> None:
    # Eliminar constraints
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'ck_pedido_items_precio_pos'
            ) THEN
                ALTER TABLE pedido_items DROP CONSTRAINT ck_pedido_items_precio_pos;
            END IF;
        END
        $$
        """
    )
    
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'ck_pedido_items_cantidad_pos'
            ) THEN
                ALTER TABLE pedido_items DROP CONSTRAINT ck_pedido_items_cantidad_pos;
            END IF;
        END
        $$
        """
    )
    
    # Eliminar índices
    op.execute("DROP INDEX IF EXISTS ix_pedido_items_producto_id")
    op.execute("DROP INDEX IF EXISTS ix_pedido_items_pedido_id")
    op.execute("DROP INDEX IF EXISTS ix_pedido_items_id")
    op.execute("DROP INDEX IF EXISTS ix_pedidos_cliente_id_created_at")
    op.execute("DROP INDEX IF EXISTS ix_pedidos_estado_created_at")
    op.execute("DROP INDEX IF EXISTS ix_pedidos_id")
    
    # Eliminar tablas
    op.execute("DROP TABLE IF EXISTS pedido_items")
    op.execute("DROP TABLE IF EXISTS pedidos")

