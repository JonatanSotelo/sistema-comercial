# app/schemas/metricas_rendimiento_schema.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date
from app.models.metricas_rendimiento_model import (
    TipoMetrica, CategoriaMetrica, TipoCalculo, FrecuenciaMedicion,
    EstadoAlerta, TipoAlerta
)

# === ESQUEMAS BASE ===

class MetricaRendimientoBase(BaseModel):
    """Esquema base para métricas de rendimiento"""
    nombre: str = Field(..., max_length=255, description="Nombre de la métrica")
    codigo: str = Field(..., max_length=100, description="Código único de la métrica")
    descripcion: Optional[str] = Field(None, description="Descripción de la métrica")
    tipo_metrica: TipoMetrica = Field(..., description="Tipo de métrica")
    categoria: CategoriaMetrica = Field(..., description="Categoría de la métrica")
    subcategoria: Optional[str] = Field(None, max_length=100, description="Subcategoría")
    tipo_calculo: TipoCalculo = Field(..., description="Tipo de cálculo")
    formula: Optional[str] = Field(None, description="Fórmula de cálculo")
    unidad_medida: Optional[str] = Field(None, max_length=50, description="Unidad de medida")
    decimales: int = Field(2, ge=0, le=10, description="Número de decimales")
    frecuencia_medicion: FrecuenciaMedicion = Field(..., description="Frecuencia de medición")
    fuente_datos: Optional[str] = Field(None, max_length=255, description="Fuente de datos")
    dependencias: Optional[List[int]] = Field(None, description="IDs de métricas dependientes")
    valor_objetivo: Optional[float] = Field(None, description="Valor objetivo")
    valor_minimo: Optional[float] = Field(None, description="Valor mínimo")
    valor_maximo: Optional[float] = Field(None, description="Valor máximo")
    rango_optimo_inicio: Optional[float] = Field(None, description="Inicio del rango óptimo")
    rango_optimo_fin: Optional[float] = Field(None, description="Fin del rango óptimo")
    color_positivo: str = Field("#28a745", pattern=r"^#[0-9A-Fa-f]{6}$", description="Color para valores positivos")
    color_negativo: str = Field("#dc3545", pattern=r"^#[0-9A-Fa-f]{6}$", description="Color para valores negativos")
    color_neutro: str = Field("#6c757d", pattern=r"^#[0-9A-Fa-f]{6}$", description="Color para valores neutros")
    icono: Optional[str] = Field(None, max_length=50, description="Icono de la métrica")
    orden_display: int = Field(0, description="Orden de visualización")

    @validator('codigo')
    def validar_codigo(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('El código debe contener solo letras, números, guiones y guiones bajos')
        return v.upper()

    @validator('rango_optimo_inicio', 'rango_optimo_fin')
    def validar_rango_optimo(cls, v, values):
        if v is not None and 'rango_optimo_inicio' in values and 'rango_optimo_fin' in values:
            inicio = values.get('rango_optimo_inicio')
            fin = values.get('rango_optimo_fin')
            if inicio is not None and fin is not None and inicio >= fin:
                raise ValueError('El inicio del rango óptimo debe ser menor que el fin')
        return v

class MetricaRendimientoCreate(MetricaRendimientoBase):
    """Esquema para crear métricas de rendimiento"""
    pass

class MetricaRendimientoUpdate(BaseModel):
    """Esquema para actualizar métricas de rendimiento"""
    nombre: Optional[str] = Field(None, max_length=255)
    descripcion: Optional[str] = None
    tipo_metrica: Optional[TipoMetrica] = None
    categoria: Optional[CategoriaMetrica] = None
    subcategoria: Optional[str] = Field(None, max_length=100)
    tipo_calculo: Optional[TipoCalculo] = None
    formula: Optional[str] = None
    unidad_medida: Optional[str] = Field(None, max_length=50)
    decimales: Optional[int] = Field(None, ge=0, le=10)
    frecuencia_medicion: Optional[FrecuenciaMedicion] = None
    fuente_datos: Optional[str] = Field(None, max_length=255)
    dependencias: Optional[List[int]] = None
    valor_objetivo: Optional[float] = None
    valor_minimo: Optional[float] = None
    valor_maximo: Optional[float] = None
    rango_optimo_inicio: Optional[float] = None
    rango_optimo_fin: Optional[float] = None
    color_positivo: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    color_negativo: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    color_neutro: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    icono: Optional[str] = Field(None, max_length=50)
    orden_display: Optional[int] = None
    activo: Optional[bool] = None

class MetricaRendimientoOut(MetricaRendimientoBase):
    """Esquema de salida para métricas de rendimiento"""
    id: int
    fecha_creacion: datetime
    fecha_ultima_actualizacion: datetime
    creado_por: Optional[int] = None
    activo: bool
    
    class Config:
        from_attributes = True

# === MEDICIONES DE MÉTRICAS ===

class MedicionMetricaBase(BaseModel):
    """Esquema base para mediciones de métricas"""
    fecha_medicion: datetime = Field(..., description="Fecha de la medición")
    periodo_desde: Optional[datetime] = Field(None, description="Inicio del período")
    periodo_hasta: Optional[datetime] = Field(None, description="Fin del período")
    valor_actual: float = Field(..., description="Valor actual de la métrica")
    valor_anterior: Optional[float] = Field(None, description="Valor anterior")
    valor_objetivo: Optional[float] = Field(None, description="Valor objetivo")
    valor_historico_promedio: Optional[float] = Field(None, description="Promedio histórico")
    variacion_absoluta: Optional[float] = Field(None, description="Variación absoluta")
    variacion_porcentual: Optional[float] = Field(None, description="Variación porcentual")
    tendencia: Optional[str] = Field(None, description="Tendencia: creciente, decreciente, estable")
    velocidad_cambio: Optional[float] = Field(None, description="Velocidad de cambio")
    percentil: Optional[float] = Field(None, ge=0, le=100, description="Percentil")
    ranking: Optional[int] = Field(None, ge=1, description="Ranking")
    desviacion_estandar: Optional[float] = Field(None, ge=0, description="Desviación estándar")
    fuente_datos: Optional[str] = Field(None, max_length=255, description="Fuente de datos")
    observaciones: Optional[str] = Field(None, description="Observaciones")
    contexto: Optional[Dict[str, Any]] = Field(None, description="Contexto adicional")
    factores_influencia: Optional[Dict[str, Any]] = Field(None, description="Factores de influencia")

    @validator('tendencia')
    def validar_tendencia(cls, v):
        if v and v not in ['creciente', 'decreciente', 'estable']:
            raise ValueError('Tendencia debe ser: creciente, decreciente o estable')
        return v

class MedicionMetricaCreate(MedicionMetricaBase):
    """Esquema para crear mediciones de métricas"""
    metrica_id: int = Field(..., description="ID de la métrica")

class MedicionMetricaUpdate(BaseModel):
    """Esquema para actualizar mediciones de métricas"""
    fecha_medicion: Optional[datetime] = None
    periodo_desde: Optional[datetime] = None
    periodo_hasta: Optional[datetime] = None
    valor_actual: Optional[float] = None
    valor_anterior: Optional[float] = None
    valor_objetivo: Optional[float] = None
    valor_historico_promedio: Optional[float] = None
    variacion_absoluta: Optional[float] = None
    variacion_porcentual: Optional[float] = None
    tendencia: Optional[str] = None
    velocidad_cambio: Optional[float] = None
    percentil: Optional[float] = Field(None, ge=0, le=100)
    ranking: Optional[int] = Field(None, ge=1)
    desviacion_estandar: Optional[float] = Field(None, ge=0)
    fuente_datos: Optional[str] = Field(None, max_length=255)
    observaciones: Optional[str] = None
    contexto: Optional[Dict[str, Any]] = None
    factores_influencia: Optional[Dict[str, Any]] = None

class MedicionMetricaOut(MedicionMetricaBase):
    """Esquema de salida para mediciones de métricas"""
    id: int
    metrica_id: int
    fecha_calculo: datetime
    calculado_por: Optional[int] = None
    
    class Config:
        from_attributes = True

# === ALERTAS DE MÉTRICAS ===

class AlertaMetricaBase(BaseModel):
    """Esquema base para alertas de métricas"""
    nombre: str = Field(..., max_length=255, description="Nombre de la alerta")
    descripcion: Optional[str] = Field(None, description="Descripción de la alerta")
    tipo_alerta: TipoAlerta = Field(..., description="Tipo de alerta")
    condicion: str = Field(..., description="Condición para activar la alerta")
    umbral_minimo: Optional[float] = Field(None, description="Umbral mínimo")
    umbral_maximo: Optional[float] = Field(None, description="Umbral máximo")
    umbral_porcentaje: Optional[float] = Field(None, ge=0, le=1000, description="Umbral porcentual")
    ventana_tiempo: Optional[int] = Field(None, ge=1, description="Ventana de tiempo en períodos")
    notificar_email: bool = Field(True, description="Notificar por email")
    notificar_dashboard: bool = Field(True, description="Notificar en dashboard")
    notificar_movil: bool = Field(False, description="Notificar en móvil")
    usuarios_notificar: Optional[List[int]] = Field(None, description="IDs de usuarios a notificar")
    frecuencia_verificacion: FrecuenciaMedicion = Field(FrecuenciaMedicion.DIARIA, description="Frecuencia de verificación")
    max_alertas_por_dia: int = Field(5, ge=1, le=100, description="Máximo de alertas por día")
    cooldown_minutos: int = Field(60, ge=1, le=1440, description="Cooldown entre alertas en minutos")

    @validator('umbral_minimo', 'umbral_maximo')
    def validar_umbrales(cls, v, values):
        if v is not None and 'umbral_minimo' in values and 'umbral_maximo' in values:
            minimo = values.get('umbral_minimo')
            maximo = values.get('umbral_maximo')
            if minimo is not None and maximo is not None and minimo >= maximo:
                raise ValueError('El umbral mínimo debe ser menor que el máximo')
        return v

class AlertaMetricaCreate(AlertaMetricaBase):
    """Esquema para crear alertas de métricas"""
    metrica_id: int = Field(..., description="ID de la métrica")

class AlertaMetricaUpdate(BaseModel):
    """Esquema para actualizar alertas de métricas"""
    nombre: Optional[str] = Field(None, max_length=255)
    descripcion: Optional[str] = None
    tipo_alerta: Optional[TipoAlerta] = None
    condicion: Optional[str] = None
    umbral_minimo: Optional[float] = None
    umbral_maximo: Optional[float] = None
    umbral_porcentaje: Optional[float] = Field(None, ge=0, le=1000)
    ventana_tiempo: Optional[int] = Field(None, ge=1)
    notificar_email: Optional[bool] = None
    notificar_dashboard: Optional[bool] = None
    notificar_movil: Optional[bool] = None
    usuarios_notificar: Optional[List[int]] = None
    frecuencia_verificacion: Optional[FrecuenciaMedicion] = None
    max_alertas_por_dia: Optional[int] = Field(None, ge=1, le=100)
    cooldown_minutos: Optional[int] = Field(None, ge=1, le=1440)
    activo: Optional[bool] = None

class AlertaMetricaOut(AlertaMetricaBase):
    """Esquema de salida para alertas de métricas"""
    id: int
    metrica_id: int
    estado: EstadoAlerta
    fecha_creacion: datetime
    fecha_ultima_activacion: Optional[datetime] = None
    fecha_ultima_verificacion: Optional[datetime] = None
    creado_por: Optional[int] = None
    activo: bool
    total_activaciones: int
    activaciones_resueltas: int
    activaciones_pendientes: int
    
    class Config:
        from_attributes = True

# === ACTIVACIONES DE ALERTAS ===

class ActivacionAlertaBase(BaseModel):
    """Esquema base para activaciones de alertas"""
    valor_que_disparo: float = Field(..., description="Valor que disparó la alerta")
    umbral_disparado: Optional[float] = Field(None, description="Umbral que se disparó")
    mensaje: str = Field(..., description="Mensaje de la alerta")
    severidad: str = Field("media", description="Severidad: baja, media, alta, critica")
    contexto_adicional: Optional[Dict[str, Any]] = Field(None, description="Contexto adicional")
    acciones_tomadas: Optional[Dict[str, Any]] = Field(None, description="Acciones tomadas")

    @validator('severidad')
    def validar_severidad(cls, v):
        if v not in ['baja', 'media', 'alta', 'critica']:
            raise ValueError('Severidad debe ser: baja, media, alta o critica')
        return v

class ActivacionAlertaCreate(ActivacionAlertaBase):
    """Esquema para crear activaciones de alertas"""
    alerta_id: int = Field(..., description="ID de la alerta")
    medicion_id: Optional[int] = Field(None, description="ID de la medición")

class ActivacionAlertaUpdate(BaseModel):
    """Esquema para actualizar activaciones de alertas"""
    estado: Optional[EstadoAlerta] = None
    comentarios_resolucion: Optional[str] = Field(None, description="Comentarios de resolución")
    contexto_adicional: Optional[Dict[str, Any]] = None
    acciones_tomadas: Optional[Dict[str, Any]] = None

class ActivacionAlertaOut(ActivacionAlertaBase):
    """Esquema de salida para activaciones de alertas"""
    id: int
    alerta_id: int
    medicion_id: Optional[int] = None
    fecha_activacion: datetime
    estado: EstadoAlerta
    fecha_resolucion: Optional[datetime] = None
    resuelto_por: Optional[int] = None
    comentarios_resolucion: Optional[str] = None
    notificaciones_enviadas: Optional[Dict[str, Any]] = None
    usuarios_notificados: Optional[List[int]] = None
    
    class Config:
        from_attributes = True

# === BENCHMARKS ===

class BenchmarkMetricaBase(BaseModel):
    """Esquema base para benchmarks de métricas"""
    nombre_benchmark: str = Field(..., max_length=255, description="Nombre del benchmark")
    descripcion: Optional[str] = Field(None, description="Descripción del benchmark")
    fuente: Optional[str] = Field(None, max_length=255, description="Fuente del benchmark")
    sector: Optional[str] = Field(None, max_length=100, description="Sector")
    region: Optional[str] = Field(None, max_length=100, description="Región")
    tamaño_empresa: Optional[str] = Field(None, description="Tamaño de empresa")
    valor_promedio_mercado: Optional[float] = Field(None, description="Valor promedio del mercado")
    valor_percentil_25: Optional[float] = Field(None, description="Percentil 25")
    valor_percentil_50: Optional[float] = Field(None, description="Percentil 50")
    valor_percentil_75: Optional[float] = Field(None, description="Percentil 75")
    valor_percentil_90: Optional[float] = Field(None, description="Percentil 90")
    valor_mejor_practica: Optional[float] = Field(None, description="Valor de mejor práctica")
    fecha_inicio_benchmark: Optional[date] = Field(None, description="Fecha de inicio del benchmark")
    fecha_fin_benchmark: Optional[date] = Field(None, description="Fecha de fin del benchmark")
    tamaño_muestra: Optional[int] = Field(None, ge=1, description="Tamaño de la muestra")

    @validator('tamaño_empresa')
    def validar_tamaño_empresa(cls, v):
        if v and v not in ['pequeña', 'mediana', 'grande']:
            raise ValueError('Tamaño de empresa debe ser: pequeña, mediana o grande')
        return v

class BenchmarkMetricaCreate(BenchmarkMetricaBase):
    """Esquema para crear benchmarks de métricas"""
    metrica_id: int = Field(..., description="ID de la métrica")

class BenchmarkMetricaUpdate(BaseModel):
    """Esquema para actualizar benchmarks de métricas"""
    nombre_benchmark: Optional[str] = Field(None, max_length=255)
    descripcion: Optional[str] = None
    fuente: Optional[str] = Field(None, max_length=255)
    sector: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=100)
    tamaño_empresa: Optional[str] = None
    valor_promedio_mercado: Optional[float] = None
    valor_percentil_25: Optional[float] = None
    valor_percentil_50: Optional[float] = None
    valor_percentil_75: Optional[float] = None
    valor_percentil_90: Optional[float] = None
    valor_mejor_practica: Optional[float] = None
    fecha_inicio_benchmark: Optional[date] = None
    fecha_fin_benchmark: Optional[date] = None
    tamaño_muestra: Optional[int] = Field(None, ge=1)
    activo: Optional[bool] = None

