"""add cobros caja

Revision ID: f5g6h7i8j9k0
Revises: e4f5g6h7i8j9
Create Date: 2025-11-21 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f5g6h7i8j9k0'
down_revision = 'e4f5g6h7i8j9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1) Crear tabla cobros
    print(">> Creando tabla cobros...")
    op.create_table('cobros',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('venta_id', sa.Integer(), nullable=False),
        sa.Column('medio', sa.Enum('EFECTIVO', 'TRANSFERENCIA', 'MERCADOPAGO', 'TARJETA', 'CHEQUE', 'OTRO', name='mediocobro'), nullable=False),
        sa.Column('importe', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('moneda', sa.String(length=3), server_default='ARS', nullable=False),
        sa.Column('referencia', sa.String(), nullable=True),
        sa.Column('observaciones', sa.Text(), nullable=True),
        sa.Column('estado', sa.Enum('CONFIRMADO', 'ANULADO', name='estadocobro'), server_default='CONFIRMADO', nullable=False),
        sa.CheckConstraint('importe >= 0', name='ck_cobros_importe_pos'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['venta_id'], ['ventas.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cobros_created_at'), 'cobros', ['created_at'], unique=False)
    op.create_index(op.f('ix_cobros_estado'), 'cobros', ['estado'], unique=False)
    op.create_index(op.f('ix_cobros_id'), 'cobros', ['id'], unique=False)
    op.create_index(op.f('ix_cobros_medio'), 'cobros', ['medio'], unique=False)
    op.create_index(op.f('ix_cobros_venta_id'), 'cobros', ['venta_id'], unique=False)
    
    # 2) Crear tabla purchase_invoices (Libro IVA Compras)
    print(">> Creando tabla purchase_invoices...")
    op.create_table('purchase_invoices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('proveedor_id', sa.Integer(), nullable=True),
        sa.Column('proveedor_nombre', sa.String(), nullable=True),
        sa.Column('fecha', sa.Date(), nullable=False),
        sa.Column('tipo_cbte', sa.Integer(), nullable=False),
        sa.Column('pto_vta', sa.Integer(), nullable=False),
        sa.Column('nro_cbte', sa.Integer(), nullable=False),
        sa.Column('doc_tipo', sa.Integer(), nullable=True),
        sa.Column('doc_nro', sa.String(), nullable=True),
        sa.Column('imp_neto', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('imp_iva', sa.Numeric(precision=12, scale=2), server_default='0', nullable=False),
        sa.Column('imp_exento', sa.Numeric(precision=12, scale=2), server_default='0', nullable=False),
        sa.Column('imp_total', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('alicuota_principal', sa.Numeric(precision=5, scale=2), server_default='21.0', nullable=False),
        sa.Column('moneda', sa.String(length=3), server_default='ARS', nullable=False),
        sa.Column('cotiz', sa.Numeric(precision=10, scale=3), server_default='1.000', nullable=False),
        sa.Column('compra_id', sa.Integer(), nullable=True),
        sa.CheckConstraint('imp_neto >= 0', name='ck_purchase_invoices_imp_neto_pos'),
        sa.CheckConstraint('imp_iva >= 0', name='ck_purchase_invoices_imp_iva_pos'),
        sa.CheckConstraint('imp_exento >= 0', name='ck_purchase_invoices_imp_exento_pos'),
        sa.CheckConstraint('imp_total >= 0', name='ck_purchase_invoices_imp_total_pos'),
        sa.CheckConstraint('alicuota_principal >= 0', name='ck_purchase_invoices_alic_pos'),
        sa.ForeignKeyConstraint(['compra_id'], ['compras.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['proveedor_id'], ['proveedores.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_purchase_invoices_compra_id'), 'purchase_invoices', ['compra_id'], unique=False)
    op.create_index(op.f('ix_purchase_invoices_fecha'), 'purchase_invoices', ['fecha'], unique=False)
    op.create_index(op.f('ix_purchase_invoices_id'), 'purchase_invoices', ['id'], unique=False)
    op.create_index(op.f('ix_purchase_invoices_proveedor_id'), 'purchase_invoices', ['proveedor_id'], unique=False)
    op.create_index(op.f('ix_purchase_invoices_tipo_cbte'), 'purchase_invoices', ['tipo_cbte'], unique=False)
    
    print(">> Cobros & Caja + IVA Compras: tablas creadas exitosamente")


def downgrade() -> None:
    print(">> Revirtiendo migración de cobros y caja...")
    op.drop_index(op.f('ix_purchase_invoices_tipo_cbte'), table_name='purchase_invoices')
    op.drop_index(op.f('ix_purchase_invoices_proveedor_id'), table_name='purchase_invoices')
    op.drop_index(op.f('ix_purchase_invoices_id'), table_name='purchase_invoices')
    op.drop_index(op.f('ix_purchase_invoices_fecha'), table_name='purchase_invoices')
    op.drop_index(op.f('ix_purchase_invoices_compra_id'), table_name='purchase_invoices')
    op.drop_table('purchase_invoices')
    
    op.drop_index(op.f('ix_cobros_venta_id'), table_name='cobros')
    op.drop_index(op.f('ix_cobros_medio'), table_name='cobros')
    op.drop_index(op.f('ix_cobros_id'), table_name='cobros')
    op.drop_index(op.f('ix_cobros_estado'), table_name='cobros')
    op.drop_index(op.f('ix_cobros_created_at'), table_name='cobros')
    op.drop_table('cobros')
    
    # Drop ENUMs
    op.execute('DROP TYPE IF EXISTS estadocobro')
    op.execute('DROP TYPE IF EXISTS mediocobro')
    
    print(">> Migración de cobros y caja revertida")

