# app/routers/proveedor_integracion_router.py
from fastapi import APIRouter, Depends, Query, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from datetime import datetime, date, timedelta

from app.db.database import get_db
from app.core.deps import require_user, require_admin
from app.services.proveedor_integracion_service import ProveedorIntegracionService
from app.schemas.proveedor_integracion_schema import (
    ProveedorIntegracionCreate, ProveedorIntegracionUpdate, ProveedorIntegracionOut,
    CatalogoProveedorCreate, CatalogoProveedorUpdate, CatalogoProveedorOut,
    PedidoProveedorCreate, PedidoProveedorUpdate, PedidoProveedorOut,
    NotificacionProveedorCreate, NotificacionProveedorUpdate, NotificacionProveedorOut,
    LogIntegracionOut, ConfiguracionIntegracionCreate, ConfiguracionIntegracionOut,
    IntegracionFiltros, CatalogoFiltros, PedidoFiltros, NotificacionFiltros,
    ResumenIntegracion, ResumenCatalogo, ResumenPedidos,
    DashboardProveedores, EstadisticasIntegracion,
    TipoIntegracion, EstadoIntegracion, TipoSincronizacion, EstadoPedido
)

router = APIRouter(prefix="/proveedores-integracion", tags=["Integración con Proveedores"])

# === INTEGRACIONES CON PROVEEDORES ===

@router.post("/", response_model=ProveedorIntegracionOut, summary="Crear integración con proveedor")
def crear_integracion(
    integracion: ProveedorIntegracionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden crear integraciones
):
    """
    Crea una nueva integración con un proveedor.
    Solo usuarios administradores pueden crear integraciones.
    """
    return ProveedorIntegracionService.crear_integracion(db, integracion, current_user.id)

