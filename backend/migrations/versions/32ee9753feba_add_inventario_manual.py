"""add_inventario_manual

Revision ID: 32ee9753feba
Revises: 31dd9753feba
Create Date: 2025-09-05 19:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '32ee9753feba'
down_revision: Union[str, Sequence[str], None] = '31dd9753feba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Crear enums para inventario
    op.execute("CREATE TYPE tipoalertainventario AS ENUM ('stock_bajo', 'stock_critico', 'stock_agotado', 'reorden_urgente', 'vencimiento_proximo', 'vencimiento_vencido', 'movimiento_sospechoso')")
    op.execute("CREATE TYPE estadoalerta AS ENUM ('pendiente', 'enviada', 'resuelta', 'ignorada')")
    
    # Crear tabla configuracion_inventario
    op.create_table('configuracion_inventario',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('producto_id', sa.Integer(), nullable=False),
        sa.Column('stock_minimo', sa.Float(), nullable=False),
        sa.Column('stock_maximo', sa.Float(), nullable=True),
        sa.Column('punto_reorden', sa.Float(), nullable=True),
        sa.Column('cantidad_reorden', sa.Float(), nullable=True),
        sa.Column('alerta_stock_bajo', sa.Boolean(), nullable=True),
        sa.Column('alerta_stock_critico', sa.Boolean(), nullable=True),
        sa.Column('alerta_vencimiento', sa.Boolean(), nullable=True),
        sa.Column('dias_vencimiento_alerta', sa.Integer(), nullable=True),
        sa.Column('alerta_movimiento_grande', sa.Boolean(), nullable=True),
        sa.Column('umbral_movimiento_grande', sa.Float(), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False),
        sa.Column('fecha_actualizacion', sa.DateTime(), nullable=False),
        sa.Column('activo', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['producto_id'], ['productos.id'], ),
        sa.UniqueConstraint('producto_id')
    )
    
    # Crear índices para configuracion_inventario
    op.create_index('ix_configuracion_inventario_id', 'configuracion_inventario', ['id'], unique=False)
    op.create_index('ix_configuracion_inventario_producto_id', 'configuracion_inventario', ['producto_id'], unique=False)
    op.create_index('ix_configuracion_inventario_activo', 'configuracion_inventario', ['activo'], unique=False)
    
    # Crear tabla alertas_inventario
    op.create_table('alertas_inventario',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('producto_id', sa.Integer(), nullable=False),
        sa.Column('tipo', sa.Enum('stock_bajo', 'stock_critico', 'stock_agotado', 'reorden_urgente', 'vencimiento_proximo', 'vencimiento_vencido', 'movimiento_sospechoso', name='tipoalertainventario'), nullable=False),
        sa.Column('estado', sa.Enum('pendiente', 'enviada', 'resuelta', 'ignorada', name='estadoalerta'), nullable=True),
        sa.Column('titulo', sa.String(length=255), nullable=False),
        sa.Column('mensaje', sa.Text(), nullable=False),
        sa.Column('prioridad', sa.Integer(), nullable=True),
        sa.Column('stock_actual', sa.Float(), nullable=True),
        sa.Column('stock_minimo', sa.Float(), nullable=True),
        sa.Column('stock_critico', sa.Float(), nullable=True),
        sa.Column('dias_vencimiento', sa.Integer(), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False),
        sa.Column('fecha_resolucion', sa.DateTime(), nullable=True),
        sa.Column('resuelta_por', sa.Integer(), nullable=True),
        sa.Column('notas_resolucion', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['producto_id'], ['productos.id'], ),
        sa.ForeignKeyConstraint(['resuelta_por'], ['users.id'], )
    )
    
    # Crear índices para alertas_inventario
    op.create_index('ix_alertas_inventario_id', 'alertas_inventario', ['id'], unique=False)
    op.create_index('ix_alertas_inventario_producto_id', 'alertas_inventario', ['producto_id'], unique=False)
    op.create_index('ix_alertas_inventario_tipo', 'alertas_inventario', ['tipo'], unique=False)
    op.create_index('ix_alertas_inventario_estado', 'alertas_inventario', ['estado'], unique=False)
    op.create_index('ix_alertas_inventario_prioridad', 'alertas_inventario', ['prioridad'], unique=False)
    op.create_index('ix_alertas_inventario_fecha_creacion', 'alertas_inventario', ['fecha_creacion'], unique=False)
    
    # Crear tabla movimientos_inventario
    op.create_table('movimientos_inventario',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('producto_id', sa.Integer(), nullable=False),
        sa.Column('tipo_movimiento', sa.String(length=50), nullable=False),
        sa.Column('cantidad', sa.Float(), nullable=False),
        sa.Column('cantidad_anterior', sa.Float(), nullable=False),
        sa.Column('cantidad_nueva', sa.Float(), nullable=False),
        sa.Column('referencia_tipo', sa.String(length=50), nullable=True),
        sa.Column('referencia_id', sa.Integer(), nullable=True),
        sa.Column('fecha_movimiento', sa.DateTime(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=True),
        sa.Column('motivo', sa.Text(), nullable=True),
        sa.Column('costo_unitario', sa.Float(), nullable=True),
        sa.Column('costo_total', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['producto_id'], ['productos.id'], ),
        sa.ForeignKeyConstraint(['usuario_id'], ['users.id'], )
    )
    
    # Crear índices para movimientos_inventario
    op.create_index('ix_movimientos_inventario_id', 'movimientos_inventario', ['id'], unique=False)
    op.create_index('ix_movimientos_inventario_producto_id', 'movimientos_inventario', ['producto_id'], unique=False)
    op.create_index('ix_movimientos_inventario_tipo_movimiento', 'movimientos_inventario', ['tipo_movimiento'], unique=False)
    op.create_index('ix_movimientos_inventario_fecha_movimiento', 'movimientos_inventario', ['fecha_movimiento'], unique=False)
    
    # Crear tabla reorden_automatico
    op.create_table('reorden_automatico',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('producto_id', sa.Integer(), nullable=False),
        sa.Column('proveedor_id', sa.Integer(), nullable=True),
        sa.Column('cantidad_sugerida', sa.Float(), nullable=False),
        sa.Column('costo_estimado', sa.Float(), nullable=True),
        sa.Column('fecha_sugerida', sa.DateTime(), nullable=False),
        sa.Column('estado', sa.String(length=20), nullable=True),
        sa.Column('aprobado_por', sa.Integer(), nullable=True),
        sa.Column('fecha_aprobacion', sa.DateTime(), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False),
        sa.Column('notas', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['producto_id'], ['productos.id'], ),
        sa.ForeignKeyConstraint(['proveedor_id'], ['proveedores.id'], ),
        sa.ForeignKeyConstraint(['aprobado_por'], ['users.id'], )
    )
    
    # Crear índices para reorden_automatico
    op.create_index('ix_reorden_automatico_id', 'reorden_automatico', ['id'], unique=False)
    op.create_index('ix_reorden_automatico_producto_id', 'reorden_automatico', ['producto_id'], unique=False)
    op.create_index('ix_reorden_automatico_proveedor_id', 'reorden_automatico', ['proveedor_id'], unique=False)
    op.create_index('ix_reorden_automatico_estado', 'reorden_automatico', ['estado'], unique=False)
    op.create_index('ix_reorden_automatico_fecha_creacion', 'reorden_automatico', ['fecha_creacion'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Eliminar tablas
    op.drop_table('reorden_automatico')
    op.drop_table('movimientos_inventario')
    op.drop_table('alertas_inventario')
    op.drop_table('configuracion_inventario')
    
    # Eliminar enums
    op.execute("DROP TYPE estadoalerta")
    op.execute("DROP TYPE tipoalertainventario")
