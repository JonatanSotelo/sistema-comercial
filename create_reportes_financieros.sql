-- Crear tabla reportes_financieros
CREATE TABLE reportes_financieros (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    tipo tiporeportefinanciero NOT NULL,
    periodo periodoreporte NOT NULL,
    estado estadoreporte DEFAULT 'generando',
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion TIMESTAMP,
    incluir_detalles BOOLEAN DEFAULT TRUE,
    incluir_proyecciones BOOLEAN DEFAULT FALSE,
    incluir_comparaciones BOOLEAN DEFAULT FALSE,
    formato_salida VARCHAR(50) DEFAULT 'json',
    filtro_productos TEXT,
    filtro_clientes TEXT,
    filtro_categorias TEXT,
    filtro_proveedores TEXT,
    descripcion TEXT,
    parametros_personalizados TEXT,
    creado_por INTEGER REFERENCES users(id),
    archivo_ruta VARCHAR(500),
    tamaño_archivo INTEGER,
    total_ingresos FLOAT,
    total_costos FLOAT,
    total_gastos FLOAT,
    ganancia_neta FLOAT,
    margen_bruto FLOAT,
    margen_neto FLOAT
);

-- Crear índices para reportes_financieros
CREATE INDEX ix_reportes_financieros_id ON reportes_financieros(id);
CREATE INDEX ix_reportes_financieros_nombre ON reportes_financieros(nombre);
CREATE INDEX ix_reportes_financieros_tipo ON reportes_financieros(tipo);
CREATE INDEX ix_reportes_financieros_periodo ON reportes_financieros(periodo);
CREATE INDEX ix_reportes_financieros_estado ON reportes_financieros(estado);
CREATE INDEX ix_reportes_financieros_fecha_inicio ON reportes_financieros(fecha_inicio);
CREATE INDEX ix_reportes_financieros_fecha_expiracion ON reportes_financieros(fecha_expiracion);

-- Crear tabla estado_resultados
CREATE TABLE estado_resultados (
    id SERIAL PRIMARY KEY,
    reporte_id INTEGER NOT NULL REFERENCES reportes_financieros(id),
    ventas_brutas FLOAT NOT NULL DEFAULT 0.0,
    descuentos_ventas FLOAT NOT NULL DEFAULT 0.0,
    devoluciones_ventas FLOAT NOT NULL DEFAULT 0.0,
    ventas_netas FLOAT NOT NULL DEFAULT 0.0,
    inventario_inicial FLOAT NOT NULL DEFAULT 0.0,
    compras FLOAT NOT NULL DEFAULT 0.0,
    inventario_final FLOAT NOT NULL DEFAULT 0.0,
    costo_ventas FLOAT NOT NULL DEFAULT 0.0,
    utilidad_bruta FLOAT NOT NULL DEFAULT 0.0,
    margen_bruto_porcentaje FLOAT NOT NULL DEFAULT 0.0,
    gastos_administrativos FLOAT NOT NULL DEFAULT 0.0,
    gastos_ventas FLOAT NOT NULL DEFAULT 0.0,
    gastos_generales FLOAT NOT NULL DEFAULT 0.0,
    total_gastos_operativos FLOAT NOT NULL DEFAULT 0.0,
    utilidad_operativa FLOAT NOT NULL DEFAULT 0.0,
    margen_operativo_porcentaje FLOAT NOT NULL DEFAULT 0.0,
    otros_ingresos FLOAT NOT NULL DEFAULT 0.0,
    otros_gastos FLOAT NOT NULL DEFAULT 0.0,
    intereses FLOAT NOT NULL DEFAULT 0.0,
    impuestos FLOAT NOT NULL DEFAULT 0.0,
    utilidad_neta FLOAT NOT NULL DEFAULT 0.0,
    margen_neto_porcentaje FLOAT NOT NULL DEFAULT 0.0,
    fecha_calculo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    periodo_desde DATE NOT NULL,
    periodo_hasta DATE NOT NULL
);

-- Crear tabla flujo_caja
CREATE TABLE flujo_caja (
    id SERIAL PRIMARY KEY,
    reporte_id INTEGER NOT NULL REFERENCES reportes_financieros(id),
    ingresos_operativos FLOAT NOT NULL DEFAULT 0.0,
    pagos_proveedores FLOAT NOT NULL DEFAULT 0.0,
    pagos_empleados FLOAT NOT NULL DEFAULT 0.0,
    pagos_impuestos FLOAT NOT NULL DEFAULT 0.0,
    otros_pagos_operativos FLOAT NOT NULL DEFAULT 0.0,
    flujo_operativo FLOAT NOT NULL DEFAULT 0.0,
    compras_activos FLOAT NOT NULL DEFAULT 0.0,
    ventas_activos FLOAT NOT NULL DEFAULT 0.0,
    inversiones FLOAT NOT NULL DEFAULT 0.0,
    flujo_inversion FLOAT NOT NULL DEFAULT 0.0,
    prestamos_recibidos FLOAT NOT NULL DEFAULT 0.0,
    pagos_prestamos FLOAT NOT NULL DEFAULT 0.0,
    dividendos_pagados FLOAT NOT NULL DEFAULT 0.0,
    flujo_financiamiento FLOAT NOT NULL DEFAULT 0.0,
    flujo_caja_neto FLOAT NOT NULL DEFAULT 0.0,
    saldo_caja_inicial FLOAT NOT NULL DEFAULT 0.0,
    saldo_caja_final FLOAT NOT NULL DEFAULT 0.0,
    fecha_calculo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    periodo_desde DATE NOT NULL,
    periodo_hasta DATE NOT NULL
);

