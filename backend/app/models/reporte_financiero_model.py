# app/models/reporte_financiero_model.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Date, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, date
from enum import Enum as PyEnum
from app.db.database import Base

class TipoReporteFinanciero(str, PyEnum):
    """Tipos de reportes financieros"""
    ESTADO_RESULTADOS = "estado_resultados"
    FLUJO_CAJA = "flujo_caja"
    RENTABILIDAD = "rentabilidad"
    PROYECCION = "proyeccion"
    DASHBOARD = "dashboard"
    ANALISIS_COSTOS = "analisis_costos"
    MARGEN_BRUTO = "margen_bruto"
    ROTACION_INVENTARIO = "rotacion_inventario"

class PeriodoReporte(str, PyEnum):
    """Períodos de reporte"""
    DIARIO = "diario"
    SEMANAL = "semanal"
    MENSUAL = "mensual"
    TRIMESTRAL = "trimestral"
    ANUAL = "anual"
    PERSONALIZADO = "personalizado"

class EstadoReporte(str, PyEnum):
    """Estados de los reportes"""
    GENERANDO = "generando"
    COMPLETADO = "completado"
    ERROR = "error"
    EXPIRADO = "expirado"

class ReporteFinanciero(Base):
    __tablename__ = "reportes_financieros"

    id = Column(Integer, primary_key=True, index=True)
    
    # Configuración del reporte
    nombre = Column(String(255), nullable=False, index=True)
    tipo = Column(Enum(TipoReporteFinanciero), nullable=False, index=True)
    periodo = Column(Enum(PeriodoReporte), nullable=False, index=True)
    estado = Column(Enum(EstadoReporte), default=EstadoReporte.GENERANDO, index=True)
    
    # Fechas del reporte
    fecha_inicio = Column(Date, nullable=False, index=True)
    fecha_fin = Column(Date, nullable=False, index=True)
    fecha_generacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_expiracion = Column(DateTime, nullable=True, index=True)
    
    # Configuración específica
    incluir_detalles = Column(Boolean, default=True)
    incluir_proyecciones = Column(Boolean, default=False)
    incluir_comparaciones = Column(Boolean, default=False)
    formato_salida = Column(String(50), default="json")  # json, pdf, excel, csv
    
    # Filtros aplicados
    filtro_productos = Column(Text, nullable=True)  # JSON con IDs de productos
    filtro_clientes = Column(Text, nullable=True)  # JSON con IDs de clientes
    filtro_categorias = Column(Text, nullable=True)  # JSON con IDs de categorías
    filtro_proveedores = Column(Text, nullable=True)  # JSON con IDs de proveedores
    
    # Metadatos
    descripcion = Column(Text, nullable=True)
    parametros_personalizados = Column(Text, nullable=True)  # JSON con parámetros adicionales
    creado_por = Column(Integer, ForeignKey("users.id"), nullable=True)
    archivo_ruta = Column(String(500), nullable=True)  # Ruta del archivo generado
    tamaño_archivo = Column(Integer, nullable=True)  # Tamaño en bytes
    
    # Resultados del reporte
    total_ingresos = Column(Float, nullable=True)
    total_costos = Column(Float, nullable=True)
    total_gastos = Column(Float, nullable=True)
    ganancia_neta = Column(Float, nullable=True)
    margen_bruto = Column(Float, nullable=True)
    margen_neto = Column(Float, nullable=True)
    
    # Relaciones
    creador = relationship("User", backref="reportes_financieros_creados")
    
    def __repr__(self):
        return f"<ReporteFinanciero(id={self.id}, nombre='{self.nombre}', tipo='{self.tipo}', estado='{self.estado}')>"

