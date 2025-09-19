from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from datetime import datetime, timedelta
import json

from app.db.database import get_db
from app.core.auth import get_current_user, oauth2_scheme
from app.models.user_model import User
from app.services.user_service import get_by_username
from app.models.producto_model import Producto
from app.models.cliente_model import Cliente
from app.models.venta_model import Venta, VentaItem
from app.models.compra_model import Compra
from app.models.notificacion_model import Notificacion
from app.schemas.notificacion_schema import NotificacionOut

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/test")
def test_auth(
    current_user: User = Depends(get_current_user)
):
    """Endpoint de prueba para verificar autenticación"""
    return {"message": "Autenticación exitosa", "user": current_user.username}

@router.get("/test-debug")
def test_debug(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Endpoint de prueba para debuggear autenticación"""
    try:
        from jose import jwt, JWTError
        from app.core.settings import settings
        
        SECRET_KEY = settings.SECRET_KEY
        ALGORITHM = settings.ALGORITHM
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        
        if username is None:
            return {"error": "Username not found in token"}
        
        user = get_by_username(db, username)
        if not user:
            return {"error": f"User {username} not found in database"}
        
        return {
            "message": "Debug successful",
            "username": username,
            "user_id": user.id,
            "user_role": user.role
        }
    except JWTError as e:
        return {"error": f"JWT Error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@router.get("/test-secret")
def test_secret():
    """Endpoint para verificar SECRET_KEY"""
    from app.core.settings import settings
    return {
        "secret_key": settings.SECRET_KEY,
        "algorithm": settings.ALGORITHM
    }

@router.get("/test-no-auth")
def test_no_auth():
    """Endpoint de prueba sin autenticación"""
    return {"message": "Endpoint sin autenticación funciona"}

@router.get("/completo")
def get_dashboard_completo(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener dashboard completo con todas las métricas"""
    
    # Fechas para cálculos
    hoy = datetime.now().date()
    inicio_mes = hoy.replace(day=1)
    inicio_anio = hoy.replace(month=1, day=1)
    
    # Resumen de ventas
    ventas_totales = db.query(func.count(Venta.id), func.coalesce(func.sum(Venta.total), 0)).first()
    ventas_hoy = db.query(func.count(Venta.id), func.coalesce(func.sum(Venta.total), 0)).filter(
        func.date(Venta.fecha) == hoy
    ).first()
    
    ventas_mes = db.query(func.count(Venta.id), func.coalesce(func.sum(Venta.total), 0)).filter(
        func.date(Venta.fecha) >= inicio_mes
    ).first()
    
    # Ventas por período (últimos 30 días)
    ventas_por_periodo = db.query(
        func.date(Venta.fecha).label('periodo'),
        func.count(Venta.id).label('cantidad_ventas'),
        func.coalesce(func.sum(Venta.total), 0).label('monto_total')
    ).filter(
        func.date(Venta.fecha) >= hoy - timedelta(days=30)
    ).group_by(func.date(Venta.fecha)).order_by('periodo').all()
    
    # Productos más vendidos
    productos_mas_vendidos = db.query(
        Producto.id.label('producto_id'),
        Producto.nombre.label('producto_nombre'),
        func.sum(VentaItem.cantidad).label('cantidad_vendida'),
        func.sum(VentaItem.subtotal).label('monto_total'),
        func.count(VentaItem.id).label('ventas_count')
    ).join(VentaItem, Producto.id == VentaItem.producto_id).group_by(
        Producto.id, Producto.nombre
    ).order_by(desc('cantidad_vendida')).limit(10).all()
    
    # Clientes top
    clientes_top = db.query(
        Cliente.id.label('cliente_id'),
        Cliente.nombre.label('cliente_nombre'),
        func.count(Venta.id).label('cantidad_ventas'),
        func.sum(Venta.total).label('monto_total')
    ).join(Venta, Cliente.id == Venta.cliente_id).group_by(
        Cliente.id, Cliente.nombre
    ).order_by(desc('monto_total')).limit(10).all()
    
    # Stock bajo
    stock_bajo = db.query(
        Producto.id.label('producto_id'),
        Producto.nombre.label('producto_nombre'),
        Producto.stock.label('stock_actual'),
        Producto.stock_minimo.label('stock_minimo')
    ).filter(
        Producto.stock <= Producto.stock_minimo,
        Producto.activo == True
    ).all()
    
    # Calcular métricas adicionales
    total_ventas, total_monto = ventas_totales
    ventas_hoy_count, monto_hoy = ventas_hoy
    ventas_mes_count, monto_mes = ventas_mes
    
    promedio_venta = total_monto / total_ventas if total_ventas > 0 else 0
    
    # Ventas mayor y menor
    venta_mayor = db.query(func.max(Venta.total)).scalar() or 0
    venta_menor = db.query(func.min(Venta.total)).scalar() or 0
    
    # Métricas adicionales
    productos_activos = db.query(func.count(Producto.id)).filter(Producto.activo == True).scalar()
    clientes_activos = db.query(func.count(Cliente.id)).scalar()
    
    # Crecimiento de ventas (comparar con mes anterior)
    mes_anterior_inicio = (inicio_mes - timedelta(days=1)).replace(day=1)
    ventas_mes_anterior = db.query(func.count(Venta.id), func.coalesce(func.sum(Venta.total), 0)).filter(
        and_(
            func.date(Venta.fecha) >= mes_anterior_inicio,
            func.date(Venta.fecha) < inicio_mes
        )
    ).first()
    
    ventas_mes_anterior_count, monto_mes_anterior = ventas_mes_anterior
    crecimiento_ventas = 0
    if monto_mes_anterior > 0:
        crecimiento_ventas = ((monto_mes - monto_mes_anterior) / monto_mes_anterior) * 100
    
    # Tendencias (últimos 7 días)
    tendencias = []
    for i in range(7):
        fecha = hoy - timedelta(days=i)
        ventas_dia = db.query(
            func.count(Venta.id).label('ventas'),
            func.coalesce(func.sum(Venta.total), 0).label('monto')
        ).filter(func.date(Venta.fecha) == fecha).first()
        
        ventas_count, monto = ventas_dia
        tendencias.append({
            'fecha': fecha.isoformat(),
            'ventas': ventas_count,
            'monto': float(monto),
            'crecimiento_diario': 0  # Se puede calcular comparando con el día anterior
        })
    
    # Procesar stock bajo
    stock_bajo_procesado = []
    for item in stock_bajo:
        diferencia = item.stock_minimo - item.stock_actual
        porcentaje = (diferencia / item.stock_minimo) * 100 if item.stock_minimo > 0 else 0
        stock_bajo_procesado.append({
            'producto_id': item.producto_id,
            'producto_nombre': item.producto_nombre,
            'stock_actual': item.stock_actual,
            'stock_minimo': item.stock_minimo,
            'diferencia': diferencia,
            'porcentaje': round(porcentaje, 1)
        })
    
    # Procesar ventas por período
    ventas_por_periodo_procesado = []
    for item in ventas_por_periodo:
        promedio = item.monto_total / item.cantidad_ventas if item.cantidad_ventas > 0 else 0
        ventas_por_periodo_procesado.append({
            'periodo': item.periodo.isoformat(),
            'cantidad_ventas': item.cantidad_ventas,
            'monto_total': float(item.monto_total),
            'promedio': round(promedio, 2)
        })
    
    # Procesar productos más vendidos
    productos_mas_vendidos_procesado = []
    for item in productos_mas_vendidos:
        productos_mas_vendidos_procesado.append({
            'producto_id': item.producto_id,
            'producto_nombre': item.producto_nombre,
            'cantidad_vendida': item.cantidad_vendida,
            'monto_total': float(item.monto_total),
            'ventas_count': item.ventas_count
        })
    
    # Procesar clientes top
    clientes_top_procesado = []
    for item in clientes_top:
        promedio_compra = item.monto_total / item.cantidad_ventas if item.cantidad_ventas > 0 else 0
        clientes_top_procesado.append({
            'cliente_id': item.cliente_id,
            'cliente_nombre': item.cliente_nombre,
            'cantidad_ventas': item.cantidad_ventas,
            'monto_total': float(item.monto_total),
            'promedio_compra': round(promedio_compra, 2)
        })
    
    return {
        'resumen_ventas': {
            'total_ventas': total_ventas,
            'total_monto': float(total_monto),
            'promedio_venta': round(promedio_venta, 2),
            'venta_mayor': float(venta_mayor),
            'venta_menor': float(venta_menor),
            'ventas_hoy': ventas_hoy_count,
            'monto_hoy': float(monto_hoy)
        },
        'ventas_por_periodo': ventas_por_periodo_procesado,
        'productos_mas_vendidos': productos_mas_vendidos_procesado,
        'clientes_top': clientes_top_procesado,
        'stock_bajo': stock_bajo_procesado,
        'metricas': {
            'ventas_ultimo_mes': ventas_mes_count,
            'crecimiento_ventas': round(crecimiento_ventas, 2),
            'productos_activos': productos_activos,
            'clientes_activos': clientes_activos,
            'ticket_promedio': round(promedio_venta, 2),
            'conversion_rate': 0  # Se puede calcular con más datos
        },
        'tendencias': tendencias,
        'ultima_actualizacion': datetime.now().isoformat()
    }

@router.get("/ventas/estadisticas")
def get_estadisticas_ventas(
    fecha_inicio: Optional[str] = Query(None, description="Fecha de inicio (YYYY-MM-DD)"),
    fecha_fin: Optional[str] = Query(None, description="Fecha de fin (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener estadísticas detalladas de ventas"""
    
    # Fechas por defecto (último mes)
    if not fecha_inicio:
        fecha_inicio = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not fecha_fin:
        fecha_fin = datetime.now().strftime('%Y-%m-%d')
    
    fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
    fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    
    # Filtros de fecha
    filtros_fecha = and_(
        func.date(Venta.fecha) >= fecha_inicio_dt,
        func.date(Venta.fecha) <= fecha_fin_dt
    )
    
    # Resumen general
    resumen = db.query(
        func.count(Venta.id).label('total_ventas'),
        func.coalesce(func.sum(Venta.total), 0).label('total_monto'),
        func.coalesce(func.avg(Venta.total), 0).label('promedio_venta'),
        func.max(Venta.total).label('venta_mayor'),
        func.min(Venta.total).label('venta_menor')
    ).filter(filtros_fecha).first()
    
    # Ventas de hoy
    hoy = datetime.now().date()
    ventas_hoy = db.query(
        func.count(Venta.id).label('ventas_hoy'),
        func.coalesce(func.sum(Venta.total), 0).label('monto_hoy')
    ).filter(func.date(Venta.fecha) == hoy).first()
    
    # Productos destacados
    productos_destacados = db.query(
        Producto.id.label('producto_id'),
        Producto.nombre.label('producto_nombre'),
        func.sum(VentaItem.cantidad).label('cantidad_vendida'),
        func.sum(VentaItem.subtotal).label('monto_total'),
        func.count(VentaItem.id).label('ventas_count')
    ).join(VentaItem, Producto.id == VentaItem.producto_id).join(
        Venta, VentaItem.venta_id == Venta.id
    ).filter(
        filtros_fecha
    ).group_by(Producto.id, Producto.nombre).order_by(
        desc('cantidad_vendida')
    ).limit(10).all()
    
    # Clientes destacados
    clientes_destacados = db.query(
        Cliente.id.label('cliente_id'),
        Cliente.nombre.label('cliente_nombre'),
        func.count(Venta.id).label('cantidad_ventas'),
        func.sum(Venta.total).label('monto_total')
    ).join(Venta, Cliente.id == Venta.cliente_id).filter(
        filtros_fecha
    ).group_by(Cliente.id, Cliente.nombre).order_by(
        desc('monto_total')
    ).limit(10).all()
    
    # Tendencias diarias
    tendencias = db.query(
        func.date(Venta.fecha).label('fecha'),
        func.count(Venta.id).label('ventas'),
        func.coalesce(func.sum(Venta.total), 0).label('monto')
    ).filter(filtros_fecha).group_by(
        func.date(Venta.fecha)
    ).order_by('fecha').all()
    
    # Procesar datos
    resumen_procesado = {
        'total_ventas': resumen.total_ventas,
        'total_monto': float(resumen.total_monto),
        'promedio_venta': round(float(resumen.promedio_venta), 2),
        'venta_mayor': float(resumen.venta_mayor or 0),
        'venta_menor': float(resumen.venta_menor or 0),
        'ventas_hoy': ventas_hoy.ventas_hoy,
        'monto_hoy': float(ventas_hoy.monto_hoy)
    }
    
    productos_destacados_procesado = []
    for item in productos_destacados:
        productos_destacados_procesado.append({
            'producto_id': item.producto_id,
            'producto_nombre': item.producto_nombre,
            'cantidad_vendida': item.cantidad_vendida,
            'monto_total': float(item.monto_total),
            'ventas_count': item.ventas_count
        })
    
    clientes_destacados_procesado = []
    for item in clientes_destacados:
        promedio_compra = item.monto_total / item.cantidad_ventas if item.cantidad_ventas > 0 else 0
        clientes_destacados_procesado.append({
            'cliente_id': item.cliente_id,
            'cliente_nombre': item.cliente_nombre,
            'cantidad_ventas': item.cantidad_ventas,
            'monto_total': float(item.monto_total),
            'promedio_compra': round(promedio_compra, 2)
        })
    
    tendencias_procesado = []
    for item in tendencias:
        tendencias_procesado.append({
            'fecha': item.fecha.isoformat(),
            'ventas': item.ventas,
            'monto': float(item.monto),
            'crecimiento_diario': 0  # Se puede calcular comparando con el día anterior
        })
    
    return {
        'resumen': resumen_procesado,
        'productos_destacados': productos_destacados_procesado,
        'clientes_destacados': clientes_destacados_procesado,
        'tendencias': tendencias_procesado,
        'filtros_aplicados': {
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin
        }
    }

@router.get("/productos/mas-vendidos")
def get_productos_mas_vendidos(
    limite: int = Query(10, ge=1, le=50, description="Número de productos a retornar"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener productos más vendidos"""
    
    productos = db.query(
        Producto.id.label('producto_id'),
        Producto.nombre.label('producto_nombre'),
        func.sum(VentaItem.cantidad).label('cantidad_vendida'),
        func.sum(VentaItem.subtotal).label('monto_total'),
        func.count(VentaItem.id).label('ventas_count')
    ).join(VentaItem, Producto.id == VentaItem.producto_id).group_by(
        Producto.id, Producto.nombre
    ).order_by(desc('cantidad_vendida')).limit(limite).all()
    
    resultado = []
    for item in productos:
        resultado.append({
            'producto_id': item.producto_id,
            'producto_nombre': item.producto_nombre,
            'cantidad_vendida': item.cantidad_vendida,
            'monto_total': float(item.monto_total),
            'ventas_count': item.ventas_count
        })
    
    return resultado

@router.get("/clientes/top")
def get_clientes_top(
    limite: int = Query(10, ge=1, le=50, description="Número de clientes a retornar"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener clientes top por monto de compras"""
    
    clientes = db.query(
        Cliente.id.label('cliente_id'),
        Cliente.nombre.label('cliente_nombre'),
        func.count(Venta.id).label('cantidad_ventas'),
        func.sum(Venta.total).label('monto_total')
    ).join(Venta, Cliente.id == Venta.cliente_id).group_by(
        Cliente.id, Cliente.nombre
    ).order_by(desc('monto_total')).limit(limite).all()
    
    resultado = []
    for item in clientes:
        promedio_compra = item.monto_total / item.cantidad_ventas if item.cantidad_ventas > 0 else 0
        resultado.append({
            'cliente_id': item.cliente_id,
            'cliente_nombre': item.cliente_nombre,
            'cantidad_ventas': item.cantidad_ventas,
            'monto_total': float(item.monto_total),
            'promedio_compra': round(promedio_compra, 2)
        })
    
    return resultado

@router.get("/stock/bajo")
def get_stock_bajo(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener productos con stock bajo"""
    
    productos = db.query(
        Producto.id.label('producto_id'),
        Producto.nombre.label('producto_nombre'),
        Producto.stock.label('stock_actual'),
        Producto.stock_minimo.label('stock_minimo')
    ).filter(
        Producto.stock <= Producto.stock_minimo,
        Producto.activo == True
    ).all()
    
    resultado = []
    for item in productos:
        diferencia = item.stock_minimo - item.stock_actual
        porcentaje = (diferencia / item.stock_minimo) * 100 if item.stock_minimo > 0 else 0
        resultado.append({
            'producto_id': item.producto_id,
            'producto_nombre': item.producto_nombre,
            'stock_actual': item.stock_actual,
            'stock_minimo': item.stock_minimo,
            'diferencia': diferencia,
            'porcentaje': round(porcentaje, 1)
        })
    
    return resultado

@router.get("/tendencias")
def get_tendencias(
    dias: int = Query(7, ge=1, le=30, description="Número de días para analizar"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener tendencias de ventas"""
    
    fecha_inicio = datetime.now().date() - timedelta(days=dias)
    
    tendencias = db.query(
        func.date(Venta.fecha).label('fecha'),
        func.count(Venta.id).label('ventas'),
        func.coalesce(func.sum(Venta.total), 0).label('monto')
    ).filter(
        func.date(Venta.fecha) >= fecha_inicio
    ).group_by(
        func.date(Venta.fecha)
    ).order_by('fecha').all()
    
    resultado = []
    for item in tendencias:
        resultado.append({
            'fecha': item.fecha.isoformat(),
            'ventas': item.ventas,
            'monto': float(item.monto),
            'crecimiento_diario': 0  # Se puede calcular comparando con el día anterior
        })
    
    return resultado