-- Crear tabla analisis_rentabilidad
CREATE TABLE analisis_rentabilidad (
    id SERIAL PRIMARY KEY,
    reporte_id INTEGER NOT NULL REFERENCES reportes_financieros(id),
    tipo_entidad VARCHAR(50) NOT NULL,
    entidad_id INTEGER NOT NULL,
    entidad_nombre VARCHAR(255) NOT NULL,
    ingresos_totales FLOAT NOT NULL DEFAULT 0.0,
    costos_totales FLOAT NOT NULL DEFAULT 0.0,
    utilidad_bruta FLOAT NOT NULL DEFAULT 0.0,
    margen_bruto_porcentaje FLOAT NOT NULL DEFAULT 0.0,
    costo_productos FLOAT NOT NULL DEFAULT 0.0,
    costo_mano_obra FLOAT NOT NULL DEFAULT 0.0,
    costo_overhead FLOAT NOT NULL DEFAULT 0.0,
    costo_marketing FLOAT NOT NULL DEFAULT 0.0,
    cantidad_vendida FLOAT NOT NULL DEFAULT 0.0,
    precio_promedio FLOAT NOT NULL DEFAULT 0.0,
    ticket_promedio FLOAT NOT NULL DEFAULT 0.0,
    rotacion_inventario FLOAT,
    dias_inventario FLOAT,
    rentabilidad_sobre_ventas FLOAT,
    rentabilidad_sobre_inversion FLOAT,
    fecha_calculo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    periodo_desde DATE NOT NULL,
    periodo_hasta DATE NOT NULL,
    ranking INTEGER
);

-- Crear índices para analisis_rentabilidad
CREATE INDEX ix_analisis_rentabilidad_id ON analisis_rentabilidad(id);
CREATE INDEX ix_analisis_rentabilidad_tipo_entidad ON analisis_rentabilidad(tipo_entidad);
CREATE INDEX ix_analisis_rentabilidad_entidad_id ON analisis_rentabilidad(entidad_id);

-- Crear tabla proyecciones_financieras
CREATE TABLE proyecciones_financieras (
    id SERIAL PRIMARY KEY,
    reporte_id INTEGER NOT NULL REFERENCES reportes_financieros(id),
    tipo_proyeccion VARCHAR(50) NOT NULL,
    horizonte_meses INTEGER NOT NULL DEFAULT 12,
    metodo_calculo VARCHAR(50) NOT NULL,
    periodo_historico_desde DATE NOT NULL,
    periodo_historico_hasta DATE NOT NULL,
    valor_historico_promedio FLOAT NOT NULL DEFAULT 0.0,
    tendencia_porcentaje FLOAT,
    proyeccion_mes_1 FLOAT,
    proyeccion_mes_2 FLOAT,
    proyeccion_mes_3 FLOAT,
    proyeccion_mes_6 FLOAT,
    proyeccion_mes_12 FLOAT,
    factor_estacional FLOAT DEFAULT 1.0,
    factor_crecimiento FLOAT DEFAULT 1.0,
    factor_inflacion FLOAT DEFAULT 1.0,
    confianza_porcentaje FLOAT DEFAULT 80.0,
    margen_error FLOAT,
    fecha_calculo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    creado_por INTEGER REFERENCES users(id),
    activo BOOLEAN DEFAULT TRUE
);

-- Crear índices para proyecciones_financieras
CREATE INDEX ix_proyecciones_financieras_id ON proyecciones_financieras(id);
CREATE INDEX ix_proyecciones_financieras_tipo_proyeccion ON proyecciones_financieras(tipo_proyeccion);
CREATE INDEX ix_proyecciones_financieras_activo ON proyecciones_financieras(activo);

-- Crear tabla metricas_financieras
CREATE TABLE metricas_financieras (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    tipo_valor VARCHAR(50) NOT NULL,
    valor_actual FLOAT NOT NULL,
    valor_anterior FLOAT,
    valor_objetivo FLOAT,
    variacion_porcentaje FLOAT,
    fecha_calculo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    periodo_desde DATE NOT NULL,
    periodo_hasta DATE NOT NULL,
    descripcion TEXT,
    formula TEXT,
    fuente_datos VARCHAR(255),
    calculado_por INTEGER REFERENCES users(id)
);

-- Crear índices para metricas_financieras
CREATE INDEX ix_metricas_financieras_id ON metricas_financieras(id);
CREATE INDEX ix_metricas_financieras_nombre ON metricas_financieras(nombre);
CREATE INDEX ix_metricas_financieras_categoria ON metricas_financieras(categoria);
CREATE INDEX ix_metricas_financieras_fecha_calculo ON metricas_financieras(fecha_calculo);

