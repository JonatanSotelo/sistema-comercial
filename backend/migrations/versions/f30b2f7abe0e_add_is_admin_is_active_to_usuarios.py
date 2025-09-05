from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "f30b2f7abe0e"
down_revision = "5cb3f141eb55"
branch_labels = None
depends_on = None

def upgrade():
    # Agregamos flags con default de servidor para cubrir filas existentes
    op.add_column(
        "usuarios",
        sa.Column("is_admin", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )
    op.add_column(
        "usuarios",
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
    )
    # (Opcional) limpiamos el default de servidor si no lo querés fijo
    op.alter_column("usuarios", "is_admin", server_default=None)
    op.alter_column("usuarios", "is_active", server_default=None)

def downgrade():
    op.drop_column("usuarios", "is_active")
    op.drop_column("usuarios", "is_admin")
