# app/models/metricas_rendimiento_model.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Date, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, date
from enum import Enum as PyEnum
from app.db.database import Base

class TipoMetrica(str, PyEnum):
    """Tipos de métricas de rendimiento"""
    VENTAS = "ventas"
    RENTABILIDAD = "rentabilidad"
    CLIENTES = "clientes"
    PRODUCTOS = "productos"
    INVENTARIO = "inventario"
    FINANCIERO = "financiero"
    OPERATIVO = "operativo"
    MARKETING = "marketing"
    RECURSOS_HUMANOS = "recursos_humanos"
    TECNOLOGIA = "tecnologia"

class CategoriaMetrica(str, PyEnum):
    """Categorías de métricas"""
    EFICIENCIA = "eficiencia"
    CALIDAD = "calidad"
    PRODUCTIVIDAD = "productividad"
    SATISFACCION = "satisfaccion"
    CRECIMIENTO = "crecimiento"
    RENTABILIDAD = "rentabilidad"
    COMPETITIVIDAD = "competitividad"
    INNOVACION = "innovacion"
    SUSTENTABILIDAD = "sustentabilidad"
    RIESGO = "riesgo"

class TipoCalculo(str, PyEnum):
    """Tipos de cálculo de métricas"""
    SUMA = "suma"
    PROMEDIO = "promedio"
    MEDIANA = "mediana"
    MAXIMO = "maximo"
    MINIMO = "minimo"
    PORCENTAJE = "porcentaje"
    RATIO = "ratio"
    TENDENCIA = "tendencia"
    CORRELACION = "correlacion"
    REGRESION = "regresion"

class FrecuenciaMedicion(str, PyEnum):
    """Frecuencias de medición"""
    DIARIA = "diaria"
    SEMANAL = "semanal"
    MENSUAL = "mensual"
    TRIMESTRAL = "trimestral"
    SEMESTRAL = "semestral"
    ANUAL = "anual"
    EN_TIEMPO_REAL = "en_tiempo_real"
    ON_DEMAND = "on_demand"

class EstadoAlerta(str, PyEnum):
    """Estados de alertas"""
    ACTIVA = "activa"
    INACTIVA = "inactiva"
    TRIGGERED = "triggered"
    RESUELTA = "resuelta"
    EXPIRADA = "expirada"

class TipoAlerta(str, PyEnum):
    """Tipos de alertas"""
    UMBRAL = "umbral"
    TENDENCIA = "tendencia"
    ANOMALIA = "anomalia"
    COMPARACION = "comparacion"
    PREDICCION = "prediccion"
    SISTEMA = "sistema"