class BenchmarkMetricaOut(BenchmarkMetricaBase):
    """Esquema de salida para benchmarks de métricas"""
    id: int
    metrica_id: int
    fecha_creacion: datetime
    fecha_ultima_actualizacion: datetime
    creado_por: Optional[int] = None
    activo: bool
    
    class Config:
        from_attributes = True

# === DASHBOARDS ===

class DashboardMetricasBase(BaseModel):
    """Esquema base para dashboards de métricas"""
    nombre: str = Field(..., max_length=255, description="Nombre del dashboard")
    descripcion: Optional[str] = Field(None, description="Descripción del dashboard")
    tipo_dashboard: str = Field(..., description="Tipo de dashboard")
    layout: Optional[Dict[str, Any]] = Field(None, description="Configuración del layout")
    colores_theme: Optional[Dict[str, Any]] = Field(None, description="Colores del tema")
    configuracion_widgets: Optional[Dict[str, Any]] = Field(None, description="Configuración de widgets")
    es_publico: bool = Field(False, description="Dashboard público")
    usuarios_permitidos: Optional[List[int]] = Field(None, description="IDs de usuarios permitidos")
    roles_permitidos: Optional[List[str]] = Field(None, description="Roles permitidos")

class DashboardMetricasCreate(DashboardMetricasBase):
    """Esquema para crear dashboards de métricas"""
    pass

