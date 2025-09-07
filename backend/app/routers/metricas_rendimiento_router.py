# app/routers/metricas_rendimiento_router.py
from fastapi import APIRouter, Depends, Query, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from datetime import datetime, date, timedelta

from app.db.database import get_db
from app.core.deps import require_user, require_admin
from app.services.metricas_rendimiento_service import MetricasRendimientoService
from app.schemas.metricas_rendimiento_schema import (
    MetricaRendimientoCreate, MetricaRendimientoUpdate, MetricaRendimientoOut,
    MedicionMetricaCreate, MedicionMetricaUpdate, MedicionMetricaOut,
    AlertaMetricaCreate, AlertaMetricaUpdate, AlertaMetricaOut,
    ActivacionAlertaCreate, ActivacionAlertaUpdate, ActivacionAlertaOut,
    BenchmarkMetricaCreate, BenchmarkMetricaUpdate, BenchmarkMetricaOut,
    DashboardMetricasCreate, DashboardMetricasUpdate, DashboardMetricasOut,
    DashboardMetricaCreate, DashboardMetricaUpdate, DashboardMetricaOut,
    ReporteMetricasCreate, ReporteMetricasUpdate, ReporteMetricasOut,
    MetricaFiltros, MedicionFiltros, AlertaFiltros,
    ResumenMetricas, EstadisticasMetrica, DashboardEjecutivo,
    TipoMetrica, CategoriaMetrica, TipoCalculo, FrecuenciaMedicion,
    EstadoAlerta, TipoAlerta
)

router = APIRouter(prefix="/metricas-rendimiento", tags=["Métricas de Rendimiento"])

# === MÉTRICAS DE RENDIMIENTO ===

@router.post("/", response_model=MetricaRendimientoOut, summary="Crear métrica de rendimiento")
def crear_metrica(
    metrica: MetricaRendimientoCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden crear métricas
):
    """
    Crea una nueva métrica de rendimiento.
    Solo usuarios administradores pueden crear métricas.
    """
    return MetricasRendimientoService.crear_metrica(db, metrica, current_user.id)

