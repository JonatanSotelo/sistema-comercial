from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
from datetime import datetime, timedelta
import json

from app.db.database import get_db
from app.core.auth import get_current_user
from app.models.user_model import User
from app.models.producto_model import Producto
from app.models.compra_model import StockMovimiento
from app.models.notificacion_model import Notificacion
from app.services.notificacion_service import NotificacionService

router = APIRouter(prefix="/inventario", tags=["Inventario"])

# Schemas para inventario
class MovimientoStockBase:
    def __init__(self, **data):
        for key, value in data.items():
            setattr(self, key, value)

class MovimientoStockCreate(MovimientoStockBase):
    producto_id: int
    tipo: str  # 'IN', 'OUT', 'AJUSTE', 'TRANSFERENCIA'
    cantidad: float
    motivo: str
    referencia: Optional[str] = None
    observaciones: Optional[str] = None

class AlertaInventarioBase:
    def __init__(self, **data):
        for key, value in data.items():
            setattr(self, key, value)

class AlertaInventarioCreate(AlertaInventarioBase):
    producto_id: int
    tipo: str  # 'stock_bajo', 'stock_critico', 'agotado', 'exceso', 'vencimiento'
    nivel: str  # 'info', 'warning', 'error', 'critical'
    mensaje: str
    observaciones: Optional[str] = None

class OrdenReabastecimientoBase:
    def __init__(self, **data):
        for key, value in data.items():
            setattr(self, key, value)

class OrdenReabastecimientoCreate(OrdenReabastecimientoBase):
    producto_id: int
    cantidad_solicitada: int
    observaciones: Optional[str] = None

class ConfiguracionInventarioBase:
    def __init__(self, **data):
        for key, value in data.items():
            setattr(self, key, value)

class ConfiguracionInventarioCreate(ConfiguracionInventarioBase):
    producto_id: int
    stock_minimo: int
    stock_maximo: int
    punto_reorden: int
    dias_cobertura: int
    activo: bool = True