class DashboardMetricasUpdate(BaseModel):
    """Esquema para actualizar dashboards de métricas"""
    nombre: Optional[str] = Field(None, max_length=255)
    descripcion: Optional[str] = None
    tipo_dashboard: Optional[str] = None
    layout: Optional[Dict[str, Any]] = None
    colores_theme: Optional[Dict[str, Any]] = None
    configuracion_widgets: Optional[Dict[str, Any]] = None
    es_publico: Optional[bool] = None
    usuarios_permitidos: Optional[List[int]] = None
    roles_permitidos: Optional[List[str]] = None
    activo: Optional[bool] = None

class DashboardMetricasOut(DashboardMetricasBase):
    """Esquema de salida para dashboards de métricas"""
    id: int
    fecha_creacion: datetime
    fecha_ultima_actualizacion: datetime
    creado_por: Optional[int] = None
    activo: bool
    
    class Config:
        from_attributes = True

# === DASHBOARD MÉTRICAS ===

class DashboardMetricaBase(BaseModel):
    """Esquema base para métricas en dashboards"""
    posicion_x: int = Field(..., ge=0, description="Posición X")
    posicion_y: int = Field(..., ge=0, description="Posición Y")
    ancho: int = Field(..., ge=1, le=12, description="Ancho del widget")
    alto: int = Field(..., ge=1, le=12, description="Alto del widget")
    tipo_grafico: Optional[str] = Field(None, description="Tipo de gráfico")
    configuracion_grafico: Optional[Dict[str, Any]] = Field(None, description="Configuración del gráfico")
    titulo_personalizado: Optional[str] = Field(None, max_length=255, description="Título personalizado")
    periodo_desde: Optional[datetime] = Field(None, description="Período desde")
    periodo_hasta: Optional[datetime] = Field(None, description="Período hasta")
    agrupacion: Optional[str] = Field(None, description="Agrupación de datos")
    orden: int = Field(0, description="Orden de visualización")

