# app/routers/reporte_financiero_router.py
from fastapi import APIRouter, Depends, Query, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from datetime import datetime, date, timedelta

from app.db.database import get_db
from app.core.deps import require_user, require_admin
from app.services.reporte_financiero_service import ReporteFinancieroService
from app.schemas.reporte_financiero_schema import (
    ReporteFinancieroCreate, ReporteFinancieroUpdate, ReporteFinancieroOut,
    EstadoResultadosCreate, EstadoResultadosOut,
    FlujoCajaCreate, FlujoCajaOut,
    AnalisisRentabilidadCreate, AnalisisRentabilidadOut,
    ProyeccionFinancieraCreate, ProyeccionFinancieraOut,
    MetricaFinancieraCreate, MetricaFinancieraOut,
    ReporteFiltros, ReporteResumen, DashboardFinanciero,
    ReporteComparativo, ExportacionReporte,
    TipoReporteFinanciero, PeriodoReporte, EstadoReporte
)

router = APIRouter(prefix="/reportes-financieros", tags=["Reportes Financieros"])

# === REPORTES FINANCIEROS ===

@router.post("/", response_model=ReporteFinancieroOut, summary="Crear reporte financiero")
def crear_reporte_financiero(
    reporte: ReporteFinancieroCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden crear reportes
):
    """
    Crea un nuevo reporte financiero.
    Solo usuarios administradores pueden crear reportes.
    """
    # Crear el reporte
    db_reporte = ReporteFinancieroService.crear_reporte_financiero(db, reporte, current_user.id)
    
    # Programar generación del reporte en background
    background_tasks.add_task(
        ReporteFinancieroService._generar_reporte_background,
        db_reporte.id,
        reporte.tipo,
        reporte.fecha_inicio,
        reporte.fecha_fin
    )
    
    return db_reporte