class EstadoResultados(Base):
    __tablename__ = "estado_resultados"

    id = Column(Integer, primary_key=True, index=True)
    reporte_id = Column(Integer, ForeignKey("reportes_financieros.id"), nullable=False, index=True)
    
    # Ingresos
    ventas_brutas = Column(Float, nullable=False, default=0.0)
    descuentos_ventas = Column(Float, nullable=False, default=0.0)
    devoluciones_ventas = Column(Float, nullable=False, default=0.0)
    ventas_netas = Column(Float, nullable=False, default=0.0)
    
    # Costo de ventas
    inventario_inicial = Column(Float, nullable=False, default=0.0)
    compras = Column(Float, nullable=False, default=0.0)
    inventario_final = Column(Float, nullable=False, default=0.0)
    costo_ventas = Column(Float, nullable=False, default=0.0)
    
    # Utilidad bruta
    utilidad_bruta = Column(Float, nullable=False, default=0.0)
    margen_bruto_porcentaje = Column(Float, nullable=False, default=0.0)
    
    # Gastos operativos
    gastos_administrativos = Column(Float, nullable=False, default=0.0)
    gastos_ventas = Column(Float, nullable=False, default=0.0)
    gastos_generales = Column(Float, nullable=False, default=0.0)
    total_gastos_operativos = Column(Float, nullable=False, default=0.0)
    
    # Utilidad operativa
    utilidad_operativa = Column(Float, nullable=False, default=0.0)
    margen_operativo_porcentaje = Column(Float, nullable=False, default=0.0)
    
    # Otros ingresos/gastos
    otros_ingresos = Column(Float, nullable=False, default=0.0)
    otros_gastos = Column(Float, nullable=False, default=0.0)
    intereses = Column(Float, nullable=False, default=0.0)
    impuestos = Column(Float, nullable=False, default=0.0)
    
    # Utilidad neta
    utilidad_neta = Column(Float, nullable=False, default=0.0)
    margen_neto_porcentaje = Column(Float, nullable=False, default=0.0)
    
    # Metadatos
    fecha_calculo = Column(DateTime, default=datetime.utcnow, nullable=False)
    periodo_desde = Column(Date, nullable=False)
    periodo_hasta = Column(Date, nullable=False)
    
    # Relaciones
    reporte = relationship("ReporteFinanciero", backref="estado_resultados")
    
    def __repr__(self):
        return f"<EstadoResultados(id={self.id}, utilidad_neta={self.utilidad_neta}, margen_neto={self.margen_neto_porcentaje}%)>"

class FlujoCaja(Base):
    __tablename__ = "flujo_caja"

    id = Column(Integer, primary_key=True, index=True)
    reporte_id = Column(Integer, ForeignKey("reportes_financieros.id"), nullable=False, index=True)
    
    # Flujo de caja operativo
    ingresos_operativos = Column(Float, nullable=False, default=0.0)
    pagos_proveedores = Column(Float, nullable=False, default=0.0)
    pagos_empleados = Column(Float, nullable=False, default=0.0)
    pagos_impuestos = Column(Float, nullable=False, default=0.0)
    otros_pagos_operativos = Column(Float, nullable=False, default=0.0)
    flujo_operativo = Column(Float, nullable=False, default=0.0)
    
    # Flujo de caja de inversión
    compras_activos = Column(Float, nullable=False, default=0.0)
    ventas_activos = Column(Float, nullable=False, default=0.0)
    inversiones = Column(Float, nullable=False, default=0.0)
    flujo_inversion = Column(Float, nullable=False, default=0.0)
    
    # Flujo de caja de financiamiento
    prestamos_recibidos = Column(Float, nullable=False, default=0.0)
    pagos_prestamos = Column(Float, nullable=False, default=0.0)
    dividendos_pagados = Column(Float, nullable=False, default=0.0)
    flujo_financiamiento = Column(Float, nullable=False, default=0.0)
    
    # Flujo de caja neto
    flujo_caja_neto = Column(Float, nullable=False, default=0.0)
    saldo_caja_inicial = Column(Float, nullable=False, default=0.0)
    saldo_caja_final = Column(Float, nullable=False, default=0.0)
    
    # Metadatos
    fecha_calculo = Column(DateTime, default=datetime.utcnow, nullable=False)
    periodo_desde = Column(Date, nullable=False)
    periodo_hasta = Column(Date, nullable=False)
    
    # Relaciones
    reporte = relationship("ReporteFinanciero", backref="flujo_caja")
    
    def __repr__(self):
        return f"<FlujoCaja(id={self.id}, flujo_neto={self.flujo_caja_neto}, saldo_final={self.saldo_caja_final})>"

