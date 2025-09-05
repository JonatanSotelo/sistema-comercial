"""add_precios_manual

Revision ID: 9e5daa1a210c
Revises: 8d5daa1a210c
Create Date: 2024-12-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9e5daa1a210c'
down_revision = '8d5daa1a210c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema."""
    # Crear enum para tipos de precio
    op.execute("CREATE TYPE tipoprecio AS ENUM ('base', 'cliente', 'volumen', 'categoria', 'estacional', 'promocional')")
    
    # Crear enum para estados de precio
    op.execute("CREATE TYPE estadoprecio AS ENUM ('activo', 'inactivo', 'expirado', 'suspendido')")
    
    # Crear tabla precios_producto
    op.create_table('precios_producto',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('producto_id', sa.Integer(), nullable=False),
        sa.Column('tipo', sa.Enum('base', 'cliente', 'volumen', 'categoria', 'estacional', 'promocional', name='tipoprecio'), nullable=False),
        sa.Column('estado', sa.Enum('activo', 'inactivo', 'expirado', 'suspendido', name='estadoprecio'), nullable=True),
        sa.Column('precio_base', sa.Float(), nullable=False),
        sa.Column('precio_especial', sa.Float(), nullable=True),
        sa.Column('descuento_porcentaje', sa.Float(), nullable=True),
        sa.Column('descuento_monto', sa.Float(), nullable=True),
        sa.Column('cliente_id', sa.Integer(), nullable=True),
        sa.Column('categoria_id', sa.Integer(), nullable=True),
        sa.Column('cantidad_minima', sa.Float(), nullable=True),
        sa.Column('cantidad_maxima', sa.Float(), nullable=True),
        sa.Column('fecha_inicio', sa.DateTime(), nullable=False),
        sa.Column('fecha_fin', sa.DateTime(), nullable=True),
        sa.Column('nombre', sa.String(length=255), nullable=True),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('creado_por', sa.Integer(), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False),
        sa.Column('fecha_actualizacion', sa.DateTime(), nullable=False),
        sa.Column('activo', sa.Boolean(), nullable=True),
        sa.Column('prioridad', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Crear índices para precios_producto
    op.create_index('ix_precios_producto_id', 'precios_producto', ['id'], unique=False)
    op.create_index('ix_precios_producto_producto_id', 'precios_producto', ['producto_id'], unique=False)
    op.create_index('ix_precios_producto_tipo', 'precios_producto', ['tipo'], unique=False)
    op.create_index('ix_precios_producto_estado', 'precios_producto', ['estado'], unique=False)
    op.create_index('ix_precios_producto_cliente_id', 'precios_producto', ['cliente_id'], unique=False)
    op.create_index('ix_precios_producto_categoria_id', 'precios_producto', ['categoria_id'], unique=False)
    op.create_index('ix_precios_producto_fecha_inicio', 'precios_producto', ['fecha_inicio'], unique=False)
    op.create_index('ix_precios_producto_fecha_fin', 'precios_producto', ['fecha_fin'], unique=False)
    op.create_index('ix_precios_producto_activo', 'precios_producto', ['activo'], unique=False)
    op.create_index('ix_precios_producto_prioridad', 'precios_producto', ['prioridad'], unique=False)
    
    # Crear tabla precios_volumen
    op.create_table('precios_volumen',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('producto_id', sa.Integer(), nullable=False),
        sa.Column('cantidad_minima', sa.Float(), nullable=False),
        sa.Column('cantidad_maxima', sa.Float(), nullable=True),
        sa.Column('descuento_porcentaje', sa.Float(), nullable=True),
        sa.Column('descuento_monto', sa.Float(), nullable=True),
        sa.Column('precio_especial', sa.Float(), nullable=True),
        sa.Column('cliente_id', sa.Integer(), nullable=True),
        sa.Column('categoria_id', sa.Integer(), nullable=True),
        sa.Column('fecha_inicio', sa.DateTime(), nullable=False),
        sa.Column('fecha_fin', sa.DateTime(), nullable=True),
        sa.Column('nombre', sa.String(length=255), nullable=True),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('creado_por', sa.Integer(), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False),
        sa.Column('activo', sa.Boolean(), nullable=True),
        sa.Column('prioridad', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Crear índices para precios_volumen
    op.create_index('ix_precios_volumen_id', 'precios_volumen', ['id'], unique=False)
    op.create_index('ix_precios_volumen_producto_id', 'precios_volumen', ['producto_id'], unique=False)
    op.create_index('ix_precios_volumen_cantidad_minima', 'precios_volumen', ['cantidad_minima'], unique=False)
    op.create_index('ix_precios_volumen_cantidad_maxima', 'precios_volumen', ['cantidad_maxima'], unique=False)
    op.create_index('ix_precios_volumen_cliente_id', 'precios_volumen', ['cliente_id'], unique=False)
    op.create_index('ix_precios_volumen_categoria_id', 'precios_volumen', ['categoria_id'], unique=False)
    op.create_index('ix_precios_volumen_fecha_inicio', 'precios_volumen', ['fecha_inicio'], unique=False)
    op.create_index('ix_precios_volumen_fecha_fin', 'precios_volumen', ['fecha_fin'], unique=False)
    op.create_index('ix_precios_volumen_activo', 'precios_volumen', ['activo'], unique=False)
    op.create_index('ix_precios_volumen_prioridad', 'precios_volumen', ['prioridad'], unique=False)
    
    # Crear tabla precios_categoria
    op.create_table('precios_categoria',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('categoria_id', sa.Integer(), nullable=False),
        sa.Column('descuento_porcentaje', sa.Float(), nullable=True),
        sa.Column('descuento_monto', sa.Float(), nullable=True),
        sa.Column('multiplicador', sa.Float(), nullable=True),
        sa.Column('cliente_id', sa.Integer(), nullable=True),
        sa.Column('producto_id', sa.Integer(), nullable=True),
        sa.Column('fecha_inicio', sa.DateTime(), nullable=False),
        sa.Column('fecha_fin', sa.DateTime(), nullable=True),
        sa.Column('nombre', sa.String(length=255), nullable=True),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('creado_por', sa.Integer(), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False),
        sa.Column('activo', sa.Boolean(), nullable=True),
        sa.Column('prioridad', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Crear índices para precios_categoria
    op.create_index('ix_precios_categoria_id', 'precios_categoria', ['id'], unique=False)
    op.create_index('ix_precios_categoria_categoria_id', 'precios_categoria', ['categoria_id'], unique=False)
    op.create_index('ix_precios_categoria_cliente_id', 'precios_categoria', ['cliente_id'], unique=False)
    op.create_index('ix_precios_categoria_producto_id', 'precios_categoria', ['producto_id'], unique=False)
    op.create_index('ix_precios_categoria_fecha_inicio', 'precios_categoria', ['fecha_inicio'], unique=False)
    op.create_index('ix_precios_categoria_fecha_fin', 'precios_categoria', ['fecha_fin'], unique=False)
    op.create_index('ix_precios_categoria_activo', 'precios_categoria', ['activo'], unique=False)
    op.create_index('ix_precios_categoria_prioridad', 'precios_categoria', ['prioridad'], unique=False)
    
    # Crear tabla precios_estacionales
    op.create_table('precios_estacionales',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('producto_id', sa.Integer(), nullable=False),
        sa.Column('nombre_temporada', sa.String(length=100), nullable=False),
        sa.Column('descuento_porcentaje', sa.Float(), nullable=True),
        sa.Column('descuento_monto', sa.Float(), nullable=True),
        sa.Column('precio_especial', sa.Float(), nullable=True),
        sa.Column('cliente_id', sa.Integer(), nullable=True),
        sa.Column('categoria_id', sa.Integer(), nullable=True),
        sa.Column('fecha_inicio', sa.Date(), nullable=False),
        sa.Column('fecha_fin', sa.Date(), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('creado_por', sa.Integer(), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False),
        sa.Column('activo', sa.Boolean(), nullable=True),
        sa.Column('prioridad', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Crear índices para precios_estacionales
    op.create_index('ix_precios_estacionales_id', 'precios_estacionales', ['id'], unique=False)
    op.create_index('ix_precios_estacionales_producto_id', 'precios_estacionales', ['producto_id'], unique=False)
    op.create_index('ix_precios_estacionales_nombre_temporada', 'precios_estacionales', ['nombre_temporada'], unique=False)
    op.create_index('ix_precios_estacionales_cliente_id', 'precios_estacionales', ['cliente_id'], unique=False)
    op.create_index('ix_precios_estacionales_categoria_id', 'precios_estacionales', ['categoria_id'], unique=False)
    op.create_index('ix_precios_estacionales_fecha_inicio', 'precios_estacionales', ['fecha_inicio'], unique=False)
    op.create_index('ix_precios_estacionales_fecha_fin', 'precios_estacionales', ['fecha_fin'], unique=False)
    op.create_index('ix_precios_estacionales_activo', 'precios_estacionales', ['activo'], unique=False)
    op.create_index('ix_precios_estacionales_prioridad', 'precios_estacionales', ['prioridad'], unique=False)
    
    # Crear tabla precio_historial
    op.create_table('precio_historial',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('producto_id', sa.Integer(), nullable=False),
        sa.Column('tipo_cambio', sa.String(length=50), nullable=False),
        sa.Column('precio_anterior', sa.Float(), nullable=True),
        sa.Column('precio_nuevo', sa.Float(), nullable=True),
        sa.Column('descuento_anterior', sa.Float(), nullable=True),
        sa.Column('descuento_nuevo', sa.Float(), nullable=True),
        sa.Column('precio_id', sa.Integer(), nullable=True),
        sa.Column('precio_tabla', sa.String(length=50), nullable=True),
        sa.Column('motivo', sa.Text(), nullable=True),
        sa.Column('usuario_id', sa.Integer(), nullable=True),
        sa.Column('fecha_cambio', sa.DateTime(), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Crear índices para precio_historial
    op.create_index('ix_precio_historial_id', 'precio_historial', ['id'], unique=False)
    op.create_index('ix_precio_historial_producto_id', 'precio_historial', ['producto_id'], unique=False)
    op.create_index('ix_precio_historial_tipo_cambio', 'precio_historial', ['tipo_cambio'], unique=False)
    op.create_index('ix_precio_historial_precio_id', 'precio_historial', ['precio_id'], unique=False)
    op.create_index('ix_precio_historial_fecha_cambio', 'precio_historial', ['fecha_cambio'], unique=False)
    
    # Crear tabla precios_aplicados
    op.create_table('precios_aplicados',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('venta_id', sa.Integer(), nullable=False),
        sa.Column('producto_id', sa.Integer(), nullable=False),
        sa.Column('cliente_id', sa.Integer(), nullable=True),
        sa.Column('precio_base', sa.Float(), nullable=False),
        sa.Column('precio_final', sa.Float(), nullable=False),
        sa.Column('descuento_aplicado', sa.Float(), nullable=True),
        sa.Column('porcentaje_descuento', sa.Float(), nullable=True),
        sa.Column('tipo_precio', sa.String(length=50), nullable=False),
        sa.Column('precio_id', sa.Integer(), nullable=True),
        sa.Column('precio_tabla', sa.String(length=50), nullable=True),
        sa.Column('cantidad', sa.Float(), nullable=False),
        sa.Column('subtotal', sa.Float(), nullable=False),
        sa.Column('fecha_aplicacion', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Crear índices para precios_aplicados
    op.create_index('ix_precios_aplicados_id', 'precios_aplicados', ['id'], unique=False)
    op.create_index('ix_precios_aplicados_venta_id', 'precios_aplicados', ['venta_id'], unique=False)
    op.create_index('ix_precios_aplicados_producto_id', 'precios_aplicados', ['producto_id'], unique=False)
    op.create_index('ix_precios_aplicados_cliente_id', 'precios_aplicados', ['cliente_id'], unique=False)
    op.create_index('ix_precios_aplicados_tipo_precio', 'precios_aplicados', ['tipo_precio'], unique=False)
    op.create_index('ix_precios_aplicados_precio_id', 'precios_aplicados', ['precio_id'], unique=False)
    op.create_index('ix_precios_aplicados_fecha_aplicacion', 'precios_aplicados', ['fecha_aplicacion'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Eliminar tablas
    op.drop_table('precios_aplicados')
    op.drop_table('precio_historial')
    op.drop_table('precios_estacionales')
    op.drop_table('precios_categoria')
    op.drop_table('precios_volumen')
    op.drop_table('precios_producto')
    
    # Eliminar enums
    op.execute("DROP TYPE estadoprecio")
    op.execute("DROP TYPE tipoprecio")