@router.get("/resumen")
def get_resumen_inventario(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener resumen del inventario"""
    
    # Total de productos
    total_productos = db.query(func.count(Producto.id)).filter(Producto.activo == True).scalar()
    
    # Productos con stock bajo
    productos_stock_bajo = db.query(func.count(Producto.id)).filter(
        and_(
            Producto.stock <= Producto.stock_minimo,
            Producto.activo == True
        )
    ).scalar()
    
    # Productos con stock crítico (menos del 50% del mínimo)
    productos_stock_critico = db.query(func.count(Producto.id)).filter(
        and_(
            Producto.stock < (Producto.stock_minimo * 0.5),
            Producto.activo == True
        )
    ).scalar()
    
    # Productos agotados
    productos_agotados = db.query(func.count(Producto.id)).filter(
        and_(
            Producto.stock <= 0,
            Producto.activo == True
        )
    ).scalar()
    
    # Alertas pendientes
    alertas_pendientes = db.query(func.count(Notificacion.id)).filter(
        and_(
            Notificacion.tipo == "stock_bajo",
            Notificacion.leida == False
        )
    ).scalar()
    
    # Alertas urgentes
    alertas_urgentes = db.query(func.count(Notificacion.id)).filter(
        and_(
            Notificacion.tipo == "stock_bajo",
            Notificacion.prioridad.in_(["urgente", "alta"]),
            Notificacion.leida == False
        )
    ).scalar()
    
    # Valor total del inventario
    valor_total = db.query(func.sum(Producto.stock * Producto.costo)).filter(
        Producto.activo == True
    ).scalar() or 0
    
    # Movimientos de hoy
    hoy = datetime.now().date()
    movimientos_hoy = db.query(func.count(StockMovimiento.id)).filter(
        func.date(StockMovimiento.fecha) == hoy
    ).scalar()
    
    # Reordenes pendientes (simulado - se puede implementar con una tabla específica)
    reordenes_pendientes = productos_stock_bajo
    
    return {
        'total_productos': total_productos,
        'productos_stock_bajo': productos_stock_bajo,
        'productos_stock_critico': productos_stock_critico,
        'productos_agotados': productos_agotados,
        'alertas_pendientes': alertas_pendientes,
        'alertas_urgentes': alertas_urgentes,
        'valor_total_inventario': float(valor_total),
        'movimientos_hoy': movimientos_hoy,
        'reordenes_pendientes': reordenes_pendientes
    }

@router.get("/estadisticas")
def get_estadisticas_inventario(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener estadísticas detalladas del inventario"""
    
    # Total de productos y configurados
    total_productos = db.query(func.count(Producto.id)).filter(Producto.activo == True).scalar()
    productos_configurados = db.query(func.count(Producto.id)).filter(
        and_(
            Producto.activo == True,
            Producto.stock_minimo > 0
        )
    ).scalar()
    
    # Alertas por tipo
    alertas_por_tipo = {}
    tipos_alertas = db.query(
        Notificacion.tipo,
        func.count(Notificacion.id)
    ).filter(Notificacion.tipo.like('stock_%')).group_by(Notificacion.tipo).all()
    
    for tipo, count in tipos_alertas:
        alertas_por_tipo[tipo] = count
    
    # Movimientos por tipo
    movimientos_por_tipo = {}
    tipos_movimientos = db.query(
        StockMovimiento.tipo,
        func.count(StockMovimiento.id)
    ).group_by(StockMovimiento.tipo).all()
    
    for tipo, count in tipos_movimientos:
        movimientos_por_tipo[tipo] = count
    
    # Valor del inventario por categoría
    valor_por_categoria = {}
    categorias = db.query(
        Producto.categoria,
        func.sum(Producto.stock * Producto.costo)
    ).filter(Producto.activo == True).group_by(Producto.categoria).all()
    
    for categoria, valor in categorias:
        valor_por_categoria[categoria] = float(valor or 0)
    
    # Productos más movidos
    productos_mas_movidos = db.query(
        Producto.id.label('producto_id'),
        Producto.nombre.label('producto_nombre'),
        func.count(StockMovimiento.id).label('total_movimientos')
    ).join(StockMovimiento, Producto.id == StockMovimiento.producto_id).group_by(
        Producto.id, Producto.nombre
    ).order_by(desc('total_movimientos')).limit(10).all()
    
    # Tendencia de stock (últimos 30 días)
    fecha_inicio = datetime.now().date() - timedelta(days=30)
    tendencia_stock = []
    
    for i in range(30):
        fecha = fecha_inicio + timedelta(days=i)
        total_stock = db.query(func.sum(Producto.stock)).filter(Producto.activo == True).scalar() or 0
        valor_total = db.query(func.sum(Producto.stock * Producto.costo)).filter(Producto.activo == True).scalar() or 0
        
        tendencia_stock.append({
            'fecha': fecha.isoformat(),
            'total_stock': total_stock,
            'valor_total': float(valor_total)
        })
    
    # Alertas resueltas este mes
    inicio_mes = datetime.now().date().replace(day=1)
    alertas_resueltas_mes = db.query(func.count(Notificacion.id)).filter(
        and_(
            Notificacion.tipo.like('stock_%'),
            Notificacion.procesada == True,
            func.date(Notificacion.fecha_procesamiento) >= inicio_mes
        )
    ).scalar()
    
    # Tiempo promedio de resolución (simulado)
    tiempo_promedio_resolucion = 2.5  # días
    
    return {
        'total_productos': total_productos,
        'productos_configurados': productos_configurados,
        'alertas_por_tipo': alertas_por_tipo,
        'movimientos_por_tipo': movimientos_por_tipo,
        'valor_inventario_por_categoria': valor_por_categoria,
        'productos_mas_movidos': [
            {
                'producto_id': item.producto_id,
                'producto_nombre': item.producto_nombre,
                'total_movimientos': item.total_movimientos
            }
            for item in productos_mas_movidos
        ],
        'tendencia_stock': tendencia_stock,
        'alertas_resueltas_mes': alertas_resueltas_mes,
        'tiempo_promedio_resolucion': tiempo_promedio_resolucion
    }

@router.get("/movimientos")
def get_movimientos_stock(
    producto_id: Optional[int] = Query(None, description="Filtrar por producto"),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo de movimiento"),
    fecha_desde: Optional[str] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    fecha_hasta: Optional[str] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Número de página"),
    per_page: int = Query(50, ge=1, le=100, description="Elementos por página"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener movimientos de stock"""
    
    query = db.query(StockMovimiento)
    
    # Aplicar filtros
    if producto_id:
        query = query.filter(StockMovimiento.producto_id == producto_id)
    
    if tipo:
        query = query.filter(StockMovimiento.tipo == tipo)
    
    if fecha_desde:
        fecha_desde_dt = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
        query = query.filter(func.date(StockMovimiento.fecha) >= fecha_desde_dt)
    
    if fecha_hasta:
        fecha_hasta_dt = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
        query = query.filter(func.date(StockMovimiento.fecha) <= fecha_hasta_dt)
    
    # Ordenar por fecha (más recientes primero)
    query = query.order_by(desc(StockMovimiento.fecha))
    
    # Paginación
    offset = (page - 1) * per_page
    movimientos = query.offset(offset).limit(per_page).all()
    
    resultado = []
    for movimiento in movimientos:
        resultado.append({
            'id': movimiento.id,
            'producto_id': movimiento.producto_id,
            'tipo': movimiento.tipo,
            'cantidad': movimiento.cantidad,
            'motivo': movimiento.motivo,
            'referencia': movimiento.referencia,
            'usuario_id': movimiento.usuario_id,
            'fecha': movimiento.fecha.isoformat() if movimiento.fecha else None,
            'observaciones': movimiento.observaciones
        })
    
    return resultado

@router.post("/movimientos")
def create_movimiento_stock(
    movimiento_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear movimiento de stock"""
    
    # Validar datos
    required_fields = ['producto_id', 'tipo', 'cantidad', 'motivo']
    for field in required_fields:
        if field not in movimiento_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Campo requerido: {field}"
            )
    
    # Verificar que el producto existe
    producto = db.query(Producto).filter(Producto.id == movimiento_data['producto_id']).first()
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    
    # Crear movimiento
    movimiento = StockMovimiento(
        producto_id=movimiento_data['producto_id'],
        tipo=movimiento_data['tipo'],
        cantidad=movimiento_data['cantidad'],
        motivo=movimiento_data['motivo'],
        referencia=movimiento_data.get('referencia'),
        usuario_id=current_user.id,
        fecha=datetime.now(),
        observaciones=movimiento_data.get('observaciones')
    )
    
    db.add(movimiento)
    db.commit()
    db.refresh(movimiento)
    
    # Actualizar stock del producto
    if movimiento_data['tipo'] == 'IN':
        producto.stock += movimiento_data['cantidad']
    elif movimiento_data['tipo'] == 'OUT':
        producto.stock -= movimiento_data['cantidad']
    elif movimiento_data['tipo'] == 'AJUSTE':
        producto.stock = movimiento_data['cantidad']
    
    db.commit()
    
    # Crear notificación si el stock está bajo
    if producto.stock <= producto.stock_minimo:
        NotificacionService.crear_notificacion_stock_bajo(
            db, producto.id, producto.stock, producto.stock_minimo, current_user.id
        )
    
    return {
        'id': movimiento.id,
        'producto_id': movimiento.producto_id,
        'tipo': movimiento.tipo,
        'cantidad': movimiento.cantidad,
        'motivo': movimiento.motivo,
        'referencia': movimiento.referencia,
        'usuario_id': movimiento.usuario_id,
        'fecha': movimiento.fecha.isoformat() if movimiento.fecha else None,
        'observaciones': movimiento.observaciones
    }

@router.get("/alertas")
def get_alertas_inventario(
    nivel: Optional[str] = Query(None, description="Filtrar por nivel de alerta"),
    pendientes: bool = Query(False, description="Solo alertas pendientes"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener alertas de inventario"""
    
    query = db.query(Notificacion).filter(Notificacion.tipo.like('stock_%'))
    
    if nivel:
        query = query.filter(Notificacion.prioridad == nivel)
    
    if pendientes:
        query = query.filter(Notificacion.leida == False)
    
    query = query.order_by(desc(Notificacion.fecha_creacion))
    
    alertas = query.all()
    
    resultado = []
    for alerta in alertas:
        resultado.append({
            'id': alerta.id,
            'producto_id': alerta.entidad_id,
            'tipo': alerta.tipo,
            'nivel': alerta.prioridad,
            'mensaje': alerta.mensaje,
            'fecha_creacion': alerta.fecha_creacion.isoformat(),
            'fecha_resolucion': alerta.fecha_procesamiento.isoformat() if alerta.fecha_procesamiento else None,
            'resuelta': alerta.procesada,
            'accion_requerida': alerta.accion_requerida
        })
    
    return resultado

@router.get("/alertas/pendientes")
def get_alertas_pendientes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener alertas pendientes de inventario"""
    
    alertas = db.query(Notificacion).filter(
        and_(
            Notificacion.tipo.like('stock_%'),
            Notificacion.leida == False
        )
    ).order_by(desc(Notificacion.fecha_creacion)).all()
    
    resultado = []
    for alerta in alertas:
        resultado.append({
            'id': alerta.id,
            'producto_id': alerta.entidad_id,
            'tipo': alerta.tipo,
            'nivel': alerta.prioridad,
            'mensaje': alerta.mensaje,
            'fecha_creacion': alerta.fecha_creacion.isoformat(),
            'accion_requerida': alerta.accion_requerida
        })
    
    return resultado

@router.get("/alertas/urgentes")
def get_alertas_urgentes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener alertas urgentes de inventario"""
    
    alertas = db.query(Notificacion).filter(
        and_(
            Notificacion.tipo.like('stock_%'),
            Notificacion.prioridad.in_(['urgente', 'alta']),
            Notificacion.leida == False
        )
    ).order_by(desc(Notificacion.fecha_creacion)).all()
    
    resultado = []
    for alerta in alertas:
        resultado.append({
            'id': alerta.id,
            'producto_id': alerta.entidad_id,
            'tipo': alerta.tipo,
            'nivel': alerta.prioridad,
            'mensaje': alerta.mensaje,
            'fecha_creacion': alerta.fecha_creacion.isoformat(),
            'accion_requerida': alerta.accion_requerida
        })
    
    return resultado

@router.patch("/alertas/{alerta_id}/resolver")
def resolver_alerta(
    alerta_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Resolver alerta de inventario"""
    
    alerta = db.query(Notificacion).filter(Notificacion.id == alerta_id).first()
    if not alerta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta no encontrada"
        )
    
    alerta.procesada = True
    alerta.fecha_procesamiento = datetime.now()
    db.commit()
    
    return {"message": "Alerta resuelta correctamente"}

@router.get("/reordenes")
def get_ordenes_reabastecimiento(
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener órdenes de reabastecimiento (simulado)"""
    
    # En una implementación real, esto vendría de una tabla específica
    # Por ahora, generamos órdenes basadas en productos con stock bajo
    
    productos_stock_bajo = db.query(Producto).filter(
        and_(
            Producto.stock <= Producto.stock_minimo,
            Producto.activo == True
        )
    ).all()
    
    resultado = []
    for producto in productos_stock_bajo:
        cantidad_solicitada = producto.stock_minimo * 2  # Solicitar el doble del mínimo
        
        resultado.append({
            'id': f"REQ-{producto.id}",
            'producto_id': producto.id,
            'producto_nombre': producto.nombre,
            'cantidad_solicitada': cantidad_solicitada,
            'cantidad_aprobada': None,
            'estado': 'pendiente',
            'fecha_solicitud': datetime.now().isoformat(),
            'fecha_aprobacion': None,
            'fecha_completado': None,
            'solicitado_por': current_user.id,
            'aprobado_por': None,
            'observaciones': f"Stock actual: {producto.stock}, Mínimo: {producto.stock_minimo}"
        })
    
    return resultado

@router.post("/generar-reorden")
def generar_orden_reabastecimiento(
    orden_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generar orden de reabastecimiento"""
    
    producto_id = orden_data.get('producto_id')
    cantidad_solicitada = orden_data.get('cantidad_solicitada')
    
    if not producto_id or not cantidad_solicitada:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="producto_id y cantidad_solicitada son requeridos"
        )
    
    # Verificar que el producto existe
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    
    # Crear orden (simulado)
    orden = {
        'id': f"REQ-{producto_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        'producto_id': producto_id,
        'producto_nombre': producto.nombre,
        'cantidad_solicitada': cantidad_solicitada,
        'cantidad_aprobada': None,
        'estado': 'pendiente',
        'fecha_solicitud': datetime.now().isoformat(),
        'fecha_aprobacion': None,
        'fecha_completado': None,
        'solicitado_por': current_user.id,
        'aprobado_por': None,
        'observaciones': orden_data.get('observaciones', '')
    }
    
    return orden

@router.patch("/reordenes/{orden_id}/aprobar")
def aprobar_orden_reabastecimiento(
    orden_id: str,
    cantidad_aprobada: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Aprobar orden de reabastecimiento"""
    
    # En una implementación real, esto actualizaría la base de datos
    return {"message": f"Orden {orden_id} aprobada correctamente"}

@router.patch("/reordenes/{orden_id}/rechazar")
def rechazar_orden_reabastecimiento(
    orden_id: str,
    motivo: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Rechazar orden de reabastecimiento"""
    
    # En una implementación real, esto actualizaría la base de datos
    return {"message": f"Orden {orden_id} rechazada correctamente"}

@router.get("/configuraciones")
def get_configuraciones_inventario(
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener configuraciones de inventario (simulado)"""
    
    # En una implementación real, esto vendría de una tabla específica
    # Por ahora, generamos configuraciones basadas en productos
    
    productos = db.query(Producto).filter(Producto.activo == True).all()
    
    resultado = []
    for producto in productos:
        resultado.append({
            'id': f"CONF-{producto.id}",
            'producto_id': producto.id,
            'producto_nombre': producto.nombre,
            'stock_minimo': producto.stock_minimo,
            'stock_maximo': producto.stock_minimo * 3,  # Máximo = 3x el mínimo
            'punto_reorden': producto.stock_minimo,
            'dias_cobertura': 30,  # Días de cobertura estimados
            'activo': True,
            'created_at': producto.created_at.isoformat() if producto.created_at else None,
            'updated_at': producto.updated_at.isoformat() if producto.updated_at else None
        })
    
    return resultado

@router.post("/configuraciones")
def create_configuracion_inventario(
    config_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear configuración de inventario"""
    
    producto_id = config_data.get('producto_id')
    if not producto_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="producto_id es requerido"
        )
    
    # Verificar que el producto existe
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )
    
    # Actualizar configuración del producto
    producto.stock_minimo = config_data.get('stock_minimo', producto.stock_minimo)
    db.commit()
    
    return {
        'id': f"CONF-{producto_id}",
        'producto_id': producto_id,
        'producto_nombre': producto.nombre,
        'stock_minimo': producto.stock_minimo,
        'stock_maximo': config_data.get('stock_maximo', producto.stock_minimo * 3),
        'punto_reorden': config_data.get('punto_reorden', producto.stock_minimo),
        'dias_cobertura': config_data.get('dias_cobertura', 30),
        'activo': True,
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }

@router.post("/procesar-alertas")
def procesar_alertas_inventario(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Procesar alertas de inventario automáticamente"""
    
    # Obtener productos con stock bajo
    productos_stock_bajo = db.query(Producto).filter(
        and_(
            Producto.stock <= Producto.stock_minimo,
            Producto.activo == True
        )
    ).all()
    
    alertas_creadas = 0
    for producto in productos_stock_bajo:
        # Verificar si ya existe una alerta pendiente para este producto
        alerta_existente = db.query(Notificacion).filter(
            and_(
                Notificacion.tipo == "stock_bajo",
                Notificacion.entidad_id == producto.id,
                Notificacion.leida == False
            )
        ).first()
        
        if not alerta_existente:
            NotificacionService.crear_notificacion_stock_bajo(
                db, producto.id, producto.stock, producto.stock_minimo, current_user.id
            )
            alertas_creadas += 1
    
    return {
        "message": f"Se procesaron {len(productos_stock_bajo)} productos y se crearon {alertas_creadas} alertas"
    }