class MetricaRendimiento(Base):
    __tablename__ = "metricas_rendimiento"

    id = Column(Integer, primary_key=True, index=True)
    
    # Identificación de la métrica
    nombre = Column(String(255), nullable=False, index=True)
    codigo = Column(String(100), nullable=False, unique=True, index=True)
    descripcion = Column(Text, nullable=True)
    
    # Clasificación
    tipo_metrica = Column(String(50), nullable=False, index=True)
    categoria = Column(String(50), nullable=False, index=True)
    subcategoria = Column(String(100), nullable=True, index=True)
    
    # Configuración de cálculo
    tipo_calculo = Column(String(50), nullable=False, index=True)
    formula = Column(Text, nullable=True)
    unidad_medida = Column(String(50), nullable=True)
    decimales = Column(Integer, default=2)
    
    # Configuración de medición
    frecuencia_medicion = Column(String(50), nullable=False, index=True)
    fuente_datos = Column(String(255), nullable=True)
    dependencias = Column(JSON, nullable=True)  # Otras métricas de las que depende
    
    # Configuración de objetivos
    valor_objetivo = Column(Float, nullable=True)
    valor_minimo = Column(Float, nullable=True)
    valor_maximo = Column(Float, nullable=True)
    rango_optimo_inicio = Column(Float, nullable=True)
    rango_optimo_fin = Column(Float, nullable=True)
    
    # Metadatos
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_ultima_actualizacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    creado_por = Column(Integer, ForeignKey("users.id"), nullable=True)
    activo = Column(Boolean, default=True, index=True)
    
    # Configuración de visualización
    color_positivo = Column(String(7), default="#28a745")  # Verde
    color_negativo = Column(String(7), default="#dc3545")  # Rojo
    color_neutro = Column(String(7), default="#6c757d")    # Gris
    icono = Column(String(50), nullable=True)
    orden_display = Column(Integer, default=0)
    
    # Relaciones
    creador = relationship("User", backref="metricas_creadas")
    mediciones = relationship("MedicionMetrica", backref="metrica", cascade="all, delete-orphan")
    alertas = relationship("AlertaMetrica", backref="metrica", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<MetricaRendimiento(id={self.id}, nombre='{self.nombre}', codigo='{self.codigo}')>"

class MedicionMetrica(Base):
    __tablename__ = "mediciones_metricas"

    id = Column(Integer, primary_key=True, index=True)
    metrica_id = Column(Integer, ForeignKey("metricas_rendimiento.id"), nullable=False, index=True)
    
    # Período de medición
    fecha_medicion = Column(DateTime, nullable=False, index=True)
    periodo_desde = Column(DateTime, nullable=True)
    periodo_hasta = Column(DateTime, nullable=True)
    
    # Valores de la medición
    valor_actual = Column(Float, nullable=False)
    valor_anterior = Column(Float, nullable=True)
    valor_objetivo = Column(Float, nullable=True)
    valor_historico_promedio = Column(Float, nullable=True)
    
    # Análisis de tendencia
    variacion_absoluta = Column(Float, nullable=True)
    variacion_porcentual = Column(Float, nullable=True)
    tendencia = Column(String(20), nullable=True)  # creciente, decreciente, estable
    velocidad_cambio = Column(Float, nullable=True)  # Cambio por período
    
    # Análisis comparativo
    percentil = Column(Float, nullable=True)  # Percentil respecto a histórico
    ranking = Column(Integer, nullable=True)  # Ranking entre métricas similares
    desviacion_estandar = Column(Float, nullable=True)
    
    # Metadatos
    fecha_calculo = Column(DateTime, default=datetime.utcnow, nullable=False)
    calculado_por = Column(Integer, ForeignKey("users.id"), nullable=True)
    fuente_datos = Column(String(255), nullable=True)
    observaciones = Column(Text, nullable=True)
    
    # Datos adicionales
    contexto = Column(JSON, nullable=True)  # Información adicional del contexto
    factores_influencia = Column(JSON, nullable=True)  # Factores que influyeron
    
    # Relaciones
    calculador = relationship("User", backref="mediciones_calculadas")
    
    def __repr__(self):
        return f"<MedicionMetrica(id={self.id}, metrica_id={self.metrica_id}, valor={self.valor_actual})>"

class AlertaMetrica(Base):
    __tablename__ = "alertas_metricas"

    id = Column(Integer, primary_key=True, index=True)
    metrica_id = Column(Integer, ForeignKey("metricas_rendimiento.id"), nullable=False, index=True)
    
    # Configuración de la alerta
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    tipo_alerta = Column(String(50), nullable=False, index=True)
    estado = Column(String(20), default=EstadoAlerta.ACTIVA.value, index=True)
    
    # Condiciones de activación
    condicion = Column(Text, nullable=False)  # Expresión lógica para activar
    umbral_minimo = Column(Float, nullable=True)
    umbral_maximo = Column(Float, nullable=True)
    umbral_porcentaje = Column(Float, nullable=True)
    ventana_tiempo = Column(Integer, nullable=True)  # En períodos
    
    # Configuración de notificación
    notificar_email = Column(Boolean, default=True)
    notificar_dashboard = Column(Boolean, default=True)
    notificar_movil = Column(Boolean, default=False)
    usuarios_notificar = Column(JSON, nullable=True)  # Lista de IDs de usuarios
    
    # Configuración de frecuencia
    frecuencia_verificacion = Column(String(50), default=FrecuenciaMedicion.DIARIA.value)
    max_alertas_por_dia = Column(Integer, default=5)
    cooldown_minutos = Column(Integer, default=60)  # Tiempo entre alertas
    
    # Metadatos
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_ultima_activacion = Column(DateTime, nullable=True)
    fecha_ultima_verificacion = Column(DateTime, nullable=True)
    creado_por = Column(Integer, ForeignKey("users.id"), nullable=True)
    activo = Column(Boolean, default=True, index=True)
    
    # Estadísticas
    total_activaciones = Column(Integer, default=0)
    activaciones_resueltas = Column(Integer, default=0)
    activaciones_pendientes = Column(Integer, default=0)
    
    # Relaciones
    creador = relationship("User", backref="alertas_creadas")
    activaciones = relationship("ActivacionAlerta", backref="alerta", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AlertaMetrica(id={self.id}, metrica_id={self.metrica_id}, tipo='{self.tipo_alerta}')>"

class ActivacionAlerta(Base):
    __tablename__ = "activaciones_alertas"

    id = Column(Integer, primary_key=True, index=True)
    alerta_id = Column(Integer, ForeignKey("alertas_metricas.id"), nullable=False, index=True)
    medicion_id = Column(Integer, ForeignKey("mediciones_metricas.id"), nullable=True, index=True)
    
    # Información de la activación
    fecha_activacion = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    valor_que_disparo = Column(Float, nullable=False)
    umbral_disparado = Column(Float, nullable=True)
    mensaje = Column(Text, nullable=False)
    severidad = Column(String(20), default="media")  # baja, media, alta, critica
    
    # Estado de la activación
    estado = Column(String(20), default=EstadoAlerta.TRIGGERED.value, index=True)
    fecha_resolucion = Column(DateTime, nullable=True)
    resuelto_por = Column(Integer, ForeignKey("users.id"), nullable=True)
    comentarios_resolucion = Column(Text, nullable=True)
    
    # Notificaciones enviadas
    notificaciones_enviadas = Column(JSON, nullable=True)
    usuarios_notificados = Column(JSON, nullable=True)
    
    # Metadatos
    contexto_adicional = Column(JSON, nullable=True)
    acciones_tomadas = Column(JSON, nullable=True)
    
    # Relaciones
    resolutor = relationship("User", backref="alertas_resueltas")
    
    def __repr__(self):
        return f"<ActivacionAlerta(id={self.id}, alerta_id={self.alerta_id}, fecha='{self.fecha_activacion}')>"

class BenchmarkMetrica(Base):
    __tablename__ = "benchmarks_metricas"

    id = Column(Integer, primary_key=True, index=True)
    metrica_id = Column(Integer, ForeignKey("metricas_rendimiento.id"), nullable=False, index=True)
    
    # Información del benchmark
    nombre_benchmark = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    fuente = Column(String(255), nullable=True)  # Fuente del benchmark
    sector = Column(String(100), nullable=True, index=True)
    region = Column(String(100), nullable=True, index=True)
    tamaño_empresa = Column(String(50), nullable=True)  # pequeña, mediana, grande
    
    # Valores de referencia
    valor_promedio_mercado = Column(Float, nullable=True)
    valor_percentil_25 = Column(Float, nullable=True)
    valor_percentil_50 = Column(Float, nullable=True)
    valor_percentil_75 = Column(Float, nullable=True)
    valor_percentil_90 = Column(Float, nullable=True)
    valor_mejor_practica = Column(Float, nullable=True)
    
    # Período de referencia
    fecha_inicio_benchmark = Column(Date, nullable=True)
    fecha_fin_benchmark = Column(Date, nullable=True)
    tamaño_muestra = Column(Integer, nullable=True)
    
    # Metadatos
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_ultima_actualizacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    creado_por = Column(Integer, ForeignKey("users.id"), nullable=True)
    activo = Column(Boolean, default=True, index=True)
    
    # Relaciones
    creador = relationship("User", backref="benchmarks_creados")
    
    def __repr__(self):
        return f"<BenchmarkMetrica(id={self.id}, metrica_id={self.metrica_id}, nombre='{self.nombre_benchmark}')>"

class DashboardMetricas(Base):
    __tablename__ = "dashboards_metricas"

    id = Column(Integer, primary_key=True, index=True)
    
    # Información del dashboard
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    tipo_dashboard = Column(String(50), nullable=False, index=True)  # ejecutivo, operativo, financiero, etc.
    
    # Configuración de visualización
    layout = Column(JSON, nullable=True)  # Configuración del layout
    colores_theme = Column(JSON, nullable=True)  # Colores del tema
    configuracion_widgets = Column(JSON, nullable=True)  # Configuración de widgets
    
    # Configuración de acceso
    es_publico = Column(Boolean, default=False)
    usuarios_permitidos = Column(JSON, nullable=True)  # Lista de IDs de usuarios
    roles_permitidos = Column(JSON, nullable=True)  # Lista de roles permitidos
    
    # Metadatos
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_ultima_actualizacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    creado_por = Column(Integer, ForeignKey("users.id"), nullable=True)
    activo = Column(Boolean, default=True, index=True)
    
    # Relaciones
    creador = relationship("User", backref="dashboards_creados")
    metricas = relationship("DashboardMetrica", backref="dashboard", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DashboardMetricas(id={self.id}, nombre='{self.nombre}', tipo='{self.tipo_dashboard}')>"

class DashboardMetrica(Base):
    __tablename__ = "dashboard_metricas"

    id = Column(Integer, primary_key=True, index=True)
    dashboard_id = Column(Integer, ForeignKey("dashboards_metricas.id"), nullable=False, index=True)
    metrica_id = Column(Integer, ForeignKey("metricas_rendimiento.id"), nullable=False, index=True)
    
    # Configuración del widget
    posicion_x = Column(Integer, nullable=False)
    posicion_y = Column(Integer, nullable=False)
    ancho = Column(Integer, nullable=False)
    alto = Column(Integer, nullable=False)
    
    # Configuración de visualización
    tipo_grafico = Column(String(50), nullable=True)  # linea, barra, pie, etc.
    configuracion_grafico = Column(JSON, nullable=True)
    titulo_personalizado = Column(String(255), nullable=True)
    
    # Configuración de datos
    periodo_desde = Column(DateTime, nullable=True)
    periodo_hasta = Column(DateTime, nullable=True)
    agrupacion = Column(String(50), nullable=True)  # diaria, semanal, mensual
    
    # Metadatos
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    orden = Column(Integer, default=0)
    activo = Column(Boolean, default=True, index=True)
    
    # Relaciones
    metrica = relationship("MetricaRendimiento", backref="dashboards")
    
    def __repr__(self):
        return f"<DashboardMetrica(id={self.id}, dashboard_id={self.dashboard_id}, metrica_id={self.metrica_id})>"

class ReporteMetricas(Base):
    __tablename__ = "reportes_metricas"

    id = Column(Integer, primary_key=True, index=True)
    
    # Información del reporte
    nombre = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=True)
    tipo_reporte = Column(String(50), nullable=False, index=True)  # ejecutivo, operativo, analisis, etc.
    
    # Configuración del reporte
    metricas_incluidas = Column(JSON, nullable=False)  # Lista de IDs de métricas
    filtros = Column(JSON, nullable=True)  # Filtros aplicados
    agrupaciones = Column(JSON, nullable=True)  # Agrupaciones de datos
    
    # Período del reporte
    fecha_desde = Column(DateTime, nullable=True)
    fecha_hasta = Column(DateTime, nullable=True)
    frecuencia_generacion = Column(String(50), nullable=True)
    
    # Configuración de entrega
    formato_entrega = Column(String(50), default="pdf")  # pdf, excel, csv, json
    destinatarios = Column(JSON, nullable=True)  # Lista de emails
    programado = Column(Boolean, default=False)
    cron_expression = Column(String(100), nullable=True)  # Para reportes programados
    
    # Metadatos
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_ultima_generacion = Column(DateTime, nullable=True)
    fecha_proxima_generacion = Column(DateTime, nullable=True)
    creado_por = Column(Integer, ForeignKey("users.id"), nullable=True)
    activo = Column(Boolean, default=True, index=True)
    
    # Estadísticas
    total_generaciones = Column(Integer, default=0)
    generaciones_exitosas = Column(Integer, default=0)
    generaciones_fallidas = Column(Integer, default=0)
    
    # Relaciones
    creador = relationship("User", backref="reportes_creados")
    
    def __repr__(self):
        return f"<ReporteMetricas(id={self.id}, nombre='{self.nombre}', tipo='{self.tipo_reporte}')>"

