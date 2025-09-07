# app/schemas/reporte_financiero_schema.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from app.models.reporte_financiero_model import TipoReporteFinanciero, PeriodoReporte, EstadoReporte

# === ESQUEMAS BASE ===

class ReporteFinancieroBase(BaseModel):
    """Esquema base para reportes financieros"""
    nombre: str = Field(..., max_length=255, description="Nombre del reporte")
    tipo: TipoReporteFinanciero = Field(..., description="Tipo de reporte")
    periodo: PeriodoReporte = Field(..., description="Período del reporte")
    fecha_inicio: date = Field(..., description="Fecha de inicio del reporte")
    fecha_fin: date = Field(..., description="Fecha de fin del reporte")
    incluir_detalles: bool = Field(True, description="Incluir detalles en el reporte")
    incluir_proyecciones: bool = Field(False, description="Incluir proyecciones")
    incluir_comparaciones: bool = Field(False, description="Incluir comparaciones")
    formato_salida: str = Field("json", description="Formato de salida del reporte")
    descripcion: Optional[str] = Field(None, description="Descripción del reporte")
    parametros_personalizados: Optional[Dict[str, Any]] = Field(None, description="Parámetros personalizados")

    @validator('fecha_fin')
    def validar_fecha_fin(cls, v, values):
        if v and 'fecha_inicio' in values and v <= values['fecha_inicio']:
            raise ValueError('La fecha de fin debe ser posterior a la fecha de inicio')
        return v

    @validator('formato_salida')
    def validar_formato_salida(cls, v):
        formatos_validos = ['json', 'pdf', 'excel', 'csv']
        if v not in formatos_validos:
            raise ValueError(f'Formato de salida debe ser uno de: {formatos_validos}')
        return v

class ReporteFinancieroCreate(ReporteFinancieroBase):
    """Esquema para crear reportes financieros"""
    filtro_productos: Optional[List[int]] = Field(None, description="IDs de productos a incluir")
    filtro_clientes: Optional[List[int]] = Field(None, description="IDs de clientes a incluir")
    filtro_categorias: Optional[List[int]] = Field(None, description="IDs de categorías a incluir")
    filtro_proveedores: Optional[List[int]] = Field(None, description="IDs de proveedores a incluir")

class ReporteFinancieroUpdate(BaseModel):
    """Esquema para actualizar reportes financieros"""
    nombre: Optional[str] = Field(None, max_length=255)
    descripcion: Optional[str] = None
    parametros_personalizados: Optional[Dict[str, Any]] = None
    incluir_detalles: Optional[bool] = None
    incluir_proyecciones: Optional[bool] = None
    incluir_comparaciones: Optional[bool] = None
    formato_salida: Optional[str] = None

class ReporteFinancieroOut(ReporteFinancieroBase):
    """Esquema de salida para reportes financieros"""
    id: int
    estado: EstadoReporte
    fecha_generacion: datetime
    fecha_expiracion: Optional[datetime] = None
    creado_por: Optional[int] = None
    archivo_ruta: Optional[str] = None
    tamaño_archivo: Optional[int] = None
    total_ingresos: Optional[float] = None
    total_costos: Optional[float] = None
    total_gastos: Optional[float] = None
    ganancia_neta: Optional[float] = None
    margen_bruto: Optional[float] = None
    margen_neto: Optional[float] = None
    
    class Config:
        from_attributes = True

# === ESTADO DE RESULTADOS ===

class EstadoResultadosBase(BaseModel):
    """Esquema base para estado de resultados"""
    ventas_brutas: float = Field(0.0, ge=0, description="Ventas brutas")
    descuentos_ventas: float = Field(0.0, ge=0, description="Descuentos en ventas")
    devoluciones_ventas: float = Field(0.0, ge=0, description="Devoluciones de ventas")
    inventario_inicial: float = Field(0.0, ge=0, description="Inventario inicial")
    compras: float = Field(0.0, ge=0, description="Compras realizadas")
    inventario_final: float = Field(0.0, ge=0, description="Inventario final")
    gastos_administrativos: float = Field(0.0, ge=0, description="Gastos administrativos")
    gastos_ventas: float = Field(0.0, ge=0, description="Gastos de ventas")
    gastos_generales: float = Field(0.0, ge=0, description="Gastos generales")
    otros_ingresos: float = Field(0.0, ge=0, description="Otros ingresos")
    otros_gastos: float = Field(0.0, ge=0, description="Otros gastos")
    intereses: float = Field(0.0, description="Intereses")
    impuestos: float = Field(0.0, ge=0, description="Impuestos")