class DashboardMetricaCreate(DashboardMetricaBase):
    """Esquema para crear métricas en dashboards"""
    dashboard_id: int = Field(..., description="ID del dashboard")
    metrica_id: int = Field(..., description="ID de la métrica")

class DashboardMetricaUpdate(BaseModel):
    """Esquema para actualizar métricas en dashboards"""
    posicion_x: Optional[int] = Field(None, ge=0)
    posicion_y: Optional[int] = Field(None, ge=0)
    ancho: Optional[int] = Field(None, ge=1, le=12)
    alto: Optional[int] = Field(None, ge=1, le=12)
    tipo_grafico: Optional[str] = None
    configuracion_grafico: Optional[Dict[str, Any]] = None
    titulo_personalizado: Optional[str] = Field(None, max_length=255)
    periodo_desde: Optional[datetime] = None
    periodo_hasta: Optional[datetime] = None
    agrupacion: Optional[str] = None
    orden: Optional[int] = None
    activo: Optional[bool] = None

class DashboardMetricaOut(DashboardMetricaBase):
    """Esquema de salida para métricas en dashboards"""
    id: int
    dashboard_id: int
    metrica_id: int
    fecha_creacion: datetime
    activo: bool
    
    class Config:
        from_attributes = True

# === REPORTES ===

