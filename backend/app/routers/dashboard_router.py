# app/routers/dashboard_router.py
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date, datetime

from app.db.database import get_db
from app.core.deps import require_user
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard_schema import (
    VentasResumen, VentasPorPeriodo, ProductoMasVendido, 
    ClienteTop, StockBajoItem, MetricasRendimiento, 
    TendenciaVentas, DashboardCompleto
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/ventas/resumen", response_model=VentasResumen, summary="Resumen de ventas")
def get_ventas_resumen(
    fecha_inicio: Optional[date] = Query(None, description="Fecha de inicio (YYYY-MM-DD)"),
    fecha_fin: Optional[date] = Query(None, description="Fecha de fin (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    _auth=Depends(require_user)
):
    """
    Obtiene resumen general de ventas:
    - Total de ventas y monto
    - Promedio por venta
    - Venta mayor y menor
    - Ventas del día actual
    """
    return DashboardService.get_ventas_resumen(db, fecha_inicio, fecha_fin)

@router.get("/ventas/periodo", response_model=List[VentasPorPeriodo], summary="Ventas por período")
def get_ventas_por_periodo(
    periodo: str = Query("dia", description="Período: dia, semana, mes"),
    limite: int = Query(30, ge=1, le=365, description="Número de períodos a mostrar"),
    db: Session = Depends(get_db),
    _auth=Depends(require_user)
):
    """
    Obtiene ventas agrupadas por período:
    - dia: últimos N días
    - semana: últimas N semanas  
    - mes: últimos N meses
    """
    if periodo not in ["dia", "semana", "mes"]:
        raise HTTPException(status_code=400, detail="Período debe ser: dia, semana o mes")
    
    return DashboardService.get_ventas_por_periodo(db, periodo, limite)

@router.get("/productos/mas-vendidos", response_model=List[ProductoMasVendido], summary="Productos más vendidos")
def get_productos_mas_vendidos(
    limite: int = Query(10, ge=1, le=100, description="Número de productos a mostrar"),
    db: Session = Depends(get_db),
    _auth=Depends(require_user)
):
    """
    Obtiene productos más vendidos ordenados por cantidad:
    - Cantidad total vendida
    - Monto total generado
    - Número de ventas
    """
    return DashboardService.get_productos_mas_vendidos(db, limite)

@router.get("/clientes/top", response_model=List[ClienteTop], summary="Clientes top")
def get_clientes_top(
    limite: int = Query(10, ge=1, le=100, description="Número de clientes a mostrar"),
    db: Session = Depends(get_db),
    _auth=Depends(require_user)
):
    """
    Obtiene clientes con más compras ordenados por monto total:
    - Cantidad de ventas
    - Monto total gastado
    - Promedio por compra
    """
    return DashboardService.get_clientes_top(db, limite)

@router.get("/stock/bajo", response_model=List[StockBajoItem], summary="Stock bajo")
def get_stock_bajo(
    stock_minimo: float = Query(10.0, ge=0, description="Stock mínimo requerido"),
    db: Session = Depends(get_db),
    _auth=Depends(require_user)
):
    """
    Obtiene productos con stock bajo:
    - Stock actual vs mínimo
    - Diferencia y porcentaje
    - Alertas de reposición
    """
    return DashboardService.get_stock_bajo(db, stock_minimo)

@router.get("/metricas", response_model=MetricasRendimiento, summary="Métricas de rendimiento")
def get_metricas_rendimiento(
    db: Session = Depends(get_db),
    _auth=Depends(require_user)
):
    """
    Obtiene métricas de rendimiento del sistema:
    - Ventas del último mes
    - Crecimiento de ventas
    - Productos y clientes activos
    - Ticket promedio
    - Tasa de conversión
    """
    return DashboardService.get_metricas_rendimiento(db)

@router.get("/tendencias", response_model=List[TendenciaVentas], summary="Tendencias de ventas")
def get_tendencias_ventas(
    dias: int = Query(30, ge=7, le=365, description="Número de días a analizar"),
    db: Session = Depends(get_db),
    _auth=Depends(require_user)
):
    """
    Obtiene tendencias de ventas por día:
    - Ventas diarias
    - Monto diario
    - Crecimiento día a día
    """
    return DashboardService.get_tendencias_ventas(db, dias)

@router.get("/completo", response_model=DashboardCompleto, summary="Dashboard completo")
def get_dashboard_completo(
    db: Session = Depends(get_db),
    _auth=Depends(require_user)
):
    """
    Obtiene dashboard completo con todas las métricas:
    - Resumen de ventas
    - Ventas por período
    - Productos más vendidos
    - Clientes top
    - Stock bajo
    - Métricas de rendimiento
    - Tendencias
    """
    return DashboardService.get_dashboard_completo(db)

@router.get("/ventas/estadisticas", summary="Estadísticas detalladas de ventas")
def get_ventas_estadisticas(
    fecha_inicio: Optional[date] = Query(None, description="Fecha de inicio"),
    fecha_fin: Optional[date] = Query(None, description="Fecha de fin"),
    db: Session = Depends(get_db),
    _auth=Depends(require_user)
):
    """
    Obtiene estadísticas detalladas de ventas con filtros de fecha.
    Incluye análisis de tendencias, comparaciones y métricas avanzadas.
    """
    resumen = DashboardService.get_ventas_resumen(db, fecha_inicio, fecha_fin)
    productos = DashboardService.get_productos_mas_vendidos(db, 5)
    clientes = DashboardService.get_clientes_top(db, 5)
    tendencias = DashboardService.get_tendencias_ventas(db, 30)
    
    return {
        "resumen": resumen,
        "productos_destacados": productos,
        "clientes_destacados": clientes,
        "tendencias": tendencias,
        "filtros_aplicados": {
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin
        }
    }
