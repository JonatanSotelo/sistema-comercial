from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "8d9c7c3f4a1b"
down_revision = "5f8d5e6a8b1c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("proveedores", sa.Column("telefono", sa.String(), nullable=True))
    op.add_column("proveedores", sa.Column("cuit", sa.String(), nullable=True))
    op.create_index("ix_proveedores_cuit", "proveedores", ["cuit"], unique=False)
    op.add_column("proveedores", sa.Column("direccion", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("proveedores", "direccion")
    op.drop_index("ix_proveedores_cuit", table_name="proveedores")
    op.drop_column("proveedores", "cuit")
    op.drop_column("proveedores", "telefono")