class ReporteMetricasBase(BaseModel):
    """Esquema base para reportes de métricas"""
    nombre: str = Field(..., max_length=255, description="Nombre del reporte")
    descripcion: Optional[str] = Field(None, description="Descripción del reporte")
    tipo_reporte: str = Field(..., description="Tipo de reporte")
    metricas_incluidas: List[int] = Field(..., min_items=1, description="IDs de métricas incluidas")
    filtros: Optional[Dict[str, Any]] = Field(None, description="Filtros aplicados")
    agrupaciones: Optional[Dict[str, Any]] = Field(None, description="Agrupaciones de datos")
    fecha_desde: Optional[datetime] = Field(None, description="Fecha desde")
    fecha_hasta: Optional[datetime] = Field(None, description="Fecha hasta")
    frecuencia_generacion: Optional[str] = Field(None, description="Frecuencia de generación")
    formato_entrega: str = Field("pdf", description="Formato de entrega")
    destinatarios: Optional[List[str]] = Field(None, description="Lista de emails")
    programado: bool = Field(False, description="Reporte programado")
    cron_expression: Optional[str] = Field(None, description="Expresión cron")

    @validator('formato_entrega')
    def validar_formato_entrega(cls, v):
        formatos_validos = ['pdf', 'excel', 'csv', 'json', 'html']
        if v not in formatos_validos:
            raise ValueError(f'Formato de entrega debe ser uno de: {formatos_validos}')
        return v

