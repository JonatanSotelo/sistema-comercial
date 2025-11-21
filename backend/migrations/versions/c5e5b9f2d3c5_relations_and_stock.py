from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "c5e5b9f2d3c5"
down_revision = "8d9c7c3f4a1b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # productos.proveedor_id
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'productos' AND column_name = 'proveedor_id'
            ) THEN
                ALTER TABLE productos ADD COLUMN proveedor_id INTEGER NULL;
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
                SELECT 1 FROM pg_constraint WHERE conname = 'fk_productos_proveedor'
            ) THEN
                ALTER TABLE productos
                ADD CONSTRAINT fk_productos_proveedor
                FOREIGN KEY (proveedor_id) REFERENCES proveedores(id) ON DELETE SET NULL;
            END IF;
        END
        $$
        """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_productos_proveedor_id
        ON productos (proveedor_id)
        """
    )

    # CHECK stock >= 0
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'ck_productos_stock_nonnegative'
            ) THEN
                ALTER TABLE productos
                ADD CONSTRAINT ck_productos_stock_nonnegative CHECK (stock >= 0);
            END IF;
        END
        $$
        """
    )

    # ventas
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS ventas (
            id SERIAL PRIMARY KEY,
            fecha TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            cliente_id INTEGER NULL REFERENCES clientes(id) ON DELETE SET NULL,
            total NUMERIC(12,2) NOT NULL DEFAULT 0
        )
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS venta_items (
            id SERIAL PRIMARY KEY,
            venta_id INTEGER NOT NULL REFERENCES ventas(id) ON DELETE CASCADE,
            producto_id INTEGER NOT NULL REFERENCES productos(id) ON DELETE RESTRICT,
            cantidad INTEGER NOT NULL,
            precio_unitario NUMERIC(12,2) NOT NULL,
            subtotal NUMERIC(12,2) NOT NULL
        )
        """
    )

    op.execute("CREATE INDEX IF NOT EXISTS ix_venta_items_venta_id ON venta_items(venta_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_venta_items_producto_id ON venta_items(producto_id)")

    # compras
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS compras (
            id SERIAL PRIMARY KEY,
            fecha TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            proveedor_id INTEGER NOT NULL REFERENCES proveedores(id) ON DELETE RESTRICT,
            total NUMERIC(12,2) NOT NULL DEFAULT 0
        )
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS compra_items (
            id SERIAL PRIMARY KEY,
            compra_id INTEGER NOT NULL REFERENCES compras(id) ON DELETE CASCADE,
            producto_id INTEGER NOT NULL REFERENCES productos(id) ON DELETE RESTRICT,
            cantidad INTEGER NOT NULL,
            costo_unitario NUMERIC(12,2) NOT NULL,
            subtotal NUMERIC(12,2) NOT NULL
        )
        """
    )

    op.execute("CREATE INDEX IF NOT EXISTS ix_compra_items_compra_id ON compra_items(compra_id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_compra_items_producto_id ON compra_items(producto_id)")

    # cantidad >= 1 checks
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'ck_venta_items_cantidad_pos'
            ) THEN
                ALTER TABLE venta_items
                ADD CONSTRAINT ck_venta_items_cantidad_pos CHECK (cantidad >= 1);
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
                SELECT 1 FROM pg_constraint WHERE conname = 'ck_compra_items_cantidad_pos'
            ) THEN
                ALTER TABLE compra_items
                ADD CONSTRAINT ck_compra_items_cantidad_pos CHECK (cantidad >= 1);
            END IF;
        END
        $$
        """
    )


def downgrade() -> None:
    # eliminar check constraints
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'ck_compra_items_cantidad_pos'
            ) THEN
                ALTER TABLE compra_items DROP CONSTRAINT ck_compra_items_cantidad_pos;
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
                SELECT 1 FROM pg_constraint WHERE conname = 'ck_venta_items_cantidad_pos'
            ) THEN
                ALTER TABLE venta_items DROP CONSTRAINT ck_venta_items_cantidad_pos;
            END IF;
        END
        $$
        """
    )

    # no se eliminan tablas si ya existían previamente, solo dejamos estructura
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'fk_productos_proveedor'
            ) THEN
                ALTER TABLE productos DROP CONSTRAINT fk_productos_proveedor;
            END IF;
        END
        $$
        """
    )

    op.execute("DROP INDEX IF EXISTS ix_productos_proveedor_id")

    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'ck_productos_stock_nonnegative'
            ) THEN
                ALTER TABLE productos DROP CONSTRAINT ck_productos_stock_nonnegative;
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
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'productos' AND column_name = 'proveedor_id'
            ) THEN
                ALTER TABLE productos DROP COLUMN proveedor_id;
            END IF;
        END
        $$
        """
    )
