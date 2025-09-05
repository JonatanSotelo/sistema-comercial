# app/schemas/dashboard_schema.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal

class VentaEstadistica(BaseModel):
    """Estadística de una venta individual"""
    id: int
    fecha: datetime
    total: float
    cliente_nombre: Optional[str] = None
    items_count: int

class VentasResumen(BaseModel):
    """Resumen general de ventas"""
    total_ventas: int
    total_monto: float
    promedio_venta: float
    venta_mayor: float
    venta_menor: float
    ventas_hoy: int
    monto_hoy: float

class VentasPorPeriodo(BaseModel):
    """Ventas agrupadas por período"""
    periodo: str  # "2024-01", "2024-01-15", etc.
    cantidad_ventas: int
    monto_total: float
    promedio: float

class ProductoMasVendido(BaseModel):
    """Producto más vendido"""
    producto_id: int
    producto_nombre: str
    cantidad_vendida: float
    monto_total: float
    ventas_count: int

class ClienteTop(BaseModel):
    """Cliente con más compras"""
    cliente_id: int
    cliente_nombre: str
    cantidad_ventas: int
    monto_total: float
    promedio_compra: float

class StockBajoItem(BaseModel):
    """Item con stock bajo"""
    producto_id: int
    producto_nombre: str
    stock_actual: float
    stock_minimo: float = 10.0  # Valor por defecto
    diferencia: float
    porcentaje: float

class MetricasRendimiento(BaseModel):
    """Métricas de rendimiento del sistema"""
    ventas_ultimo_mes: int
    crecimiento_ventas: float  # Porcentaje
    productos_activos: int
    clientes_activos: int
    ticket_promedio: float
    conversion_rate: float  # Porcentaje

class TendenciaVentas(BaseModel):
    """Tendencia de ventas por período"""
    fecha: date
    ventas: int
    monto: float
    crecimiento_diario: float  # Porcentaje

class DashboardCompleto(BaseModel):
    """Dashboard completo con todas las métricas"""
    resumen_ventas: VentasResumen
    ventas_por_periodo: List[VentasPorPeriodo]
    productos_mas_vendidos: List[ProductoMasVendido]
    clientes_top: List[ClienteTop]
    stock_bajo: List[StockBajoItem]
    metricas: MetricasRendimiento
    tendencias: List[TendenciaVentas]
    ultima_actualizacion: datetime