class EstadoResultadosCreate(EstadoResultadosBase):
    """Esquema para crear estado de resultados"""
    reporte_id: int = Field(..., description="ID del reporte financiero")
    periodo_desde: date = Field(..., description="Período desde")
    periodo_hasta: date = Field(..., description="Período hasta")

class EstadoResultadosOut(EstadoResultadosBase):
    """Esquema de salida para estado de resultados"""
    id: int
    reporte_id: int
    ventas_netas: float
    costo_ventas: float
    utilidad_bruta: float
    margen_bruto_porcentaje: float
    total_gastos_operativos: float
    utilidad_operativa: float
    margen_operativo_porcentaje: float
    utilidad_neta: float
    margen_neto_porcentaje: float
    fecha_calculo: datetime
    periodo_desde: date
    periodo_hasta: date
    
    class Config:
        from_attributes = True

# === FLUJO DE CAJA ===

class FlujoCajaBase(BaseModel):
    """Esquema base para flujo de caja"""
    ingresos_operativos: float = Field(0.0, ge=0, description="Ingresos operativos")
    pagos_proveedores: float = Field(0.0, ge=0, description="Pagos a proveedores")
    pagos_empleados: float = Field(0.0, ge=0, description="Pagos a empleados")
    pagos_impuestos: float = Field(0.0, ge=0, description="Pagos de impuestos")
    otros_pagos_operativos: float = Field(0.0, ge=0, description="Otros pagos operativos")
    compras_activos: float = Field(0.0, ge=0, description="Compras de activos")
    ventas_activos: float = Field(0.0, ge=0, description="Ventas de activos")
    inversiones: float = Field(0.0, description="Inversiones")
    prestamos_recibidos: float = Field(0.0, ge=0, description="Préstamos recibidos")
    pagos_prestamos: float = Field(0.0, ge=0, description="Pagos de préstamos")
    dividendos_pagados: float = Field(0.0, ge=0, description="Dividendos pagados")
    saldo_caja_inicial: float = Field(0.0, ge=0, description="Saldo de caja inicial")

class FlujoCajaCreate(FlujoCajaBase):
    """Esquema para crear flujo de caja"""
    reporte_id: int = Field(..., description="ID del reporte financiero")
    periodo_desde: date = Field(..., description="Período desde")
    periodo_hasta: date = Field(..., description="Período hasta")

class FlujoCajaOut(FlujoCajaBase):
    """Esquema de salida para flujo de caja"""
    id: int
    reporte_id: int
    flujo_operativo: float
    flujo_inversion: float
    flujo_financiamiento: float
    flujo_caja_neto: float
    saldo_caja_final: float
    fecha_calculo: datetime
    periodo_desde: date
    periodo_hasta: date
    
    class Config:
        from_attributes = True

# === ANÁLISIS DE RENTABILIDAD ===

class AnalisisRentabilidadBase(BaseModel):
    """Esquema base para análisis de rentabilidad"""
    tipo_entidad: str = Field(..., description="Tipo de entidad (producto, cliente, categoria, proveedor)")
    entidad_id: int = Field(..., description="ID de la entidad")
    entidad_nombre: str = Field(..., max_length=255, description="Nombre de la entidad")
    ingresos_totales: float = Field(0.0, ge=0, description="Ingresos totales")
    costos_totales: float = Field(0.0, ge=0, description="Costos totales")
    costo_productos: float = Field(0.0, ge=0, description="Costo de productos")
    costo_mano_obra: float = Field(0.0, ge=0, description="Costo de mano de obra")
    costo_overhead: float = Field(0.0, ge=0, description="Costo overhead")
    costo_marketing: float = Field(0.0, ge=0, description="Costo de marketing")
    cantidad_vendida: float = Field(0.0, ge=0, description="Cantidad vendida")
    precio_promedio: float = Field(0.0, ge=0, description="Precio promedio")

    @validator('tipo_entidad')
    def validar_tipo_entidad(cls, v):
        tipos_validos = ['producto', 'cliente', 'categoria', 'proveedor']
        if v not in tipos_validos:
            raise ValueError(f'Tipo de entidad debe ser uno de: {tipos_validos}')
        return v