@router.get("/", response_model=List[ReporteFinancieroOut], summary="Listar reportes financieros")
def listar_reportes_financieros(
    skip: int = Query(0, ge=0, description="Número de reportes a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de reportes a retornar"),
    tipo: Optional[TipoReporteFinanciero] = Query(None, description="Filtrar por tipo"),
    periodo: Optional[PeriodoReporte] = Query(None, description="Filtrar por período"),
    estado: Optional[EstadoReporte] = Query(None, description="Filtrar por estado"),
    fecha_desde: Optional[date] = Query(None, description="Fecha desde"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha hasta"),
    creado_por: Optional[int] = Query(None, description="Filtrar por creador"),
    solo_activos: bool = Query(True, description="Solo reportes activos"),
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Lista reportes financieros con filtros opcionales.
    """
    filtros = ReporteFiltros(
        tipo=tipo,
        periodo=periodo,
        estado=estado,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        creado_por=creado_por,
        solo_activos=solo_activos
    )
    
    return ReporteFinancieroService.obtener_reportes_financieros(db, filtros, skip, limit)

@router.get("/{reporte_id}", response_model=ReporteFinancieroOut, summary="Obtener reporte financiero")
def obtener_reporte_financiero(
    reporte_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Obtiene un reporte financiero específico.
    """
    from app.models.reporte_financiero_model import ReporteFinanciero
    reporte = db.query(ReporteFinanciero).filter(ReporteFinanciero.id == reporte_id).first()
    
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    
    return reporte

@router.put("/{reporte_id}", response_model=ReporteFinancieroOut, summary="Actualizar reporte financiero")
def actualizar_reporte_financiero(
    reporte_id: int,
    reporte_update: ReporteFinancieroUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden actualizar
):
    """
    Actualiza un reporte financiero existente.
    Solo usuarios administradores pueden actualizar reportes.
    """
    from app.models.reporte_financiero_model import ReporteFinanciero
    reporte = db.query(ReporteFinanciero).filter(ReporteFinanciero.id == reporte_id).first()
    
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    
    # Actualizar campos
    for field, value in reporte_update.dict(exclude_unset=True).items():
        setattr(reporte, field, value)
    
    db.commit()
    db.refresh(reporte)
    
    return reporte

@router.delete("/{reporte_id}", summary="Eliminar reporte financiero")
def eliminar_reporte_financiero(
    reporte_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden eliminar
):
    """
    Elimina un reporte financiero.
    Solo usuarios administradores pueden eliminar reportes.
    """
    from app.models.reporte_financiero_model import ReporteFinanciero
    reporte = db.query(ReporteFinanciero).filter(ReporteFinanciero.id == reporte_id).first()
    
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    
    db.delete(reporte)
    db.commit()
    
    return {"message": "Reporte eliminado correctamente"}

# === ESTADO DE RESULTADOS ===

@router.post("/estado-resultados", response_model=EstadoResultadosOut, summary="Generar estado de resultados")
def generar_estado_resultados(
    reporte_id: int = Query(..., description="ID del reporte financiero"),
    periodo_desde: date = Query(..., description="Período desde"),
    periodo_hasta: date = Query(..., description="Período hasta"),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden generar
):
    """
    Genera un estado de resultados (P&L) para un período específico.
    Solo usuarios administradores pueden generar reportes.
    """
    return ReporteFinancieroService.generar_estado_resultados(db, reporte_id, periodo_desde, periodo_hasta)

@router.get("/estado-resultados/{reporte_id}", response_model=EstadoResultadosOut, summary="Obtener estado de resultados")
def obtener_estado_resultados(
    reporte_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Obtiene el estado de resultados de un reporte específico.
    """
    from app.models.reporte_financiero_model import EstadoResultados
    estado = db.query(EstadoResultados).filter(EstadoResultados.reporte_id == reporte_id).first()
    
    if not estado:
        raise HTTPException(status_code=404, detail="Estado de resultados no encontrado")
    
    return estado

# === FLUJO DE CAJA ===

@router.post("/flujo-caja", response_model=FlujoCajaOut, summary="Generar flujo de caja")
def generar_flujo_caja(
    reporte_id: int = Query(..., description="ID del reporte financiero"),
    periodo_desde: date = Query(..., description="Período desde"),
    periodo_hasta: date = Query(..., description="Período hasta"),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden generar
):
    """
    Genera un flujo de caja (Cash Flow) para un período específico.
    Solo usuarios administradores pueden generar reportes.
    """
    return ReporteFinancieroService.generar_flujo_caja(db, reporte_id, periodo_desde, periodo_hasta)

@router.get("/flujo-caja/{reporte_id}", response_model=FlujoCajaOut, summary="Obtener flujo de caja")
def obtener_flujo_caja(
    reporte_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Obtiene el flujo de caja de un reporte específico.
    """
    from app.models.reporte_financiero_model import FlujoCaja
    flujo = db.query(FlujoCaja).filter(FlujoCaja.reporte_id == reporte_id).first()
    
    if not flujo:
        raise HTTPException(status_code=404, detail="Flujo de caja no encontrado")
    
    return flujo

# === ANÁLISIS DE RENTABILIDAD ===

@router.post("/analisis-rentabilidad", response_model=List[AnalisisRentabilidadOut], summary="Generar análisis de rentabilidad")
def generar_analisis_rentabilidad(
    reporte_id: int = Query(..., description="ID del reporte financiero"),
    tipo_entidad: str = Query(..., description="Tipo de entidad (producto, cliente, categoria, proveedor)"),
    periodo_desde: date = Query(..., description="Período desde"),
    periodo_hasta: date = Query(..., description="Período hasta"),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden generar
):
    """
    Genera análisis de rentabilidad por entidad (producto, cliente, categoría, proveedor).
    Solo usuarios administradores pueden generar reportes.
    """
    tipos_validos = ['producto', 'cliente', 'categoria', 'proveedor']
    if tipo_entidad not in tipos_validos:
        raise HTTPException(status_code=400, detail=f"Tipo de entidad debe ser uno de: {tipos_validos}")
    
    return ReporteFinancieroService.generar_analisis_rentabilidad(
        db, reporte_id, tipo_entidad, periodo_desde, periodo_hasta
    )

@router.get("/analisis-rentabilidad/{reporte_id}", response_model=List[AnalisisRentabilidadOut], summary="Obtener análisis de rentabilidad")
def obtener_analisis_rentabilidad(
    reporte_id: int,
    tipo_entidad: Optional[str] = Query(None, description="Filtrar por tipo de entidad"),
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Obtiene el análisis de rentabilidad de un reporte específico.
    """
    from app.models.reporte_financiero_model import AnalisisRentabilidad
    query = db.query(AnalisisRentabilidad).filter(AnalisisRentabilidad.reporte_id == reporte_id)
    
    if tipo_entidad:
        query = query.filter(AnalisisRentabilidad.tipo_entidad == tipo_entidad)
    
    analisis = query.order_by(desc(AnalisisRentabilidad.margen_bruto_porcentaje)).all()
    
    if not analisis:
        raise HTTPException(status_code=404, detail="Análisis de rentabilidad no encontrado")
    
    return analisis

# === PROYECCIONES FINANCIERAS ===

@router.post("/proyecciones", response_model=ProyeccionFinancieraOut, summary="Generar proyección financiera")
def generar_proyeccion_financiera(
    proyeccion: ProyeccionFinancieraCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden generar
):
    """
    Genera una proyección financiera.
    Solo usuarios administradores pueden generar proyecciones.
    """
    return ReporteFinancieroService.generar_proyeccion_financiera(
        db, proyeccion.reporte_id, proyeccion.tipo_proyeccion,
        proyeccion.horizonte_meses, proyeccion.metodo_calculo,
        proyeccion.periodo_historico_desde, proyeccion.periodo_historico_hasta
    )

@router.get("/proyecciones/{reporte_id}", response_model=List[ProyeccionFinancieraOut], summary="Obtener proyecciones financieras")
def obtener_proyecciones_financieras(
    reporte_id: int,
    tipo_proyeccion: Optional[str] = Query(None, description="Filtrar por tipo de proyección"),
    activo: Optional[bool] = Query(True, description="Solo proyecciones activas"),
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Obtiene las proyecciones financieras de un reporte específico.
    """
    from app.models.reporte_financiero_model import ProyeccionFinanciera
    query = db.query(ProyeccionFinanciera).filter(ProyeccionFinanciera.reporte_id == reporte_id)
    
    if tipo_proyeccion:
        query = query.filter(ProyeccionFinanciera.tipo_proyeccion == tipo_proyeccion)
    if activo is not None:
        query = query.filter(ProyeccionFinanciera.activo == activo)
    
    proyecciones = query.order_by(desc(ProyeccionFinanciera.fecha_calculo)).all()
    
    if not proyecciones:
        raise HTTPException(status_code=404, detail="Proyecciones financieras no encontradas")
    
    return proyecciones

# === MÉTRICAS FINANCIERAS ===

@router.post("/metricas", response_model=MetricaFinancieraOut, summary="Crear métrica financiera")
def crear_metrica_financiera(
    metrica: MetricaFinancieraCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden crear métricas
):
    """
    Crea una nueva métrica financiera.
    Solo usuarios administradores pueden crear métricas.
    """
    from app.models.reporte_financiero_model import MetricaFinanciera
    
    db_metrica = MetricaFinanciera(
        nombre=metrica.nombre,
        categoria=metrica.categoria,
        tipo_valor=metrica.tipo_valor,
        valor_actual=metrica.valor_actual,
        valor_objetivo=metrica.valor_objetivo,
        descripcion=metrica.descripcion,
        formula=metrica.formula,
        fuente_datos=metrica.fuente_datos,
        periodo_desde=metrica.periodo_desde,
        periodo_hasta=metrica.periodo_hasta,
        calculado_por=current_user.id
    )
    
    db.add(db_metrica)
    db.commit()
    db.refresh(db_metrica)
    
    return db_metrica

@router.get("/metricas", response_model=List[MetricaFinancieraOut], summary="Listar métricas financieras")
def listar_metricas_financieras(
    skip: int = Query(0, ge=0, description="Número de métricas a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de métricas a retornar"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoría"),
    tipo_valor: Optional[str] = Query(None, description="Filtrar por tipo de valor"),
    fecha_desde: Optional[date] = Query(None, description="Fecha desde"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha hasta"),
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Lista métricas financieras con filtros opcionales.
    """
    from app.models.reporte_financiero_model import MetricaFinanciera
    query = db.query(MetricaFinanciera)
    
    if categoria:
        query = query.filter(MetricaFinanciera.categoria == categoria)
    if tipo_valor:
        query = query.filter(MetricaFinanciera.tipo_valor == tipo_valor)
    if fecha_desde:
        query = query.filter(MetricaFinanciera.periodo_desde >= fecha_desde)
    if fecha_hasta:
        query = query.filter(MetricaFinanciera.periodo_hasta <= fecha_hasta)
    
    metricas = query.order_by(desc(MetricaFinanciera.fecha_calculo)).offset(skip).limit(limit).all()
    
    return metricas

# === DASHBOARD Y RESUMEN ===

@router.get("/dashboard", response_model=DashboardFinanciero, summary="Dashboard financiero")
def obtener_dashboard_financiero(
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Obtiene el dashboard financiero en tiempo real.
    """
    return ReporteFinancieroService.obtener_dashboard_financiero(db)

@router.get("/resumen", response_model=ReporteResumen, summary="Resumen de reportes")
def obtener_resumen_reportes(
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Obtiene un resumen de los reportes financieros.
    """
    from app.models.reporte_financiero_model import ReporteFinanciero, EstadoResultados
    
    # Contar reportes por tipo
    total_reportes = db.query(ReporteFinanciero).count()
    
    reportes_por_tipo = {}
    for tipo in TipoReporteFinanciero:
        count = db.query(ReporteFinanciero).filter(ReporteFinanciero.tipo == tipo).count()
        reportes_por_tipo[tipo.value] = count
    
    # Contar reportes por estado
    reportes_por_estado = {}
    for estado in EstadoReporte:
        count = db.query(ReporteFinanciero).filter(ReporteFinanciero.estado == estado).count()
        reportes_por_estado[estado.value] = count
    
    # Contar reportes por período
    reportes_por_periodo = {}
    for periodo in PeriodoReporte:
        count = db.query(ReporteFinanciero).filter(ReporteFinanciero.periodo == periodo).count()
        reportes_por_periodo[periodo.value] = count
    
    # Obtener último reporte
    ultimo_reporte = db.query(ReporteFinanciero).order_by(desc(ReporteFinanciero.fecha_generacion)).first()
    
    # Obtener datos del mes actual
    hoy = date.today()
    inicio_mes = hoy.replace(day=1)
    
    # Simulación de datos - en implementación real se consultaría la base de datos
    total_ingresos_mes = 100000.0
    total_costos_mes = 70000.0
    ganancia_neta_mes = total_ingresos_mes - total_costos_mes
    margen_bruto_promedio = 30.0
    
    return ReporteResumen(
        total_reportes=total_reportes,
        reportes_por_tipo=reportes_por_tipo,
        reportes_por_estado=reportes_por_estado,
        reportes_por_periodo=reportes_por_periodo,
        ultimo_reporte=ultimo_reporte.fecha_generacion if ultimo_reporte else None,
        reporte_mas_reciente=ultimo_reporte.nombre if ultimo_reporte else None,
        total_ingresos_mes=total_ingresos_mes,
        total_costos_mes=total_costos_mes,
        ganancia_neta_mes=ganancia_neta_mes,
        margen_bruto_promedio=margen_bruto_promedio
    )

# === EXPORTACIÓN ===

@router.post("/{reporte_id}/exportar", summary="Exportar reporte")
def exportar_reporte(
    reporte_id: int,
    configuracion: ExportacionReporte,
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Exporta un reporte en el formato especificado.
    """
    from app.models.reporte_financiero_model import ReporteFinanciero
    reporte = db.query(ReporteFinanciero).filter(ReporteFinanciero.id == reporte_id).first()
    
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    
    # Simulación de exportación - en implementación real se generaría el archivo
    if configuracion.formato == "pdf":
        archivo_ruta = f"/tmp/reporte_{reporte_id}.pdf"
    elif configuracion.formato == "excel":
        archivo_ruta = f"/tmp/reporte_{reporte_id}.xlsx"
    elif configuracion.formato == "csv":
        archivo_ruta = f"/tmp/reporte_{reporte_id}.csv"
    else:
        archivo_ruta = f"/tmp/reporte_{reporte_id}.json"
    
    return {
        "mensaje": f"Reporte exportado en formato {configuracion.formato}",
        "archivo_ruta": archivo_ruta,
        "formato": configuracion.formato,
        "tamaño_estimado": "2.5 MB"
    }

# === COMPARACIONES ===

@router.get("/{reporte_id}/comparar", response_model=ReporteComparativo, summary="Comparar reporte")
def comparar_reporte(
    reporte_id: int,
    reporte_comparar_id: int = Query(..., description="ID del reporte a comparar"),
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Compara dos reportes financieros.
    """
    from app.models.reporte_financiero_model import ReporteFinanciero, EstadoResultados
    
    # Obtener reportes
    reporte_actual = db.query(ReporteFinanciero).filter(ReporteFinanciero.id == reporte_id).first()
    reporte_comparar = db.query(ReporteFinanciero).filter(ReporteFinanciero.id == reporte_comparar_id).first()
    
    if not reporte_actual or not reporte_comparar:
        raise HTTPException(status_code=404, detail="Uno o ambos reportes no encontrados")
    
    # Obtener estados de resultados
    estado_actual = db.query(EstadoResultados).filter(EstadoResultados.reporte_id == reporte_id).first()
    estado_comparar = db.query(EstadoResultados).filter(EstadoResultados.reporte_id == reporte_comparar_id).first()
    
    if not estado_actual or not estado_comparar:
        raise HTTPException(status_code=404, detail="Estados de resultados no encontrados")
    
    # Calcular variaciones
    variaciones = {}
    if estado_actual.ventas_netas > 0 and estado_comparar.ventas_netas > 0:
        variaciones['ventas'] = ((estado_actual.ventas_netas - estado_comparar.ventas_netas) / estado_comparar.ventas_netas) * 100
    if estado_actual.utilidad_bruta > 0 and estado_comparar.utilidad_bruta > 0:
        variaciones['utilidad_bruta'] = ((estado_actual.utilidad_bruta - estado_comparar.utilidad_bruta) / estado_comparar.utilidad_bruta) * 100
    if estado_actual.utilidad_neta > 0 and estado_comparar.utilidad_neta > 0:
        variaciones['utilidad_neta'] = ((estado_actual.utilidad_neta - estado_comparar.utilidad_neta) / estado_comparar.utilidad_neta) * 100
    
    # Determinar tendencias
    tendencias = {}
    for metrica, variacion in variaciones.items():
        if variacion > 5:
            tendencias[metrica] = "creciente"
        elif variacion < -5:
            tendencias[metrica] = "decreciente"
        else:
            tendencias[metrica] = "estable"
    
    # Generar recomendaciones
    recomendaciones = []
    if variaciones.get('ventas', 0) < -10:
        recomendaciones.append("Las ventas han disminuido significativamente. Revisar estrategia de marketing.")
    if variaciones.get('utilidad_bruta', 0) < -10:
        recomendaciones.append("La utilidad bruta ha disminuido. Revisar costos y precios.")
    if variaciones.get('utilidad_neta', 0) < -10:
        recomendaciones.append("La utilidad neta ha disminuido. Revisar estructura de gastos.")
    
    return ReporteComparativo(
        periodo_actual={
            "ventas_netas": estado_actual.ventas_netas,
            "utilidad_bruta": estado_actual.utilidad_bruta,
            "utilidad_neta": estado_actual.utilidad_neta,
            "margen_bruto": estado_actual.margen_bruto_porcentaje,
            "margen_neto": estado_actual.margen_neto_porcentaje
        },
        periodo_anterior={
            "ventas_netas": estado_comparar.ventas_netas,
            "utilidad_bruta": estado_comparar.utilidad_bruta,
            "utilidad_neta": estado_comparar.utilidad_neta,
            "margen_bruto": estado_comparar.margen_bruto_porcentaje,
            "margen_neto": estado_comparar.margen_neto_porcentaje
        },
        variaciones=variaciones,
        tendencias=tendencias,
        recomendaciones=recomendaciones
    )

# === UTILIDADES ===

@router.post("/{reporte_id}/regenerar", summary="Regenerar reporte")
def regenerar_reporte(
    reporte_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden regenerar
):
    """
    Regenera un reporte financiero.
    Solo usuarios administradores pueden regenerar reportes.
    """
    from app.models.reporte_financiero_model import ReporteFinanciero
    reporte = db.query(ReporteFinanciero).filter(ReporteFinanciero.id == reporte_id).first()
    
    if not reporte:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    
    # Actualizar estado a generando
    reporte.estado = EstadoReporte.GENERANDO
    db.commit()
    
    # Programar regeneración en background
    background_tasks.add_task(
        ReporteFinancieroService._generar_reporte_background,
        reporte_id,
        reporte.tipo,
        reporte.fecha_inicio,
        reporte.fecha_fin
    )
    
    return {"message": "Reporte en proceso de regeneración"}

@router.get("/tipos-disponibles", summary="Obtener tipos de reportes disponibles")
def obtener_tipos_disponibles():
    """
    Obtiene los tipos de reportes financieros disponibles.
    """
    return {
        "tipos_reporte": [tipo.value for tipo in TipoReporteFinanciero],
        "periodos": [periodo.value for periodo in PeriodoReporte],
        "estados": [estado.value for estado in EstadoReporte],
        "formatos_exportacion": ["json", "pdf", "excel", "csv"],
        "tipos_entidad_rentabilidad": ["producto", "cliente", "categoria", "proveedor"],
        "tipos_proyeccion": ["ventas", "costos", "utilidad", "flujo_caja"],
        "metodos_calculo": ["tendencia", "estacional", "regresion", "manual"],
        "categorias_metricas": ["rentabilidad", "liquidez", "eficiencia", "crecimiento"],
        "tipos_valor": ["porcentaje", "monto", "ratio", "indice"]
    }