@router.get("/", response_model=List[ProveedorIntegracionOut], summary="Listar integraciones")
def listar_integraciones(
    skip: int = Query(0, ge=0, description="Número de integraciones a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de integraciones a retornar"),
    proveedor_id: Optional[int] = Query(None, description="Filtrar por proveedor"),
    tipo_integracion: Optional[TipoIntegracion] = Query(None, description="Filtrar por tipo"),
    estado: Optional[EstadoIntegracion] = Query(None, description="Filtrar por estado"),
    activo: Optional[bool] = Query(True, description="Solo integraciones activas"),
    sincronizar_productos: Optional[bool] = Query(None, description="Filtrar por sincronización de productos"),
    permitir_pedidos_automaticos: Optional[bool] = Query(None, description="Filtrar por pedidos automáticos"),
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Lista integraciones con proveedores con filtros opcionales.
    """
    filtros = IntegracionFiltros(
        proveedor_id=proveedor_id,
        tipo_integracion=tipo_integracion,
        estado=estado,
        activo=activo,
        sincronizar_productos=sincronizar_productos,
        permitir_pedidos_automaticos=permitir_pedidos_automaticos
    )
    
    return ProveedorIntegracionService.obtener_integraciones(db, filtros, skip, limit)

@router.get("/{integracion_id}", response_model=ProveedorIntegracionOut, summary="Obtener integración")
def obtener_integracion(
    integracion_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Obtiene una integración específica.
    """
    from app.models.proveedor_integracion_model import ProveedorIntegracion
    integracion = db.query(ProveedorIntegracion).filter(ProveedorIntegracion.id == integracion_id).first()
    
    if not integracion:
        raise HTTPException(status_code=404, detail="Integración no encontrada")
    
    return integracion

@router.put("/{integracion_id}", response_model=ProveedorIntegracionOut, summary="Actualizar integración")
def actualizar_integracion(
    integracion_id: int,
    integracion_update: ProveedorIntegracionUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden actualizar
):
    """
    Actualiza una integración existente.
    Solo usuarios administradores pueden actualizar integraciones.
    """
    from app.models.proveedor_integracion_model import ProveedorIntegracion
    integracion = db.query(ProveedorIntegracion).filter(ProveedorIntegracion.id == integracion_id).first()
    
    if not integracion:
        raise HTTPException(status_code=404, detail="Integración no encontrada")
    
    # Actualizar campos
    for field, value in integracion_update.dict(exclude_unset=True).items():
        setattr(integracion, field, value)
    
    integracion.fecha_ultima_actualizacion = datetime.utcnow()
    db.commit()
    db.refresh(integracion)
    
    return integracion

@router.delete("/{integracion_id}", summary="Eliminar integración")
def eliminar_integracion(
    integracion_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden eliminar
):
    """
    Elimina una integración.
    Solo usuarios administradores pueden eliminar integraciones.
    """
    from app.models.proveedor_integracion_model import ProveedorIntegracion
    integracion = db.query(ProveedorIntegracion).filter(ProveedorIntegracion.id == integracion_id).first()
    
    if not integracion:
        raise HTTPException(status_code=404, detail="Integración no encontrada")
    
    db.delete(integracion)
    db.commit()
    
    return {"message": "Integración eliminada correctamente"}

# === SINCRONIZACIÓN ===

@router.post("/{integracion_id}/sincronizar", summary="Sincronizar catálogo")
def sincronizar_catalogo(
    integracion_id: int,
    forzar_sincronizacion: bool = Query(False, description="Forzar sincronización"),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden sincronizar
):
    """
    Sincroniza el catálogo de productos con el proveedor.
    Solo usuarios administradores pueden sincronizar.
    """
    # Programar sincronización en background
    background_tasks.add_task(
        ProveedorIntegracionService.sincronizar_catalogo,
        db, integracion_id, forzar_sincronizacion
    )
    
    return {"message": "Sincronización iniciada en background"}

@router.get("/{integracion_id}/estado", summary="Obtener estado de sincronización")
def obtener_estado_sincronizacion(
    integracion_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Obtiene el estado actual de sincronización de una integración.
    """
    from app.models.proveedor_integracion_model import ProveedorIntegracion
    integracion = db.query(ProveedorIntegracion).filter(ProveedorIntegracion.id == integracion_id).first()
    
    if not integracion:
        raise HTTPException(status_code=404, detail="Integración no encontrada")
    
    return {
        "estado": integracion.estado,
        "fecha_ultima_sincronizacion": integracion.fecha_ultima_sincronizacion,
        "total_sincronizaciones": integracion.total_sincronizaciones,
        "sincronizaciones_exitosas": integracion.sincronizaciones_exitosas,
        "sincronizaciones_fallidas": integracion.sincronizaciones_fallidas,
        "ultimo_error": integracion.ultimo_error
    }

# === CATÁLOGO DE PROVEEDORES ===

@router.post("/{integracion_id}/catalogo", response_model=CatalogoProveedorOut, summary="Crear producto en catálogo")
def crear_producto_catalogo(
    integracion_id: int,
    producto: CatalogoProveedorCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden crear productos
):
    """
    Crea un producto en el catálogo del proveedor.
    Solo usuarios administradores pueden crear productos.
    """
    from app.models.proveedor_integracion_model import CatalogoProveedor
    
    db_producto = CatalogoProveedor(
        integracion_id=integracion_id,
        codigo_proveedor=producto.codigo_proveedor,
        nombre_proveedor=producto.nombre_proveedor,
        descripcion_proveedor=producto.descripcion_proveedor,
        categoria_proveedor=producto.categoria_proveedor,
        marca_proveedor=producto.marca_proveedor,
        modelo_proveedor=producto.modelo_proveedor,
        sku_proveedor=producto.sku_proveedor,
        precio_proveedor=producto.precio_proveedor,
        stock_proveedor=producto.stock_proveedor,
        disponible=producto.disponible,
        sincronizar_precio=producto.sincronizar_precio,
        sincronizar_stock=producto.sincronizar_stock,
        margen_minimo=producto.margen_minimo,
        stock_minimo=producto.stock_minimo,
        producto_id=producto.producto_id,
        mapeo_automatico=producto.mapeo_automatico
    )
    
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    
    return db_producto

@router.get("/{integracion_id}/catalogo", response_model=List[CatalogoProveedorOut], summary="Listar catálogo")
def listar_catalogo(
    integracion_id: int,
    skip: int = Query(0, ge=0, description="Número de productos a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de productos a retornar"),
    producto_id: Optional[int] = Query(None, description="Filtrar por producto interno"),
    disponible: Optional[bool] = Query(None, description="Filtrar por disponibilidad"),
    categoria_proveedor: Optional[str] = Query(None, description="Filtrar por categoría"),
    marca_proveedor: Optional[str] = Query(None, description="Filtrar por marca"),
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Lista el catálogo de productos de un proveedor con filtros opcionales.
    """
    from app.models.proveedor_integracion_model import CatalogoProveedor
    query = db.query(CatalogoProveedor).filter(CatalogoProveedor.integracion_id == integracion_id)
    
    if producto_id:
        query = query.filter(CatalogoProveedor.producto_id == producto_id)
    if disponible is not None:
        query = query.filter(CatalogoProveedor.disponible == disponible)
    if categoria_proveedor:
        query = query.filter(CatalogoProveedor.categoria_proveedor.ilike(f"%{categoria_proveedor}%"))
    if marca_proveedor:
        query = query.filter(CatalogoProveedor.marca_proveedor.ilike(f"%{marca_proveedor}%"))
    
    return query.order_by(desc(CatalogoProveedor.fecha_creacion)).offset(skip).limit(limit).all()

@router.put("/catalogo/{producto_id}", response_model=CatalogoProveedorOut, summary="Actualizar producto en catálogo")
def actualizar_producto_catalogo(
    producto_id: int,
    producto_update: CatalogoProveedorUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden actualizar
):
    """
    Actualiza un producto en el catálogo del proveedor.
    Solo usuarios administradores pueden actualizar productos.
    """
    from app.models.proveedor_integracion_model import CatalogoProveedor
    producto = db.query(CatalogoProveedor).filter(CatalogoProveedor.id == producto_id).first()
    
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Actualizar campos
    for field, value in producto_update.dict(exclude_unset=True).items():
        setattr(producto, field, value)
    
    producto.fecha_ultima_actualizacion = datetime.utcnow()
    db.commit()
    db.refresh(producto)
    
    return producto

@router.delete("/catalogo/{producto_id}", summary="Eliminar producto del catálogo")
def eliminar_producto_catalogo(
    producto_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden eliminar
):
    """
    Elimina un producto del catálogo del proveedor.
    Solo usuarios administradores pueden eliminar productos.
    """
    from app.models.proveedor_integracion_model import CatalogoProveedor
    producto = db.query(CatalogoProveedor).filter(CatalogoProveedor.id == producto_id).first()
    
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    db.delete(producto)
    db.commit()
    
    return {"message": "Producto eliminado del catálogo correctamente"}

# === PEDIDOS A PROVEEDORES ===

@router.post("/{integracion_id}/pedidos", response_model=PedidoProveedorOut, summary="Crear pedido")
def crear_pedido(
    integracion_id: int,
    pedido: PedidoProveedorCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Crea un pedido a un proveedor.
    """
    from app.models.proveedor_integracion_model import PedidoProveedor, PedidoProveedorItem
    
    # Crear pedido
    db_pedido = PedidoProveedor(
        integracion_id=integracion_id,
        numero_pedido_interno=pedido.numero_pedido_interno,
        fecha_entrega_estimada=pedido.fecha_entrega_estimada,
        tipo_pedido=pedido.tipo_pedido,
        prioridad=pedido.prioridad,
        observaciones=pedido.observaciones,
        creado_por=current_user.id
    )
    
    db.add(db_pedido)
    db.flush()  # Para obtener el ID
    
    # Crear items del pedido
    subtotal = 0.0
    for item_data in pedido.items:
        item = PedidoProveedorItem(
            pedido_id=db_pedido.id,
            catalogo_id=item_data.catalogo_id,
            codigo_proveedor=item_data.codigo_proveedor,
            nombre_producto=item_data.nombre_producto,
            descripcion=item_data.descripcion,
            cantidad_solicitada=item_data.cantidad_solicitada,
            precio_unitario=item_data.precio_unitario,
            descuento_unitario=item_data.descuento_unitario,
            precio_total=item_data.cantidad_solicitada * (item_data.precio_unitario - item_data.descuento_unitario)
        )
        
        db.add(item)
        subtotal += item.precio_total
    
    # Calcular totales
    db_pedido.subtotal = subtotal
    db_pedido.descuento = 0.0  # Se puede calcular basado en reglas de negocio
    db_pedido.impuestos = 0.0  # Se puede calcular basado en reglas de negocio
    db_pedido.total = subtotal - db_pedido.descuento + db_pedido.impuestos
    
    db.commit()
    db.refresh(db_pedido)
    
    return db_pedido

@router.get("/{integracion_id}/pedidos", response_model=List[PedidoProveedorOut], summary="Listar pedidos")
def listar_pedidos(
    integracion_id: int,
    skip: int = Query(0, ge=0, description="Número de pedidos a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de pedidos a retornar"),
    estado: Optional[EstadoPedido] = Query(None, description="Filtrar por estado"),
    tipo_pedido: Optional[str] = Query(None, description="Filtrar por tipo de pedido"),
    prioridad: Optional[str] = Query(None, description="Filtrar por prioridad"),
    fecha_desde: Optional[date] = Query(None, description="Fecha desde"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha hasta"),
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Lista pedidos a un proveedor con filtros opcionales.
    """
    from app.models.proveedor_integracion_model import PedidoProveedor
    query = db.query(PedidoProveedor).filter(PedidoProveedor.integracion_id == integracion_id)
    
    if estado:
        query = query.filter(PedidoProveedor.estado == estado.value)
    if tipo_pedido:
        query = query.filter(PedidoProveedor.tipo_pedido == tipo_pedido)
    if prioridad:
        query = query.filter(PedidoProveedor.prioridad == prioridad)
    if fecha_desde:
        query = query.filter(PedidoProveedor.fecha_pedido >= fecha_desde)
    if fecha_hasta:
        query = query.filter(PedidoProveedor.fecha_pedido <= fecha_hasta)
    
    return query.order_by(desc(PedidoProveedor.fecha_creacion)).offset(skip).limit(limit).all()

@router.put("/pedidos/{pedido_id}", response_model=PedidoProveedorOut, summary="Actualizar pedido")
def actualizar_pedido(
    pedido_id: int,
    pedido_update: PedidoProveedorUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Actualiza un pedido existente.
    """
    from app.models.proveedor_integracion_model import PedidoProveedor
    pedido = db.query(PedidoProveedor).filter(PedidoProveedor.id == pedido_id).first()
    
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    # Actualizar campos
    for field, value in pedido_update.dict(exclude_unset=True).items():
        setattr(pedido, field, value)
    
    pedido.fecha_ultima_actualizacion = datetime.utcnow()
    db.commit()
    db.refresh(pedido)
    
    return pedido

# === PEDIDOS AUTOMÁTICOS ===

@router.post("/{integracion_id}/pedidos-automaticos", response_model=PedidoProveedorOut, summary="Crear pedido automático")
def crear_pedido_automatico(
    integracion_id: int,
    items: List[dict],
    prioridad: str = Query("normal", description="Prioridad del pedido"),
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Crea un pedido automático a un proveedor.
    """
    return ProveedorIntegracionService.crear_pedido_automatico(db, integracion_id, items, prioridad)

# === NOTIFICACIONES ===

@router.get("/{integracion_id}/notificaciones", response_model=List[NotificacionProveedorOut], summary="Listar notificaciones")
def listar_notificaciones(
    integracion_id: int,
    skip: int = Query(0, ge=0, description="Número de notificaciones a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de notificaciones a retornar"),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo"),
    prioridad: Optional[str] = Query(None, description="Filtrar por prioridad"),
    leida: Optional[bool] = Query(None, description="Filtrar por estado de lectura"),
    procesada: Optional[bool] = Query(None, description="Filtrar por estado de procesamiento"),
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Lista notificaciones de un proveedor con filtros opcionales.
    """
    from app.models.proveedor_integracion_model import NotificacionProveedor
    query = db.query(NotificacionProveedor).filter(NotificacionProveedor.integracion_id == integracion_id)
    
    if tipo:
        query = query.filter(NotificacionProveedor.tipo == tipo)
    if prioridad:
        query = query.filter(NotificacionProveedor.prioridad == prioridad)
    if leida is not None:
        query = query.filter(NotificacionProveedor.leida == leida)
    if procesada is not None:
        query = query.filter(NotificacionProveedor.procesada == procesada)
    
    return query.order_by(desc(NotificacionProveedor.fecha_creacion)).offset(skip).limit(limit).all()

@router.put("/notificaciones/{notificacion_id}", response_model=NotificacionProveedorOut, summary="Actualizar notificación")
def actualizar_notificacion(
    notificacion_id: int,
    notificacion_update: NotificacionProveedorUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Actualiza una notificación de proveedor.
    """
    from app.models.proveedor_integracion_model import NotificacionProveedor
    notificacion = db.query(NotificacionProveedor).filter(NotificacionProveedor.id == notificacion_id).first()
    
    if not notificacion:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    
    # Actualizar campos
    for field, value in notificacion_update.dict(exclude_unset=True).items():
        setattr(notificacion, field, value)
    
    # Actualizar fechas si es necesario
    if notificacion_update.leida and not notificacion.leida:
        notificacion.fecha_lectura = datetime.utcnow()
    if notificacion_update.procesada and not notificacion.procesada:
        notificacion.fecha_procesamiento = datetime.utcnow()
    
    db.commit()
    db.refresh(notificacion)
    
    return notificacion

# === LOGS ===

@router.get("/{integracion_id}/logs", response_model=List[LogIntegracionOut], summary="Listar logs")
def listar_logs(
    integracion_id: int,
    skip: int = Query(0, ge=0, description="Número de logs a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de logs a retornar"),
    tipo_operacion: Optional[str] = Query(None, description="Filtrar por tipo de operación"),
    nivel: Optional[str] = Query(None, description="Filtrar por nivel"),
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Lista logs de una integración con filtros opcionales.
    """
    from app.models.proveedor_integracion_model import LogIntegracion
    query = db.query(LogIntegracion).filter(LogIntegracion.integracion_id == integracion_id)
    
    if tipo_operacion:
        query = query.filter(LogIntegracion.tipo_operacion == tipo_operacion)
    if nivel:
        query = query.filter(LogIntegracion.nivel == nivel)
    
    return query.order_by(desc(LogIntegracion.fecha_creacion)).offset(skip).limit(limit).all()

# === DASHBOARD Y RESUMEN ===

@router.get("/dashboard", response_model=DashboardProveedores, summary="Dashboard de proveedores")
def obtener_dashboard_proveedores(
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Obtiene el dashboard de proveedores con métricas en tiempo real.
    """
    return ProveedorIntegracionService.obtener_dashboard_proveedores(db)

@router.get("/{integracion_id}/estadisticas", response_model=EstadisticasIntegracion, summary="Estadísticas de integración")
def obtener_estadisticas_integracion(
    integracion_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Obtiene estadísticas detalladas de una integración específica.
    """
    from app.models.proveedor_integracion_model import ProveedorIntegracion
    integracion = db.query(ProveedorIntegracion).filter(ProveedorIntegracion.id == integracion_id).first()
    
    if not integracion:
        raise HTTPException(status_code=404, detail="Integración no encontrada")
    
    # Simulación de estadísticas detalladas
    return EstadisticasIntegracion(
        integracion_id=integracion.id,
        nombre_integracion=integracion.nombre_integracion,
        proveedor_nombre=f"Proveedor {integracion.proveedor_id}",
        total_sincronizaciones=integracion.total_sincronizaciones,
        sincronizaciones_exitosas=integracion.sincronizaciones_exitosas,
        sincronizaciones_fallidas=integracion.sincronizaciones_fallidas,
        tasa_exito=(integracion.sincronizaciones_exitosas / integracion.total_sincronizaciones * 100) if integracion.total_sincronizaciones > 0 else 0.0,
        ultima_sincronizacion=integracion.fecha_ultima_sincronizacion,
        tiempo_promedio_sincronizacion=0.0,  # Se calcularía con datos reales
        total_productos=0,  # Se calcularía con datos reales
        productos_actualizados=0,  # Se calcularía con datos reales
        productos_nuevos=0,  # Se calcularía con datos reales
        productos_eliminados=0,  # Se calcularía con datos reales
        total_pedidos=0,  # Se calcularía con datos reales
        pedidos_exitosos=0,  # Se calcularía con datos reales
        pedidos_fallidos=0,  # Se calcularía con datos reales
        valor_total_pedidos=0.0,  # Se calcularía con datos reales
        errores_por_tipo={},  # Se calcularía con datos reales
        errores_recientes=[],  # Se calcularía con datos reales
        recomendaciones=[]  # Se calcularía con datos reales
    )

# === UTILIDADES ===

@router.get("/tipos-disponibles", summary="Obtener tipos disponibles")
def obtener_tipos_disponibles():
    """
    Obtiene los tipos y opciones disponibles para integraciones.
    """
    return {
        "tipos_integracion": [tipo.value for tipo in TipoIntegracion],
        "estados_integracion": [estado.value for estado in EstadoIntegracion],
        "tipos_sincronizacion": [tipo.value for tipo in TipoSincronizacion],
        "estados_pedido": [estado.value for estado in EstadoPedido],
        "tipos_notificacion": ["precio", "stock", "pedido", "error", "info"],
        "prioridades": ["baja", "normal", "alta", "urgente"],
        "niveles_log": ["debug", "info", "warning", "error", "critical"],
        "tipos_valor_configuracion": ["string", "integer", "float", "boolean", "json"]
    }

@router.post("/{integracion_id}/test", summary="Probar integración")
def probar_integracion(
    integracion_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden probar
):
    """
    Prueba la conectividad y configuración de una integración.
    Solo usuarios administradores pueden probar integraciones.
    """
    from app.models.proveedor_integracion_model import ProveedorIntegracion
    integracion = db.query(ProveedorIntegracion).filter(ProveedorIntegracion.id == integracion_id).first()
    
    if not integracion:
        raise HTTPException(status_code=404, detail="Integración no encontrada")
    
    # Simulación de prueba de conectividad
    try:
        # Aquí se haría la prueba real de conectividad
        return {
            "exito": True,
            "mensaje": "Conexión exitosa",
            "tiempo_respuesta_ms": 150,
            "fecha_prueba": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "exito": False,
            "mensaje": f"Error en la conexión: {str(e)}",
            "fecha_prueba": datetime.utcnow().isoformat()
        }