class AnalisisRentabilidadCreate(AnalisisRentabilidadBase):
    """Esquema para crear análisis de rentabilidad"""
    reporte_id: int = Field(..., description="ID del reporte financiero")
    periodo_desde: date = Field(..., description="Período desde")
    periodo_hasta: date = Field(..., description="Período hasta")

class AnalisisRentabilidadOut(AnalisisRentabilidadBase):
    """Esquema de salida para análisis de rentabilidad"""
    id: int
    reporte_id: int
    utilidad_bruta: float
    margen_bruto_porcentaje: float
    ticket_promedio: float
    rotacion_inventario: Optional[float] = None
    dias_inventario: Optional[float] = None
    rentabilidad_sobre_ventas: Optional[float] = None
    rentabilidad_sobre_inversion: Optional[float] = None
    ranking: Optional[int] = None
    fecha_calculo: datetime
    periodo_desde: date
    periodo_hasta: date
    
    class Config:
        from_attributes = True

# === PROYECCIONES FINANCIERAS ===

class ProyeccionFinancieraBase(BaseModel):
    """Esquema base para proyecciones financieras"""
    tipo_proyeccion: str = Field(..., description="Tipo de proyección")
    horizonte_meses: int = Field(12, ge=1, le=60, description="Horizonte en meses")
    metodo_calculo: str = Field(..., description="Método de cálculo")
    periodo_historico_desde: date = Field(..., description="Período histórico desde")
    periodo_historico_hasta: date = Field(..., description="Período histórico hasta")
    factor_estacional: float = Field(1.0, ge=0, le=5.0, description="Factor estacional")
    factor_crecimiento: float = Field(1.0, ge=0, le=5.0, description="Factor de crecimiento")
    factor_inflacion: float = Field(1.0, ge=0, le=5.0, description="Factor de inflación")
    confianza_porcentaje: float = Field(80.0, ge=0, le=100, description="Nivel de confianza")

    @validator('tipo_proyeccion')
    def validar_tipo_proyeccion(cls, v):
        tipos_validos = ['ventas', 'costos', 'utilidad', 'flujo_caja']
        if v not in tipos_validos:
            raise ValueError(f'Tipo de proyección debe ser uno de: {tipos_validos}')
        return v

    @validator('metodo_calculo')
    def validar_metodo_calculo(cls, v):
        metodos_validos = ['tendencia', 'estacional', 'regresion', 'manual']
        if v not in metodos_validos:
            raise ValueError(f'Método de cálculo debe ser uno de: {metodos_validos}')
        return v

class ProyeccionFinancieraCreate(ProyeccionFinancieraBase):
    """Esquema para crear proyecciones financieras"""
    reporte_id: int = Field(..., description="ID del reporte financiero")

class ProyeccionFinancieraOut(ProyeccionFinancieraBase):
    """Esquema de salida para proyecciones financieras"""
    id: int
    reporte_id: int
    valor_historico_promedio: float
    tendencia_porcentaje: Optional[float] = None
    proyeccion_mes_1: Optional[float] = None
    proyeccion_mes_2: Optional[float] = None
    proyeccion_mes_3: Optional[float] = None
    proyeccion_mes_6: Optional[float] = None
    proyeccion_mes_12: Optional[float] = None
    margen_error: Optional[float] = None
    fecha_calculo: datetime
    creado_por: Optional[int] = None
    activo: bool
    
    class Config:
        from_attributes = True

# === MÉTRICAS FINANCIERAS ===

class MetricaFinancieraBase(BaseModel):
    """Esquema base para métricas financieras"""
    nombre: str = Field(..., max_length=255, description="Nombre de la métrica")
    categoria: str = Field(..., max_length=100, description="Categoría de la métrica")
    tipo_valor: str = Field(..., description="Tipo de valor")
    valor_actual: float = Field(..., description="Valor actual")
    valor_objetivo: Optional[float] = Field(None, description="Valor objetivo")
    descripcion: Optional[str] = Field(None, description="Descripción de la métrica")
    formula: Optional[str] = Field(None, description="Fórmula de cálculo")
    fuente_datos: Optional[str] = Field(None, max_length=255, description="Fuente de datos")

    @validator('categoria')
    def validar_categoria(cls, v):
        categorias_validas = ['rentabilidad', 'liquidez', 'eficiencia', 'crecimiento']
        if v not in categorias_validas:
            raise ValueError(f'Categoría debe ser una de: {categorias_validas}')
        return v

    @validator('tipo_valor')
    def validar_tipo_valor(cls, v):
        tipos_validos = ['porcentaje', 'monto', 'ratio', 'indice']
        if v not in tipos_validos:
            raise ValueError(f'Tipo de valor debe ser uno de: {tipos_validos}')
        return v