@router.get("/", response_model=List[MetricaRendimientoOut], summary="Listar métricas")
def listar_metricas(
    skip: int = Query(0, ge=0, description="Número de métricas a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de métricas a retornar"),
    tipo_metrica: Optional[TipoMetrica] = Query(None, description="Filtrar por tipo"),
    categoria: Optional[CategoriaMetrica] = Query(None, description="Filtrar por categoría"),
    subcategoria: Optional[str] = Query(None, description="Filtrar por subcategoría"),
    frecuencia_medicion: Optional[FrecuenciaMedicion] = Query(None, description="Filtrar por frecuencia"),
    activo: Optional[bool] = Query(True, description="Solo métricas activas"),
    creado_por: Optional[int] = Query(None, description="Filtrar por creador"),
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Lista métricas de rendimiento con filtros opcionales.
    """
    filtros = MetricaFiltros(
        tipo_metrica=tipo_metrica,
        categoria=categoria,
        subcategoria=subcategoria,
        frecuencia_medicion=frecuencia_medicion,
        activo=activo,
        creado_por=creado_por
    )
    
    return MetricasRendimientoService.obtener_metricas(db, filtros, skip, limit)

@router.get("/{metrica_id}", response_model=MetricaRendimientoOut, summary="Obtener métrica")
def obtener_metrica(
    metrica_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Obtiene una métrica específica.
    """
    from app.models.metricas_rendimiento_model import MetricaRendimiento
    metrica = db.query(MetricaRendimiento).filter(MetricaRendimiento.id == metrica_id).first()
    
    if not metrica:
        raise HTTPException(status_code=404, detail="Métrica no encontrada")
    
    return metrica

@router.put("/{metrica_id}", response_model=MetricaRendimientoOut, summary="Actualizar métrica")
def actualizar_metrica(
    metrica_id: int,
    metrica_update: MetricaRendimientoUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden actualizar
):
    """
    Actualiza una métrica existente.
    Solo usuarios administradores pueden actualizar métricas.
    """
    from app.models.metricas_rendimiento_model import MetricaRendimiento
    metrica = db.query(MetricaRendimiento).filter(MetricaRendimiento.id == metrica_id).first()
    
    if not metrica:
        raise HTTPException(status_code=404, detail="Métrica no encontrada")
    
    # Actualizar campos
    for field, value in metrica_update.dict(exclude_unset=True).items():
        if field == "dependencias" and value is not None:
            setattr(metrica, field, json.dumps(value))
        else:
            setattr(metrica, field, value)
    
    metrica.fecha_ultima_actualizacion = datetime.utcnow()
    db.commit()
    db.refresh(metrica)
    
    return metrica

@router.delete("/{metrica_id}", summary="Eliminar métrica")
def eliminar_metrica(
    metrica_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden eliminar
):
    """
    Elimina una métrica.
    Solo usuarios administradores pueden eliminar métricas.
    """
    from app.models.metricas_rendimiento_model import MetricaRendimiento
    metrica = db.query(MetricaRendimiento).filter(MetricaRendimiento.id == metrica_id).first()
    
    if not metrica:
        raise HTTPException(status_code=404, detail="Métrica no encontrada")
    
    db.delete(metrica)
    db.commit()
    
    return {"message": "Métrica eliminada correctamente"}

# === MEDICIONES DE MÉTRICAS ===

@router.post("/{metrica_id}/mediciones", response_model=MedicionMetricaOut, summary="Calcular medición")
def calcular_medicion(
    metrica_id: int,
    fecha_medicion: Optional[datetime] = Query(None, description="Fecha de medición"),
    periodo_desde: Optional[datetime] = Query(None, description="Período desde"),
    periodo_hasta: Optional[datetime] = Query(None, description="Período hasta"),
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Calcula una medición para una métrica específica.
    """
    return MetricasRendimientoService.calcular_metrica(
        db, metrica_id, fecha_medicion, periodo_desde, periodo_hasta, current_user.id
    )

@router.get("/{metrica_id}/mediciones", response_model=List[MedicionMetricaOut], summary="Listar mediciones")
def listar_mediciones(
    metrica_id: int,
    skip: int = Query(0, ge=0, description="Número de mediciones a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de mediciones a retornar"),
    fecha_desde: Optional[datetime] = Query(None, description="Fecha desde"),
    fecha_hasta: Optional[datetime] = Query(None, description="Fecha hasta"),
    tendencia: Optional[str] = Query(None, description="Filtrar por tendencia"),
    calculado_por: Optional[int] = Query(None, description="Filtrar por calculador"),
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Lista mediciones de una métrica con filtros opcionales.
    """
    from app.models.metricas_rendimiento_model import MedicionMetrica
    query = db.query(MedicionMetrica).filter(MedicionMetrica.metrica_id == metrica_id)
    
    if fecha_desde:
        query = query.filter(MedicionMetrica.fecha_medicion >= fecha_desde)
    if fecha_hasta:
        query = query.filter(MedicionMetrica.fecha_medicion <= fecha_hasta)
    if tendencia:
        query = query.filter(MedicionMetrica.tendencia == tendencia)
    if calculado_por:
        query = query.filter(MedicionMetrica.calculado_por == calculado_por)
    
    return query.order_by(desc(MedicionMetrica.fecha_medicion)).offset(skip).limit(limit).all()

@router.get("/{metrica_id}/mediciones/{medicion_id}", response_model=MedicionMetricaOut, summary="Obtener medición")
def obtener_medicion(
    metrica_id: int,
    medicion_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Obtiene una medición específica.
    """
    from app.models.metricas_rendimiento_model import MedicionMetrica
    medicion = db.query(MedicionMetrica).filter(
        MedicionMetrica.id == medicion_id,
        MedicionMetrica.metrica_id == metrica_id
    ).first()
    
    if not medicion:
        raise HTTPException(status_code=404, detail="Medición no encontrada")
    
    return medicion

# === ALERTAS DE MÉTRICAS ===

@router.post("/{metrica_id}/alertas", response_model=AlertaMetricaOut, summary="Crear alerta")
def crear_alerta(
    metrica_id: int,
    alerta: AlertaMetricaCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden crear alertas
):
    """
    Crea una nueva alerta para una métrica.
    Solo usuarios administradores pueden crear alertas.
    """
    alerta.metrica_id = metrica_id
    return MetricasRendimientoService.crear_alerta(db, alerta, current_user.id)

@router.get("/{metrica_id}/alertas", response_model=List[AlertaMetricaOut], summary="Listar alertas")
def listar_alertas(
    metrica_id: int,
    skip: int = Query(0, ge=0, description="Número de alertas a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de alertas a retornar"),
    tipo_alerta: Optional[TipoAlerta] = Query(None, description="Filtrar por tipo"),
    estado: Optional[EstadoAlerta] = Query(None, description="Filtrar por estado"),
    activo: Optional[bool] = Query(True, description="Solo alertas activas"),
    creado_por: Optional[int] = Query(None, description="Filtrar por creador"),
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Lista alertas de una métrica con filtros opcionales.
    """
    from app.models.metricas_rendimiento_model import AlertaMetrica
    query = db.query(AlertaMetrica).filter(AlertaMetrica.metrica_id == metrica_id)
    
    if tipo_alerta:
        query = query.filter(AlertaMetrica.tipo_alerta == tipo_alerta.value)
    if estado:
        query = query.filter(AlertaMetrica.estado == estado.value)
    if activo is not None:
        query = query.filter(AlertaMetrica.activo == activo)
    if creado_por:
        query = query.filter(AlertaMetrica.creado_por == creado_por)
    
    return query.order_by(desc(AlertaMetrica.fecha_creacion)).offset(skip).limit(limit).all()

@router.put("/alertas/{alerta_id}", response_model=AlertaMetricaOut, summary="Actualizar alerta")
def actualizar_alerta(
    alerta_id: int,
    alerta_update: AlertaMetricaUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden actualizar
):
    """
    Actualiza una alerta existente.
    Solo usuarios administradores pueden actualizar alertas.
    """
    from app.models.metricas_rendimiento_model import AlertaMetrica
    alerta = db.query(AlertaMetrica).filter(AlertaMetrica.id == alerta_id).first()
    
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    
    # Actualizar campos
    for field, value in alerta_update.dict(exclude_unset=True).items():
        if field == "usuarios_notificar" and value is not None:
            setattr(alerta, field, json.dumps(value))
        else:
            setattr(alerta, field, value)
    
    db.commit()
    db.refresh(alerta)
    
    return alerta

@router.delete("/alertas/{alerta_id}", summary="Eliminar alerta")
def eliminar_alerta(
    alerta_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden eliminar
):
    """
    Elimina una alerta.
    Solo usuarios administradores pueden eliminar alertas.
    """
    from app.models.metricas_rendimiento_model import AlertaMetrica
    alerta = db.query(AlertaMetrica).filter(AlertaMetrica.id == alerta_id).first()
    
    if not alerta:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    
    db.delete(alerta)
    db.commit()
    
    return {"message": "Alerta eliminada correctamente"}

# === ACTIVACIONES DE ALERTAS ===

@router.get("/alertas/{alerta_id}/activaciones", response_model=List[ActivacionAlertaOut], summary="Listar activaciones")
def listar_activaciones(
    alerta_id: int,
    skip: int = Query(0, ge=0, description="Número de activaciones a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de activaciones a retornar"),
    estado: Optional[EstadoAlerta] = Query(None, description="Filtrar por estado"),
    severidad: Optional[str] = Query(None, description="Filtrar por severidad"),
    fecha_desde: Optional[datetime] = Query(None, description="Fecha desde"),
    fecha_hasta: Optional[datetime] = Query(None, description="Fecha hasta"),
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Lista activaciones de una alerta con filtros opcionales.
    """
    from app.models.metricas_rendimiento_model import ActivacionAlerta
    query = db.query(ActivacionAlerta).filter(ActivacionAlerta.alerta_id == alerta_id)
    
    if estado:
        query = query.filter(ActivacionAlerta.estado == estado.value)
    if severidad:
        query = query.filter(ActivacionAlerta.severidad == severidad)
    if fecha_desde:
        query = query.filter(ActivacionAlerta.fecha_activacion >= fecha_desde)
    if fecha_hasta:
        query = query.filter(ActivacionAlerta.fecha_activacion <= fecha_hasta)
    
    return query.order_by(desc(ActivacionAlerta.fecha_activacion)).offset(skip).limit(limit).all()

@router.put("/activaciones/{activacion_id}", response_model=ActivacionAlertaOut, summary="Actualizar activación")
def actualizar_activacion(
    activacion_id: int,
    activacion_update: ActivacionAlertaUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Actualiza una activación de alerta.
    """
    from app.models.metricas_rendimiento_model import ActivacionAlerta
    activacion = db.query(ActivacionAlerta).filter(ActivacionAlerta.id == activacion_id).first()
    
    if not activacion:
        raise HTTPException(status_code=404, detail="Activación no encontrada")
    
    # Actualizar campos
    for field, value in activacion_update.dict(exclude_unset=True).items():
        setattr(activacion, field, value)
    
    # Si se marca como resuelta, actualizar fechas
    if activacion_update.estado == EstadoAlerta.RESUELTA.value:
        activacion.fecha_resolucion = datetime.utcnow()
        activacion.resuelto_por = current_user.id
    
    db.commit()
    db.refresh(activacion)
    
    return activacion

# === DASHBOARD EJECUTIVO ===

@router.get("/dashboard-ejecutivo", response_model=DashboardEjecutivo, summary="Dashboard ejecutivo")
def obtener_dashboard_ejecutivo(
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Obtiene el dashboard ejecutivo con métricas clave del negocio.
    """
    return MetricasRendimientoService.obtener_dashboard_ejecutivo(db)

@router.get("/resumen", response_model=ResumenMetricas, summary="Resumen de métricas")
def obtener_resumen_metricas(
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Obtiene un resumen de todas las métricas del sistema.
    """
    return MetricasRendimientoService.obtener_resumen_metricas(db)

@router.get("/{metrica_id}/estadisticas", response_model=EstadisticasMetrica, summary="Estadísticas de métrica")
def obtener_estadisticas_metrica(
    metrica_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Obtiene estadísticas detalladas de una métrica específica.
    """
    from app.models.metricas_rendimiento_model import MetricaRendimiento
    metrica = db.query(MetricaRendimiento).filter(MetricaRendimiento.id == metrica_id).first()
    
    if not metrica:
        raise HTTPException(status_code=404, detail="Métrica no encontrada")
    
    # Simulación de estadísticas detalladas
    return EstadisticasMetrica(
        metrica_id=metrica.id,
        nombre_metrica=metrica.nombre,
        codigo_metrica=metrica.codigo,
        total_mediciones=0,  # Se calcularía con datos reales
        mediciones_mes_actual=0,  # Se calcularía con datos reales
        valor_promedio=0.0,  # Se calcularía con datos reales
        valor_mediana=0.0,  # Se calcularía con datos reales
        valor_minimo=0.0,  # Se calcularía con datos reales
        valor_maximo=0.0,  # Se calcularía con datos reales
        desviacion_estandar=0.0,  # Se calcularía con datos reales
        tendencia_actual="estable",  # Se calcularía con datos reales
        velocidad_cambio=0.0,  # Se calcularía con datos reales
        variacion_mes_anterior=0.0,  # Se calcularía con datos reales
        variacion_anio_anterior=0.0,  # Se calcularía con datos reales
        total_alertas=0,  # Se calcularía con datos reales
        alertas_activas=0,  # Se calcularía con datos reales
        alertas_disparadas_mes=0,  # Se calcularía con datos reales
        tiempo_promedio_resolucion=None,  # Se calcularía con datos reales
        percentil_mercado=None,  # Se calcularía con datos reales
        comparacion_objetivo=None,  # Se calcularía con datos reales
        gap_mejor_practica=None  # Se calcularía con datos reales
    )

# === CÁLCULO AUTOMÁTICO ===

@router.post("/calcular-todas", summary="Calcular todas las métricas")
def calcular_todas_metricas(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden calcular todas
):
    """
    Calcula todas las métricas activas del sistema.
    Solo usuarios administradores pueden ejecutar este proceso.
    """
    from app.models.metricas_rendimiento_model import MetricaRendimiento
    
    metricas_activas = db.query(MetricaRendimiento).filter(
        MetricaRendimiento.activo == True
    ).all()
    
    for metrica in metricas_activas:
        background_tasks.add_task(
            MetricasRendimientoService.calcular_metrica,
            db, metrica.id, None, None, None, current_user.id
        )
    
    return {
        "message": f"Cálculo iniciado para {len(metricas_activas)} métricas",
        "metricas_procesadas": len(metricas_activas)
    }

# === UTILIDADES ===

@router.get("/tipos-disponibles", summary="Obtener tipos disponibles")
def obtener_tipos_disponibles():
    """
    Obtiene los tipos y opciones disponibles para métricas.
    """
    return {
        "tipos_metrica": [tipo.value for tipo in TipoMetrica],
        "categorias": [categoria.value for categoria in CategoriaMetrica],
        "tipos_calculo": [tipo.value for tipo in TipoCalculo],
        "frecuencias_medicion": [frecuencia.value for frecuencia in FrecuenciaMedicion],
        "tipos_alerta": [tipo.value for tipo in TipoAlerta],
        "estados_alerta": [estado.value for estado in EstadoAlerta],
        "severidades": ["baja", "media", "alta", "critica"],
        "tendencias": ["creciente", "decreciente", "estable"],
        "tipos_dashboard": ["ejecutivo", "operativo", "financiero", "comercial", "recursos_humanos"],
        "tipos_reporte": ["ejecutivo", "operativo", "analisis", "comparativo", "tendencia"],
        "formatos_entrega": ["pdf", "excel", "csv", "json", "html"],
        "tipos_grafico": ["linea", "barra", "pie", "area", "scatter", "histograma", "boxplot"]
    }

@router.post("/{metrica_id}/test", summary="Probar métrica")
def probar_metrica(
    metrica_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden probar
):
    """
    Prueba el cálculo de una métrica específica.
    Solo usuarios administradores pueden probar métricas.
    """
    from app.models.metricas_rendimiento_model import MetricaRendimiento
    metrica = db.query(MetricaRendimiento).filter(MetricaRendimiento.id == metrica_id).first()
    
    if not metrica:
        raise HTTPException(status_code=404, detail="Métrica no encontrada")
    
    try:
        # Calcular métrica de prueba
        medicion = MetricasRendimientoService.calcular_metrica(
            db, metrica_id, datetime.utcnow(), None, None, current_user.id
        )
        
        return {
            "exito": True,
            "mensaje": "Cálculo exitoso",
            "valor_calculado": medicion.valor_actual,
            "tendencia": medicion.tendencia,
            "variacion_porcentual": medicion.variacion_porcentual,
            "fecha_calculo": medicion.fecha_calculo.isoformat()
        }
    except Exception as e:
        return {
            "exito": False,
            "mensaje": f"Error en el cálculo: {str(e)}",
            "fecha_error": datetime.utcnow().isoformat()
        }