class ReporteMetricasCreate(ReporteMetricasBase):
    """Esquema para crear reportes de métricas"""
    pass

class ReporteMetricasUpdate(BaseModel):
    """Esquema para actualizar reportes de métricas"""
    nombre: Optional[str] = Field(None, max_length=255)
    descripcion: Optional[str] = None
    tipo_reporte: Optional[str] = None
    metricas_incluidas: Optional[List[int]] = Field(None, min_items=1)
    filtros: Optional[Dict[str, Any]] = None
    agrupaciones: Optional[Dict[str, Any]] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    frecuencia_generacion: Optional[str] = None
    formato_entrega: Optional[str] = None
    destinatarios: Optional[List[str]] = None
    programado: Optional[bool] = None
    cron_expression: Optional[str] = None
    activo: Optional[bool] = None

class ReporteMetricasOut(ReporteMetricasBase):
    """Esquema de salida para reportes de métricas"""
    id: int
    fecha_creacion: datetime
    fecha_ultima_generacion: Optional[datetime] = None
    fecha_proxima_generacion: Optional[datetime] = None
    creado_por: Optional[int] = None
    activo: bool
    total_generaciones: int
    generaciones_exitosas: int
    generaciones_fallidas: int
    
    class Config:
        from_attributes = True

# === ESQUEMAS DE CONSULTA Y FILTROS ===

