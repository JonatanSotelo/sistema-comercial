from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "5f8d5e6a8b1c"
down_revision = ("310587ef6e56", "410587ef6e56")
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("clientes", sa.Column("cuit", sa.String(), nullable=True))
    op.create_index("ix_clientes_cuit", "clientes", ["cuit"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_clientes_cuit", table_name="clientes")
    op.drop_column("clientes", "cuit")