class MetricaFinancieraCreate(MetricaFinancieraBase):
    """Esquema para crear métricas financieras"""
    periodo_desde: date = Field(..., description="Período desde")
    periodo_hasta: date = Field(..., description="Período hasta")

class MetricaFinancieraOut(MetricaFinancieraBase):
    """Esquema de salida para métricas financieras"""
    id: int
    valor_anterior: Optional[float] = None
    variacion_porcentaje: Optional[float] = None
    fecha_calculo: datetime
    periodo_desde: date
    periodo_hasta: date
    calculado_por: Optional[int] = None
    
    class Config:
        from_attributes = True

# === ESQUEMAS DE CONSULTA Y FILTROS ===

class ReporteFiltros(BaseModel):
    """Filtros para consultar reportes"""
    tipo: Optional[TipoReporteFinanciero] = Field(None, description="Filtrar por tipo")
    periodo: Optional[PeriodoReporte] = Field(None, description="Filtrar por período")
    estado: Optional[EstadoReporte] = Field(None, description="Filtrar por estado")
    fecha_desde: Optional[date] = Field(None, description="Fecha desde")
    fecha_hasta: Optional[date] = Field(None, description="Fecha hasta")
    creado_por: Optional[int] = Field(None, description="Filtrar por creador")
    solo_activos: bool = Field(True, description="Solo reportes activos")

class ReporteResumen(BaseModel):
    """Resumen de reportes financieros"""
    total_reportes: int
    reportes_por_tipo: Dict[str, int]
    reportes_por_estado: Dict[str, int]
    reportes_por_periodo: Dict[str, int]
    ultimo_reporte: Optional[datetime] = None
    reporte_mas_reciente: Optional[str] = None
    total_ingresos_mes: float
    total_costos_mes: float
    ganancia_neta_mes: float
    margen_bruto_promedio: float

class DashboardFinanciero(BaseModel):
    """Dashboard financiero en tiempo real"""
    # Métricas principales
    ingresos_mes_actual: float
    ingresos_mes_anterior: float
    crecimiento_ingresos: float
    
    costos_mes_actual: float
    costos_mes_anterior: float
    crecimiento_costos: float
    
    utilidad_neta_mes: float
    utilidad_neta_anterior: float
    crecimiento_utilidad: float
    
    # Ratios clave
    margen_bruto: float
    margen_neto: float
    rotacion_inventario: float
    dias_cobro_promedio: float
    dias_pago_promedio: float
    
    # Proyecciones
    proyeccion_ventas_3_meses: float
    proyeccion_utilidad_3_meses: float
    tendencia_crecimiento: str  # "creciente", "decreciente", "estable"
    
    # Alertas
    alertas: List[Dict[str, Any]] = []
    
    # Top performers
    top_productos_rentables: List[Dict[str, Any]] = []
    top_clientes_rentables: List[Dict[str, Any]] = []
    categorias_mas_rentables: List[Dict[str, Any]] = []

class ReporteComparativo(BaseModel):
    """Reporte comparativo entre períodos"""
    periodo_actual: Dict[str, Any]
    periodo_anterior: Dict[str, Any]
    variaciones: Dict[str, float]  # Variaciones en porcentaje
    tendencias: Dict[str, str]  # "creciente", "decreciente", "estable"
    recomendaciones: List[str] = []

class ExportacionReporte(BaseModel):
    """Configuración para exportar reportes"""
    formato: str = Field(..., description="Formato de exportación")
    incluir_graficos: bool = Field(True, description="Incluir gráficos")
    incluir_detalles: bool = Field(True, description="Incluir detalles")
    incluir_comparaciones: bool = Field(False, description="Incluir comparaciones")
    idioma: str = Field("es", description="Idioma del reporte")
    moneda: str = Field("ARS", description="Moneda del reporte")