class MetricaFiltros(BaseModel):
    """Filtros para consultar métricas"""
    tipo_metrica: Optional[TipoMetrica] = Field(None, description="Filtrar por tipo")
    categoria: Optional[CategoriaMetrica] = Field(None, description="Filtrar por categoría")
    subcategoria: Optional[str] = Field(None, description="Filtrar por subcategoría")
    frecuencia_medicion: Optional[FrecuenciaMedicion] = Field(None, description="Filtrar por frecuencia")
    activo: Optional[bool] = Field(True, description="Solo métricas activas")
    creado_por: Optional[int] = Field(None, description="Filtrar por creador")

class MedicionFiltros(BaseModel):
    """Filtros para consultar mediciones"""
    metrica_id: Optional[int] = Field(None, description="Filtrar por métrica")
    fecha_desde: Optional[datetime] = Field(None, description="Fecha desde")
    fecha_hasta: Optional[datetime] = Field(None, description="Fecha hasta")
    tendencia: Optional[str] = Field(None, description="Filtrar por tendencia")
    calculado_por: Optional[int] = Field(None, description="Filtrar por calculador")

class AlertaFiltros(BaseModel):
    """Filtros para consultar alertas"""
    metrica_id: Optional[int] = Field(None, description="Filtrar por métrica")
    tipo_alerta: Optional[TipoAlerta] = Field(None, description="Filtrar por tipo")
    estado: Optional[EstadoAlerta] = Field(None, description="Filtrar por estado")
    activo: Optional[bool] = Field(True, description="Solo alertas activas")
    creado_por: Optional[int] = Field(None, description="Filtrar por creador")

# === ESQUEMAS DE RESUMEN Y ESTADÍSTICAS ===

class ResumenMetricas(BaseModel):
    """Resumen de métricas"""
    total_metricas: int
    metricas_activas: int
    metricas_inactivas: int
    total_mediciones: int
    mediciones_mes_actual: int
    total_alertas: int
    alertas_activas: int
    alertas_disparadas: int
    total_dashboards: int
    dashboards_publicos: int
    total_reportes: int
    reportes_programados: int

class EstadisticasMetrica(BaseModel):
    """Estadísticas de una métrica específica"""
    metrica_id: int
    nombre_metrica: str
    codigo_metrica: str
    
    # Estadísticas de mediciones
    total_mediciones: int
    mediciones_mes_actual: int
    valor_promedio: float
    valor_mediana: float
    valor_minimo: float
    valor_maximo: float
    desviacion_estandar: float
    
    # Análisis de tendencia
    tendencia_actual: str
    velocidad_cambio: float
    variacion_mes_anterior: float
    variacion_anio_anterior: float
    
    # Análisis de alertas
    total_alertas: int
    alertas_activas: int
    alertas_disparadas_mes: int
    tiempo_promedio_resolucion: Optional[float] = None
    
    # Benchmarking
    percentil_mercado: Optional[float] = None
    comparacion_objetivo: Optional[float] = None
    gap_mejor_practica: Optional[float] = None

class DashboardEjecutivo(BaseModel):
    """Dashboard ejecutivo con métricas clave"""
    # Métricas financieras
    ingresos_mes: float
    ingresos_anio: float
    crecimiento_ingresos: float
    margen_bruto: float
    margen_neto: float
    rentabilidad_activos: float
    
    # Métricas operativas
    ventas_mes: int
    clientes_activos: int
    productos_vendidos: int
    ticket_promedio: float
    satisfaccion_cliente: float
    
    # Métricas de crecimiento
    crecimiento_ventas: float
    crecimiento_clientes: float
    crecimiento_productos: float
    penetracion_mercado: float
    
    # Alertas críticas
    alertas_criticas: List[Dict[str, Any]] = []
    alertas_importantes: List[Dict[str, Any]] = []
    
    # Tendencias
    tendencia_ingresos: str
    tendencia_ventas: str
    tendencia_clientes: str
    tendencia_rentabilidad: str
    
    # Recomendaciones
    recomendaciones: List[str] = []
    
    # Metadatos
    fecha_actualizacion: datetime
    proxima_actualizacion: datetime

