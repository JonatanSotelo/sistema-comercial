"""add_reportes_financieros_manual

Revision ID: 410587ef6e56
Revises: 9e5daa1a210c
Create Date: 2025-01-27 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '410587ef6e56'
down_revision = '9e5daa1a210c'
branch_labels = None
depends_on = None


def upgrade():
    # Crear ENUMs para reportes financieros
    op.execute("CREATE TYPE tiporeportefinanciero AS ENUM ('estado_resultados', 'flujo_caja', 'rentabilidad', 'proyeccion', 'dashboard', 'analisis_costos', 'margen_bruto', 'rotacion_inventario')")
    op.execute("CREATE TYPE periodoreporte AS ENUM ('diario', 'semanal', 'mensual', 'trimestral', 'anual', 'personalizado')")
    op.execute("CREATE TYPE estadoreporte AS ENUM ('generando', 'completado', 'error', 'expirado')")
    
    # Crear tabla reportes_financieros
    op.create_table('reportes_financieros',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=255), nullable=False),
        sa.Column('tipo', sa.Enum('estado_resultados', 'flujo_caja', 'rentabilidad', 'proyeccion', 'dashboard', 'analisis_costos', 'margen_bruto', 'rotacion_inventario', name='tiporeportefinanciero'), nullable=False),
        sa.Column('periodo', sa.Enum('diario', 'semanal', 'mensual', 'trimestral', 'anual', 'personalizado', name='periodoreporte'), nullable=False),
        sa.Column('estado', sa.Enum('generando', 'completado', 'error', 'expirado', name='estadoreporte'), nullable=True),
        sa.Column('fecha_inicio', sa.Date(), nullable=False),
        sa.Column('fecha_fin', sa.Date(), nullable=False),
        sa.Column('fecha_generacion', sa.DateTime(), nullable=False),
        sa.Column('fecha_expiracion', sa.DateTime(), nullable=True),
        sa.Column('incluir_detalles', sa.Boolean(), nullable=True),
        sa.Column('incluir_proyecciones', sa.Boolean(), nullable=True),
        sa.Column('incluir_comparaciones', sa.Boolean(), nullable=True),
        sa.Column('formato_salida', sa.String(length=50), nullable=True),
        sa.Column('filtro_productos', sa.Text(), nullable=True),
        sa.Column('filtro_clientes', sa.Text(), nullable=True),
        sa.Column('filtro_categorias', sa.Text(), nullable=True),
        sa.Column('filtro_proveedores', sa.Text(), nullable=True),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('parametros_personalizados', sa.Text(), nullable=True),
        sa.Column('creado_por', sa.Integer(), nullable=True),
        sa.Column('archivo_ruta', sa.String(length=500), nullable=True),
        sa.Column('tamaño_archivo', sa.Integer(), nullable=True),
        sa.Column('total_ingresos', sa.Float(), nullable=True),
        sa.Column('total_costos', sa.Float(), nullable=True),
        sa.Column('total_gastos', sa.Float(), nullable=True),
        sa.Column('ganancia_neta', sa.Float(), nullable=True),
        sa.Column('margen_bruto', sa.Float(), nullable=True),
        sa.Column('margen_neto', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['creado_por'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Crear índices para reportes_financieros
    op.create_index('ix_reportes_financieros_id', 'reportes_financieros', ['id'])
    op.create_index('ix_reportes_financieros_nombre', 'reportes_financieros', ['nombre'])
    op.create_index('ix_reportes_financieros_tipo', 'reportes_financieros', ['tipo'])
    op.create_index('ix_reportes_financieros_periodo', 'reportes_financieros', ['periodo'])
    op.create_index('ix_reportes_financieros_estado', 'reportes_financieros', ['estado'])
    op.create_index('ix_reportes_financieros_fecha_inicio', 'reportes_financieros', ['fecha_inicio'])
    op.create_index('ix_reportes_financieros_fecha_expiracion', 'reportes_financieros', ['fecha_expiracion'])
    
    # Crear tabla estado_resultados
    op.create_table('estado_resultados',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reporte_id', sa.Integer(), nullable=False),
        sa.Column('ventas_brutas', sa.Float(), nullable=False),
        sa.Column('descuentos_ventas', sa.Float(), nullable=False),
        sa.Column('devoluciones_ventas', sa.Float(), nullable=False),
        sa.Column('ventas_netas', sa.Float(), nullable=False),
        sa.Column('inventario_inicial', sa.Float(), nullable=False),
        sa.Column('compras', sa.Float(), nullable=False),
        sa.Column('inventario_final', sa.Float(), nullable=False),
        sa.Column('costo_ventas', sa.Float(), nullable=False),
        sa.Column('utilidad_bruta', sa.Float(), nullable=False),
        sa.Column('margen_bruto_porcentaje', sa.Float(), nullable=False),
        sa.Column('gastos_administrativos', sa.Float(), nullable=False),
        sa.Column('gastos_ventas', sa.Float(), nullable=False),
        sa.Column('gastos_generales', sa.Float(), nullable=False),
        sa.Column('total_gastos_operativos', sa.Float(), nullable=False),
        sa.Column('utilidad_operativa', sa.Float(), nullable=False),
        sa.Column('margen_operativo_porcentaje', sa.Float(), nullable=False),
        sa.Column('otros_ingresos', sa.Float(), nullable=False),
        sa.Column('otros_gastos', sa.Float(), nullable=False),
        sa.Column('intereses', sa.Float(), nullable=False),
        sa.Column('impuestos', sa.Float(), nullable=False),
        sa.Column('utilidad_neta', sa.Float(), nullable=False),
        sa.Column('margen_neto_porcentaje', sa.Float(), nullable=False),
        sa.Column('fecha_calculo', sa.DateTime(), nullable=False),
        sa.Column('periodo_desde', sa.Date(), nullable=False),
        sa.Column('periodo_hasta', sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(['reporte_id'], ['reportes_financieros.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Crear tabla flujo_caja
    op.create_table('flujo_caja',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reporte_id', sa.Integer(), nullable=False),
        sa.Column('ingresos_operativos', sa.Float(), nullable=False),
        sa.Column('pagos_proveedores', sa.Float(), nullable=False),
        sa.Column('pagos_empleados', sa.Float(), nullable=False),
        sa.Column('pagos_impuestos', sa.Float(), nullable=False),
        sa.Column('otros_pagos_operativos', sa.Float(), nullable=False),
        sa.Column('flujo_operativo', sa.Float(), nullable=False),
        sa.Column('compras_activos', sa.Float(), nullable=False),
        sa.Column('ventas_activos', sa.Float(), nullable=False),
        sa.Column('inversiones', sa.Float(), nullable=False),
        sa.Column('flujo_inversion', sa.Float(), nullable=False),
        sa.Column('prestamos_recibidos', sa.Float(), nullable=False),
        sa.Column('pagos_prestamos', sa.Float(), nullable=False),
        sa.Column('dividendos_pagados', sa.Float(), nullable=False),
        sa.Column('flujo_financiamiento', sa.Float(), nullable=False),
        sa.Column('flujo_caja_neto', sa.Float(), nullable=False),
        sa.Column('saldo_caja_inicial', sa.Float(), nullable=False),
        sa.Column('saldo_caja_final', sa.Float(), nullable=False),
        sa.Column('fecha_calculo', sa.DateTime(), nullable=False),
        sa.Column('periodo_desde', sa.Date(), nullable=False),
        sa.Column('periodo_hasta', sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(['reporte_id'], ['reportes_financieros.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Crear tabla analisis_rentabilidad
    op.create_table('analisis_rentabilidad',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reporte_id', sa.Integer(), nullable=False),
        sa.Column('tipo_entidad', sa.String(length=50), nullable=False),
        sa.Column('entidad_id', sa.Integer(), nullable=False),
        sa.Column('entidad_nombre', sa.String(length=255), nullable=False),
        sa.Column('ingresos_totales', sa.Float(), nullable=False),
        sa.Column('costos_totales', sa.Float(), nullable=False),
        sa.Column('utilidad_bruta', sa.Float(), nullable=False),
        sa.Column('margen_bruto_porcentaje', sa.Float(), nullable=False),
        sa.Column('costo_productos', sa.Float(), nullable=False),
        sa.Column('costo_mano_obra', sa.Float(), nullable=False),
        sa.Column('costo_overhead', sa.Float(), nullable=False),
        sa.Column('costo_marketing', sa.Float(), nullable=False),
        sa.Column('cantidad_vendida', sa.Float(), nullable=False),
        sa.Column('precio_promedio', sa.Float(), nullable=False),
        sa.Column('ticket_promedio', sa.Float(), nullable=False),
        sa.Column('rotacion_inventario', sa.Float(), nullable=True),
        sa.Column('dias_inventario', sa.Float(), nullable=True),
        sa.Column('rentabilidad_sobre_ventas', sa.Float(), nullable=True),
        sa.Column('rentabilidad_sobre_inversion', sa.Float(), nullable=True),
        sa.Column('fecha_calculo', sa.DateTime(), nullable=False),
        sa.Column('periodo_desde', sa.Date(), nullable=False),
        sa.Column('periodo_hasta', sa.Date(), nullable=False),
        sa.Column('ranking', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['reporte_id'], ['reportes_financieros.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Crear índices para analisis_rentabilidad
    op.create_index('ix_analisis_rentabilidad_id', 'analisis_rentabilidad', ['id'])
    op.create_index('ix_analisis_rentabilidad_tipo_entidad', 'analisis_rentabilidad', ['tipo_entidad'])
    op.create_index('ix_analisis_rentabilidad_entidad_id', 'analisis_rentabilidad', ['entidad_id'])
    
    # Crear tabla proyecciones_financieras
    op.create_table('proyecciones_financieras',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reporte_id', sa.Integer(), nullable=False),
        sa.Column('tipo_proyeccion', sa.String(length=50), nullable=False),
        sa.Column('horizonte_meses', sa.Integer(), nullable=False),
        sa.Column('metodo_calculo', sa.String(length=50), nullable=False),
        sa.Column('periodo_historico_desde', sa.Date(), nullable=False),
        sa.Column('periodo_historico_hasta', sa.Date(), nullable=False),
        sa.Column('valor_historico_promedio', sa.Float(), nullable=False),
        sa.Column('tendencia_porcentaje', sa.Float(), nullable=True),
        sa.Column('proyeccion_mes_1', sa.Float(), nullable=True),
        sa.Column('proyeccion_mes_2', sa.Float(), nullable=True),
        sa.Column('proyeccion_mes_3', sa.Float(), nullable=True),
        sa.Column('proyeccion_mes_6', sa.Float(), nullable=True),
        sa.Column('proyeccion_mes_12', sa.Float(), nullable=True),
        sa.Column('factor_estacional', sa.Float(), nullable=True),
        sa.Column('factor_crecimiento', sa.Float(), nullable=True),
        sa.Column('factor_inflacion', sa.Float(), nullable=True),
        sa.Column('confianza_porcentaje', sa.Float(), nullable=True),
        sa.Column('margen_error', sa.Float(), nullable=True),
        sa.Column('fecha_calculo', sa.DateTime(), nullable=False),
        sa.Column('creado_por', sa.Integer(), nullable=True),
        sa.Column('activo', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['creado_por'], ['users.id'], ),
        sa.ForeignKeyConstraint(['reporte_id'], ['reportes_financieros.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Crear índices para proyecciones_financieras
    op.create_index('ix_proyecciones_financieras_id', 'proyecciones_financieras', ['id'])
    op.create_index('ix_proyecciones_financieras_tipo_proyeccion', 'proyecciones_financieras', ['tipo_proyeccion'])
    op.create_index('ix_proyecciones_financieras_activo', 'proyecciones_financieras', ['activo'])
    
    # Crear tabla metricas_financieras
    op.create_table('metricas_financieras',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nombre', sa.String(length=255), nullable=False),
        sa.Column('categoria', sa.String(length=100), nullable=False),
        sa.Column('tipo_valor', sa.String(length=50), nullable=False),
        sa.Column('valor_actual', sa.Float(), nullable=False),
        sa.Column('valor_anterior', sa.Float(), nullable=True),
        sa.Column('valor_objetivo', sa.Float(), nullable=True),
        sa.Column('variacion_porcentaje', sa.Float(), nullable=True),
        sa.Column('fecha_calculo', sa.DateTime(), nullable=False),
        sa.Column('periodo_desde', sa.Date(), nullable=False),
        sa.Column('periodo_hasta', sa.Date(), nullable=False),
        sa.Column('descripcion', sa.Text(), nullable=True),
        sa.Column('formula', sa.Text(), nullable=True),
        sa.Column('fuente_datos', sa.String(length=255), nullable=True),
        sa.Column('calculado_por', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['calculado_por'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Crear índices para metricas_financieras
    op.create_index('ix_metricas_financieras_id', 'metricas_financieras', ['id'])
    op.create_index('ix_metricas_financieras_nombre', 'metricas_financieras', ['nombre'])
    op.create_index('ix_metricas_financieras_categoria', 'metricas_financieras', ['categoria'])
    op.create_index('ix_metricas_financieras_fecha_calculo', 'metricas_financieras', ['fecha_calculo'])


def downgrade():
    # Eliminar índices
    op.drop_index('ix_metricas_financieras_fecha_calculo', table_name='metricas_financieras')
    op.drop_index('ix_metricas_financieras_categoria', table_name='metricas_financieras')
    op.drop_index('ix_metricas_financieras_nombre', table_name='metricas_financieras')
    op.drop_index('ix_metricas_financieras_id', table_name='metricas_financieras')
    op.drop_index('ix_proyecciones_financieras_activo', table_name='proyecciones_financieras')
    op.drop_index('ix_proyecciones_financieras_tipo_proyeccion', table_name='proyecciones_financieras')
    op.drop_index('ix_proyecciones_financieras_id', table_name='proyecciones_financieras')
    op.drop_index('ix_analisis_rentabilidad_entidad_id', table_name='analisis_rentabilidad')
    op.drop_index('ix_analisis_rentabilidad_tipo_entidad', table_name='analisis_rentabilidad')
    op.drop_index('ix_analisis_rentabilidad_id', table_name='analisis_rentabilidad')
    op.drop_index('ix_reportes_financieros_fecha_expiracion', table_name='reportes_financieros')
    op.drop_index('ix_reportes_financieros_fecha_inicio', table_name='reportes_financieros')
    op.drop_index('ix_reportes_financieros_estado', table_name='reportes_financieros')
    op.drop_index('ix_reportes_financieros_periodo', table_name='reportes_financieros')
    op.drop_index('ix_reportes_financieros_tipo', table_name='reportes_financieros')
    op.drop_index('ix_reportes_financieros_nombre', table_name='reportes_financieros')
    op.drop_index('ix_reportes_financieros_id', table_name='reportes_financieros')
    
    # Eliminar tablas
    op.drop_table('metricas_financieras')
    op.drop_table('proyecciones_financieras')
    op.drop_table('analisis_rentabilidad')
    op.drop_table('flujo_caja')
    op.drop_table('estado_resultados')
    op.drop_table('reportes_financieros')
    
    # Eliminar ENUMs
    op.execute("DROP TYPE IF EXISTS estadoreporte")
    op.execute("DROP TYPE IF EXISTS periodoreporte")
    op.execute("DROP TYPE IF EXISTS tiporeportefinanciero")

