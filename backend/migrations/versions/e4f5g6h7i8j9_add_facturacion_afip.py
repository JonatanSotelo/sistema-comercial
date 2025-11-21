"""add facturacion afip

Revision ID: e4f5g6h7i8j9
Revises: d3e4f5g6h7i8
Create Date: 2025-11-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e4f5g6h7i8j9'
down_revision = 'd3e4f5g6h7i8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1) Agregar campos fiscales a clientes
    print(">> Agregando campos fiscales a tabla clientes...")
    op.add_column('clientes', sa.Column('direccion', sa.String(), nullable=True))
    op.add_column('clientes', sa.Column('condicion_iva', sa.String(), nullable=True))
    op.add_column('clientes', sa.Column('doc_tipo', sa.Integer(), nullable=True))
    op.add_column('clientes', sa.Column('doc_nro', sa.String(), nullable=True))
    
    # 2) Crear tabla facturas
    print(">> Creando tabla facturas...")
    op.create_table('facturas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('venta_id', sa.Integer(), nullable=True),
        sa.Column('pedido_id', sa.Integer(), nullable=True),
        sa.Column('tipo_cbte', sa.Integer(), nullable=False),
        sa.Column('pto_vta', sa.Integer(), nullable=False),
        sa.Column('nro_cbte', sa.Integer(), nullable=False),
        sa.Column('concepto', sa.Integer(), nullable=False),
        sa.Column('doc_tipo', sa.Integer(), nullable=False),
        sa.Column('doc_nro', sa.String(), nullable=False),
        sa.Column('imp_neto', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('imp_iva', sa.Numeric(precision=12, scale=2), server_default='0', nullable=False),
        sa.Column('imp_total', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('imp_exento', sa.Numeric(precision=12, scale=2), server_default='0', nullable=False),
        sa.Column('moneda', sa.String(length=3), server_default='ARS', nullable=False),
        sa.Column('cotiz', sa.Numeric(precision=10, scale=3), server_default='1.000', nullable=False),
        sa.Column('cae', sa.String(length=14), nullable=True),
        sa.Column('cae_vto', sa.String(length=10), nullable=True),
        sa.Column('resultado', sa.String(length=1), nullable=True),
        sa.Column('obs', sa.Text(), nullable=True),
        sa.Column('qr_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.CheckConstraint('imp_neto >= 0', name='ck_facturas_imp_neto_pos'),
        sa.CheckConstraint('imp_iva >= 0', name='ck_facturas_imp_iva_pos'),
        sa.CheckConstraint('imp_total >= 0', name='ck_facturas_imp_total_pos'),
        sa.CheckConstraint('imp_exento >= 0', name='ck_facturas_imp_exento_pos'),
        sa.CheckConstraint('(venta_id IS NOT NULL) OR (pedido_id IS NOT NULL)', name='ck_facturas_origen'),
        sa.ForeignKeyConstraint(['pedido_id'], ['pedidos.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['venta_id'], ['ventas.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_facturas_cae'), 'facturas', ['cae'], unique=False)
    op.create_index(op.f('ix_facturas_created_at'), 'facturas', ['created_at'], unique=False)
    op.create_index(op.f('ix_facturas_id'), 'facturas', ['id'], unique=False)
    op.create_index(op.f('ix_facturas_pedido_id'), 'facturas', ['pedido_id'], unique=False)
    op.create_index(op.f('ix_facturas_pto_vta'), 'facturas', ['pto_vta'], unique=False)
    op.create_index(op.f('ix_facturas_tipo_cbte'), 'facturas', ['tipo_cbte'], unique=False)
    op.create_index(op.f('ix_facturas_venta_id'), 'facturas', ['venta_id'], unique=False)
    
    # 3) Crear tabla factura_items
    print(">> Creando tabla factura_items...")
    op.create_table('factura_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('factura_id', sa.Integer(), nullable=False),
        sa.Column('producto_id', sa.Integer(), nullable=True),
        sa.Column('descripcion', sa.String(), nullable=False),
        sa.Column('cantidad', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('precio_unitario', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('alic_iva', sa.Numeric(precision=5, scale=2), server_default='21.0', nullable=False),
        sa.Column('subtotal', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('iva_monto', sa.Numeric(precision=12, scale=2), server_default='0', nullable=False),
        sa.CheckConstraint('cantidad > 0', name='ck_factura_items_cantidad_pos'),
        sa.CheckConstraint('precio_unitario >= 0', name='ck_factura_items_precio_pos'),
        sa.CheckConstraint('alic_iva >= 0', name='ck_factura_items_alic_iva_pos'),
        sa.CheckConstraint('subtotal >= 0', name='ck_factura_items_subtotal_pos'),
        sa.CheckConstraint('iva_monto >= 0', name='ck_factura_items_iva_monto_pos'),
        sa.ForeignKeyConstraint(['factura_id'], ['facturas.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['producto_id'], ['productos.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_factura_items_factura_id'), 'factura_items', ['factura_id'], unique=False)
    op.create_index(op.f('ix_factura_items_id'), 'factura_items', ['id'], unique=False)
    
    print(">> Facturación AFIP: tablas creadas exitosamente")


def downgrade() -> None:
    print(">> Revirtiendo migración de facturación AFIP...")
    op.drop_index(op.f('ix_factura_items_id'), table_name='factura_items')
    op.drop_index(op.f('ix_factura_items_factura_id'), table_name='factura_items')
    op.drop_table('factura_items')
    
    op.drop_index(op.f('ix_facturas_venta_id'), table_name='facturas')
    op.drop_index(op.f('ix_facturas_tipo_cbte'), table_name='facturas')
    op.drop_index(op.f('ix_facturas_pto_vta'), table_name='facturas')
    op.drop_index(op.f('ix_facturas_pedido_id'), table_name='facturas')
    op.drop_index(op.f('ix_facturas_id'), table_name='facturas')
    op.drop_index(op.f('ix_facturas_created_at'), table_name='facturas')
    op.drop_index(op.f('ix_facturas_cae'), table_name='facturas')
    op.drop_table('facturas')
    
    op.drop_column('clientes', 'doc_nro')
    op.drop_column('clientes', 'doc_tipo')
    op.drop_column('clientes', 'condicion_iva')
    op.drop_column('clientes', 'direccion')
    print(">> Migración de facturación revertida")