class AnalisisRentabilidad(Base):
    __tablename__ = "analisis_rentabilidad"

    id = Column(Integer, primary_key=True, index=True)
    reporte_id = Column(Integer, ForeignKey("reportes_financieros.id"), nullable=False, index=True)
    
    # Identificación del análisis
    tipo_entidad = Column(String(50), nullable=False, index=True)  # producto, cliente, categoria, proveedor
    entidad_id = Column(Integer, nullable=False, index=True)
    entidad_nombre = Column(String(255), nullable=False)
    
    # Métricas de rentabilidad
    ingresos_totales = Column(Float, nullable=False, default=0.0)
    costos_totales = Column(Float, nullable=False, default=0.0)
    utilidad_bruta = Column(Float, nullable=False, default=0.0)
    margen_bruto_porcentaje = Column(Float, nullable=False, default=0.0)
    
    # Costos específicos
    costo_productos = Column(Float, nullable=False, default=0.0)
    costo_mano_obra = Column(Float, nullable=False, default=0.0)
    costo_overhead = Column(Float, nullable=False, default=0.0)
    costo_marketing = Column(Float, nullable=False, default=0.0)
    
    # Métricas de volumen
    cantidad_vendida = Column(Float, nullable=False, default=0.0)
    precio_promedio = Column(Float, nullable=False, default=0.0)
    ticket_promedio = Column(Float, nullable=False, default=0.0)
    
    # Métricas de eficiencia
    rotacion_inventario = Column(Float, nullable=True)
    dias_inventario = Column(Float, nullable=True)
    rentabilidad_sobre_ventas = Column(Float, nullable=True)
    rentabilidad_sobre_inversion = Column(Float, nullable=True)
    
    # Metadatos
    fecha_calculo = Column(DateTime, default=datetime.utcnow, nullable=False)
    periodo_desde = Column(Date, nullable=False)
    periodo_hasta = Column(Date, nullable=False)
    ranking = Column(Integer, nullable=True)  # Ranking de rentabilidad
    
    # Relaciones
    reporte = relationship("ReporteFinanciero", backref="analisis_rentabilidad")
    
    def __repr__(self):
        return f"<AnalisisRentabilidad(id={self.id}, entidad='{self.entidad_nombre}', margen={self.margen_bruto_porcentaje}%)>"

class ProyeccionFinanciera(Base):
    __tablename__ = "proyecciones_financieras"

    id = Column(Integer, primary_key=True, index=True)
    reporte_id = Column(Integer, ForeignKey("reportes_financieros.id"), nullable=False, index=True)
    
    # Configuración de la proyección
    tipo_proyeccion = Column(String(50), nullable=False, index=True)  # ventas, costos, utilidad, flujo_caja
    horizonte_meses = Column(Integer, nullable=False, default=12)
    metodo_calculo = Column(String(50), nullable=False)  # tendencia, estacional, regresion, manual
    
    # Datos históricos
    periodo_historico_desde = Column(Date, nullable=False)
    periodo_historico_hasta = Column(Date, nullable=False)
    valor_historico_promedio = Column(Float, nullable=False, default=0.0)
    tendencia_porcentaje = Column(Float, nullable=True)  # Tendencia mensual
    
    # Proyecciones por mes
    proyeccion_mes_1 = Column(Float, nullable=True)
    proyeccion_mes_2 = Column(Float, nullable=True)
    proyeccion_mes_3 = Column(Float, nullable=True)
    proyeccion_mes_6 = Column(Float, nullable=True)
    proyeccion_mes_12 = Column(Float, nullable=True)
    
    # Factores de ajuste
    factor_estacional = Column(Float, nullable=True, default=1.0)
    factor_crecimiento = Column(Float, nullable=True, default=1.0)
    factor_inflacion = Column(Float, nullable=True, default=1.0)
    
    # Nivel de confianza
    confianza_porcentaje = Column(Float, nullable=True, default=80.0)
    margen_error = Column(Float, nullable=True)
    
    # Metadatos
    fecha_calculo = Column(DateTime, default=datetime.utcnow, nullable=False)
    creado_por = Column(Integer, ForeignKey("users.id"), nullable=True)
    activo = Column(Boolean, default=True, index=True)
    
    # Relaciones
    reporte = relationship("ReporteFinanciero", backref="proyecciones_financieras")
    creador = relationship("User", backref="proyecciones_creadas")
    
    def __repr__(self):
        return f"<ProyeccionFinanciera(id={self.id}, tipo='{self.tipo_proyeccion}', horizonte={self.horizonte_meses} meses)>"

class MetricaFinanciera(Base):
    __tablename__ = "metricas_financieras"

    id = Column(Integer, primary_key=True, index=True)
    
    # Identificación de la métrica
    nombre = Column(String(255), nullable=False, index=True)
    categoria = Column(String(100), nullable=False, index=True)  # rentabilidad, liquidez, eficiencia, crecimiento
    tipo_valor = Column(String(50), nullable=False)  # porcentaje, monto, ratio, indice
    
    # Valor de la métrica
    valor_actual = Column(Float, nullable=False)
    valor_anterior = Column(Float, nullable=True)
    valor_objetivo = Column(Float, nullable=True)
    variacion_porcentaje = Column(Float, nullable=True)
    
    # Contexto temporal
    fecha_calculo = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    periodo_desde = Column(Date, nullable=False)
    periodo_hasta = Column(Date, nullable=False)
    
    # Metadatos
    descripcion = Column(Text, nullable=True)
    formula = Column(Text, nullable=True)  # Fórmula de cálculo
    fuente_datos = Column(String(255), nullable=True)
    calculado_por = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relaciones
    calculador = relationship("User", backref="metricas_calculadas")
    
    def __repr__(self):
        return f"<MetricaFinanciera(id={self.id}, nombre='{self.nombre}', valor={self.valor_actual})>"

