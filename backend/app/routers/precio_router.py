# app/routers/precio_router.py
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional, List
from datetime import datetime

from app.db.database import get_db
from app.core.deps import require_user, require_admin
from app.services.precio_service import PrecioService
from app.schemas.precio_schema import (
    PrecioProductoCreate, PrecioProductoUpdate, PrecioProductoOut,
    PrecioVolumenCreate, PrecioVolumenUpdate, PrecioVolumenOut,
    PrecioCategoriaCreate, PrecioCategoriaUpdate, PrecioCategoriaOut,
    PrecioEstacionalCreate, PrecioEstacionalUpdate, PrecioEstacionalOut,
    PrecioHistorialOut, PrecioAplicadoOut,
    PrecioFiltros, PrecioResumen, PrecioEstadisticas,
    PrecioAplicarRequest, PrecioAplicarResponse,
    TipoPrecio, EstadoPrecio
)

router = APIRouter(prefix="/precios", tags=["Precios Dinámicos"])

# === PRECIOS DE PRODUCTO ===

@router.post("/productos", response_model=PrecioProductoOut, summary="Crear precio de producto")
def crear_precio_producto(
    precio: PrecioProductoCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden crear precios
):
    """
    Crea un nuevo precio dinámico para un producto.
    Solo usuarios administradores pueden crear precios.
    """
    # Verificar que el producto existe
    from app.models.producto_model import Producto
    producto = db.query(Producto).filter(Producto.id == precio.producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Verificar que el cliente existe si se especifica
    if precio.cliente_id:
        from app.models.cliente_model import Cliente
        cliente = db.query(Cliente).filter(Cliente.id == precio.cliente_id).first()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    return PrecioService.crear_precio_producto(db, precio, current_user.id)

@router.get("/productos", response_model=List[PrecioProductoOut], summary="Listar precios de producto")
def listar_precios_producto(
    skip: int = Query(0, ge=0, description="Número de precios a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de precios a retornar"),
    producto_id: Optional[int] = Query(None, description="Filtrar por producto"),
    cliente_id: Optional[int] = Query(None, description="Filtrar por cliente"),
    categoria_id: Optional[int] = Query(None, description="Filtrar por categoría"),
    tipo: Optional[TipoPrecio] = Query(None, description="Filtrar por tipo"),
    estado: Optional[EstadoPrecio] = Query(None, description="Filtrar por estado"),
    fecha_desde: Optional[datetime] = Query(None, description="Fecha desde"),
    fecha_hasta: Optional[datetime] = Query(None, description="Fecha hasta"),
    solo_activos: bool = Query(True, description="Solo precios activos"),
    solo_vigentes: bool = Query(True, description="Solo precios vigentes"),
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Lista precios de producto con filtros opcionales.
    """
    filtros = PrecioFiltros(
        producto_id=producto_id,
        cliente_id=cliente_id,
        categoria_id=categoria_id,
        tipo=tipo,
        estado=estado,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        solo_activos=solo_activos,
        solo_vigentes=solo_vigentes
    )
    
    return PrecioService.obtener_precios_producto(db, filtros, skip, limit)

@router.get("/productos/{precio_id}", response_model=PrecioProductoOut, summary="Obtener precio de producto")
def obtener_precio_producto(
    precio_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Obtiene un precio de producto específico.
    """
    from app.models.precio_model import PrecioProducto
    precio = db.query(PrecioProducto).filter(PrecioProducto.id == precio_id).first()
    
    if not precio:
        raise HTTPException(status_code=404, detail="Precio no encontrado")
    
    return precio

@router.put("/productos/{precio_id}", response_model=PrecioProductoOut, summary="Actualizar precio de producto")
def actualizar_precio_producto(
    precio_id: int,
    precio_update: PrecioProductoUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden actualizar
):
    """
    Actualiza un precio de producto existente.
    Solo usuarios administradores pueden actualizar precios.
    """
    precio = PrecioService.actualizar_precio_producto(db, precio_id, precio_update, current_user.id)
    
    if not precio:
        raise HTTPException(status_code=404, detail="Precio no encontrado")
    
    return precio

@router.delete("/productos/{precio_id}", summary="Eliminar precio de producto")
def eliminar_precio_producto(
    precio_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden eliminar
):
    """
    Elimina un precio de producto.
    Solo usuarios administradores pueden eliminar precios.
    """
    from app.models.precio_model import PrecioProducto
    precio = db.query(PrecioProducto).filter(PrecioProducto.id == precio_id).first()
    
    if not precio:
        raise HTTPException(status_code=404, detail="Precio no encontrado")
    
    # Registrar en historial
    PrecioService._registrar_historial(
        db, precio.producto_id, "eliminacion", precio.precio_especial, None,
        precio.descuento_porcentaje, None, precio.id, "precios_producto",
        current_user.id, "Precio eliminado"
    )
    
    db.delete(precio)
    db.commit()
    
    return {"message": "Precio eliminado correctamente"}

# === PRECIOS POR VOLUMEN ===

@router.post("/volumen", response_model=PrecioVolumenOut, summary="Crear precio por volumen")
def crear_precio_volumen(
    precio: PrecioVolumenCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden crear
):
    """
    Crea un nuevo precio por volumen.
    Solo usuarios administradores pueden crear precios.
    """
    # Verificar que el producto existe
    from app.models.producto_model import Producto
    producto = db.query(Producto).filter(Producto.id == precio.producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    return PrecioService.crear_precio_volumen(db, precio, current_user.id)

@router.get("/volumen", response_model=List[PrecioVolumenOut], summary="Listar precios por volumen")
def listar_precios_volumen(
    skip: int = Query(0, ge=0, description="Número de precios a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de precios a retornar"),
    producto_id: Optional[int] = Query(None, description="Filtrar por producto"),
    cliente_id: Optional[int] = Query(None, description="Filtrar por cliente"),
    categoria_id: Optional[int] = Query(None, description="Filtrar por categoría"),
    fecha_desde: Optional[datetime] = Query(None, description="Fecha desde"),
    fecha_hasta: Optional[datetime] = Query(None, description="Fecha hasta"),
    solo_activos: bool = Query(True, description="Solo precios activos"),
    solo_vigentes: bool = Query(True, description="Solo precios vigentes"),
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Lista precios por volumen con filtros opcionales.
    """
    filtros = PrecioFiltros(
        producto_id=producto_id,
        cliente_id=cliente_id,
        categoria_id=categoria_id,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        solo_activos=solo_activos,
        solo_vigentes=solo_vigentes
    )
    
    return PrecioService.obtener_precios_volumen(db, filtros, skip, limit)

@router.put("/volumen/{precio_id}", response_model=PrecioVolumenOut, summary="Actualizar precio por volumen")
def actualizar_precio_volumen(
    precio_id: int,
    precio_update: PrecioVolumenUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden actualizar
):
    """
    Actualiza un precio por volumen existente.
    Solo usuarios administradores pueden actualizar precios.
    """
    from app.models.precio_model import PrecioVolumen
    precio = db.query(PrecioVolumen).filter(PrecioVolumen.id == precio_id).first()
    
    if not precio:
        raise HTTPException(status_code=404, detail="Precio no encontrado")
    
    # Actualizar campos
    for field, value in precio_update.dict(exclude_unset=True).items():
        setattr(precio, field, value)
    
    db.commit()
    db.refresh(precio)
    
    return precio

# === PRECIOS POR CATEGORÍA ===

@router.post("/categoria", response_model=PrecioCategoriaOut, summary="Crear precio por categoría")
def crear_precio_categoria(
    precio: PrecioCategoriaCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden crear
):
    """
    Crea un nuevo precio por categoría.
    Solo usuarios administradores pueden crear precios.
    """
    return PrecioService.crear_precio_categoria(db, precio, current_user.id)

@router.get("/categoria", response_model=List[PrecioCategoriaOut], summary="Listar precios por categoría")
def listar_precios_categoria(
    skip: int = Query(0, ge=0, description="Número de precios a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de precios a retornar"),
    categoria_id: Optional[int] = Query(None, description="Filtrar por categoría"),
    cliente_id: Optional[int] = Query(None, description="Filtrar por cliente"),
    producto_id: Optional[int] = Query(None, description="Filtrar por producto"),
    fecha_desde: Optional[datetime] = Query(None, description="Fecha desde"),
    fecha_hasta: Optional[datetime] = Query(None, description="Fecha hasta"),
    solo_activos: bool = Query(True, description="Solo precios activos"),
    solo_vigentes: bool = Query(True, description="Solo precios vigentes"),
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Lista precios por categoría con filtros opcionales.
    """
    filtros = PrecioFiltros(
        categoria_id=categoria_id,
        cliente_id=cliente_id,
        producto_id=producto_id,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        solo_activos=solo_activos,
        solo_vigentes=solo_vigentes
    )
    
    return PrecioService.obtener_precios_categoria(db, filtros, skip, limit)

@router.put("/categoria/{precio_id}", response_model=PrecioCategoriaOut, summary="Actualizar precio por categoría")
def actualizar_precio_categoria(
    precio_id: int,
    precio_update: PrecioCategoriaUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden actualizar
):
    """
    Actualiza un precio por categoría existente.
    Solo usuarios administradores pueden actualizar precios.
    """
    from app.models.precio_model import PrecioCategoria
    precio = db.query(PrecioCategoria).filter(PrecioCategoria.id == precio_id).first()
    
    if not precio:
        raise HTTPException(status_code=404, detail="Precio no encontrado")
    
    # Actualizar campos
    for field, value in precio_update.dict(exclude_unset=True).items():
        setattr(precio, field, value)
    
    db.commit()
    db.refresh(precio)
    
    return precio

# === PRECIOS ESTACIONALES ===

@router.post("/estacionales", response_model=PrecioEstacionalOut, summary="Crear precio estacional")
def crear_precio_estacional(
    precio: PrecioEstacionalCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden crear
):
    """
    Crea un nuevo precio estacional.
    Solo usuarios administradores pueden crear precios.
    """
    # Verificar que el producto existe
    from app.models.producto_model import Producto
    producto = db.query(Producto).filter(Producto.id == precio.producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    return PrecioService.crear_precio_estacional(db, precio, current_user.id)

@router.get("/estacionales", response_model=List[PrecioEstacionalOut], summary="Listar precios estacionales")
def listar_precios_estacionales(
    skip: int = Query(0, ge=0, description="Número de precios a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de precios a retornar"),
    producto_id: Optional[int] = Query(None, description="Filtrar por producto"),
    cliente_id: Optional[int] = Query(None, description="Filtrar por cliente"),
    categoria_id: Optional[int] = Query(None, description="Filtrar por categoría"),
    fecha_desde: Optional[datetime] = Query(None, description="Fecha desde"),
    fecha_hasta: Optional[datetime] = Query(None, description="Fecha hasta"),
    solo_activos: bool = Query(True, description="Solo precios activos"),
    solo_vigentes: bool = Query(True, description="Solo precios vigentes"),
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Lista precios estacionales con filtros opcionales.
    """
    filtros = PrecioFiltros(
        producto_id=producto_id,
        cliente_id=cliente_id,
        categoria_id=categoria_id,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        solo_activos=solo_activos,
        solo_vigentes=solo_vigentes
    )
    
    return PrecioService.obtener_precios_estacionales(db, filtros, skip, limit)

@router.put("/estacionales/{precio_id}", response_model=PrecioEstacionalOut, summary="Actualizar precio estacional")
def actualizar_precio_estacional(
    precio_id: int,
    precio_update: PrecioEstacionalUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden actualizar
):
    """
    Actualiza un precio estacional existente.
    Solo usuarios administradores pueden actualizar precios.
    """
    from app.models.precio_model import PrecioEstacional
    precio = db.query(PrecioEstacional).filter(PrecioEstacional.id == precio_id).first()
    
    if not precio:
        raise HTTPException(status_code=404, detail="Precio no encontrado")
    
    # Actualizar campos
    for field, value in precio_update.dict(exclude_unset=True).items():
        setattr(precio, field, value)
    
    db.commit()
    db.refresh(precio)
    
    return precio

# === APLICACIÓN DE PRECIOS ===

@router.post("/aplicar", response_model=PrecioAplicarResponse, summary="Aplicar precio dinámico")
def aplicar_precio_dinamico(
    request: PrecioAplicarRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Aplica el mejor precio dinámico para un producto en una venta.
    """
    # Verificar que la venta existe
    from app.models.venta_model import Venta
    venta = db.query(Venta).filter(Venta.id == request.venta_id).first()
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    
    # Verificar que el producto existe
    from app.models.producto_model import Producto
    producto = db.query(Producto).filter(Producto.id == request.producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    return PrecioService.aplicar_precio_dinamico(db, request)

@router.get("/aplicados", response_model=List[PrecioAplicadoOut], summary="Listar precios aplicados")
def listar_precios_aplicados(
    skip: int = Query(0, ge=0, description="Número de precios a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de precios a retornar"),
    venta_id: Optional[int] = Query(None, description="Filtrar por venta"),
    producto_id: Optional[int] = Query(None, description="Filtrar por producto"),
    cliente_id: Optional[int] = Query(None, description="Filtrar por cliente"),
    tipo_precio: Optional[str] = Query(None, description="Filtrar por tipo de precio"),
    fecha_desde: Optional[datetime] = Query(None, description="Fecha desde"),
    fecha_hasta: Optional[datetime] = Query(None, description="Fecha hasta"),
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Lista precios aplicados en ventas con filtros opcionales.
    """
    from app.models.precio_model import PrecioAplicado
    from sqlalchemy import and_
    
    query = db.query(PrecioAplicado)
    
    if venta_id:
        query = query.filter(PrecioAplicado.venta_id == venta_id)
    if producto_id:
        query = query.filter(PrecioAplicado.producto_id == producto_id)
    if cliente_id:
        query = query.filter(PrecioAplicado.cliente_id == cliente_id)
    if tipo_precio:
        query = query.filter(PrecioAplicado.tipo_precio == tipo_precio)
    if fecha_desde:
        query = query.filter(PrecioAplicado.fecha_aplicacion >= fecha_desde)
    if fecha_hasta:
        query = query.filter(PrecioAplicado.fecha_aplicacion <= fecha_hasta)
    
    precios = query.order_by(desc(PrecioAplicado.fecha_aplicacion)).offset(skip).limit(limit).all()
    
    return precios

# === HISTORIAL ===

@router.get("/historial", response_model=List[PrecioHistorialOut], summary="Listar historial de precios")
def listar_historial_precios(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a retornar"),
    producto_id: Optional[int] = Query(None, description="Filtrar por producto"),
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Lista el historial de cambios de precios.
    """
    return PrecioService.obtener_historial_precios(db, producto_id, skip, limit)

# === RESUMEN Y ESTADÍSTICAS ===

@router.get("/resumen", response_model=PrecioResumen, summary="Resumen de precios")
def obtener_resumen_precios(
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Obtiene un resumen del estado de los precios.
    """
    return PrecioService.obtener_resumen_precios(db)

@router.get("/estadisticas", response_model=PrecioEstadisticas, summary="Estadísticas de precios")
def obtener_estadisticas_precios(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden ver estadísticas
):
    """
    Obtiene estadísticas detalladas de precios.
    Solo usuarios administradores pueden ver estadísticas.
    """
    return PrecioService.obtener_estadisticas_precios(db)

# === UTILIDADES ===

@router.get("/simular", response_model=PrecioAplicarResponse, summary="Simular precio dinámico")
def simular_precio_dinamico(
    producto_id: int = Query(..., description="ID del producto"),
    cliente_id: Optional[int] = Query(None, description="ID del cliente"),
    cantidad: float = Query(..., ge=0, description="Cantidad del producto"),
    db: Session = Depends(get_db),
    current_user=Depends(require_user)
):
    """
    Simula la aplicación de precio dinámico sin crear registros.
    Útil para previsualizar descuentos antes de aplicar.
    """
    # Obtener precio base del producto
    from app.models.producto_model import Producto
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Crear request de simulación
    request = PrecioAplicarRequest(
        venta_id=0,  # ID ficticio para simulación
        producto_id=producto_id,
        cliente_id=cliente_id,
        cantidad=cantidad,
        precio_base=producto.precio or 0.0
    )
    
    return PrecioService.aplicar_precio_dinamico(db, request)

@router.post("/activar/{precio_id}", summary="Activar precio")
def activar_precio(
    precio_id: int,
    tipo: str = Query(..., description="Tipo de precio (producto, volumen, categoria, estacional)"),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden activar
):
    """
    Activa un precio específico.
    Solo usuarios administradores pueden activar precios.
    """
    # Determinar la tabla según el tipo
    if tipo == "producto":
        from app.models.precio_model import PrecioProducto
        precio = db.query(PrecioProducto).filter(PrecioProducto.id == precio_id).first()
    elif tipo == "volumen":
        from app.models.precio_model import PrecioVolumen
        precio = db.query(PrecioVolumen).filter(PrecioVolumen.id == precio_id).first()
    elif tipo == "categoria":
        from app.models.precio_model import PrecioCategoria
        precio = db.query(PrecioCategoria).filter(PrecioCategoria.id == precio_id).first()
    elif tipo == "estacional":
        from app.models.precio_model import PrecioEstacional
        precio = db.query(PrecioEstacional).filter(PrecioEstacional.id == precio_id).first()
    else:
        raise HTTPException(status_code=400, detail="Tipo de precio inválido")
    
    if not precio:
        raise HTTPException(status_code=404, detail="Precio no encontrado")
    
    precio.activo = True
    db.commit()
    
    return {"message": f"Precio {tipo} activado correctamente"}

@router.post("/desactivar/{precio_id}", summary="Desactivar precio")
def desactivar_precio(
    precio_id: int,
    tipo: str = Query(..., description="Tipo de precio (producto, volumen, categoria, estacional)"),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin)  # Solo admins pueden desactivar
):
    """
    Desactiva un precio específico.
    Solo usuarios administradores pueden desactivar precios.
    """
    # Determinar la tabla según el tipo
    if tipo == "producto":
        from app.models.precio_model import PrecioProducto
        precio = db.query(PrecioProducto).filter(PrecioProducto.id == precio_id).first()
    elif tipo == "volumen":
        from app.models.precio_model import PrecioVolumen
        precio = db.query(PrecioVolumen).filter(PrecioVolumen.id == precio_id).first()
    elif tipo == "categoria":
        from app.models.precio_model import PrecioCategoria
        precio = db.query(PrecioCategoria).filter(PrecioCategoria.id == precio_id).first()
    elif tipo == "estacional":
        from app.models.precio_model import PrecioEstacional
        precio = db.query(PrecioEstacional).filter(PrecioEstacional.id == precio_id).first()
    else:
        raise HTTPException(status_code=400, detail="Tipo de precio inválido")
    
    if not precio:
        raise HTTPException(status_code=404, detail="Precio no encontrado")
    
    precio.activo = False
    db.commit()
    
    return {"message": f"Precio {tipo} desactivado correctamente"}
