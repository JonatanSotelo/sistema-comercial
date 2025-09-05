# app/services/precio_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, text
from datetime import datetime, date
from typing import List, Optional, Dict, Any, Tuple
import json

from app.models.precio_model import (
    PrecioProducto, PrecioVolumen, PrecioCategoria, PrecioEstacional,
    PrecioHistorial, PrecioAplicado, TipoPrecio, EstadoPrecio
)
from app.schemas.precio_schema import (
    PrecioProductoCreate, PrecioProductoUpdate,
    PrecioVolumenCreate, PrecioVolumenUpdate,
    PrecioCategoriaCreate, PrecioCategoriaUpdate,
    PrecioEstacionalCreate, PrecioEstacionalUpdate,
    PrecioFiltros, PrecioResumen, PrecioEstadisticas,
    PrecioAplicarRequest, PrecioAplicarResponse
)

class PrecioService:
    
    # === PRECIOS DE PRODUCTO ===
    
    @staticmethod
    def crear_precio_producto(
        db: Session,
        precio: PrecioProductoCreate,
        creado_por: Optional[int] = None
    ) -> PrecioProducto:
        """Crea un nuevo precio de producto"""
        db_precio = PrecioProducto(
            producto_id=precio.producto_id,
            tipo=precio.tipo.value,
            precio_base=precio.precio_base,
            precio_especial=precio.precio_especial,
            descuento_porcentaje=precio.descuento_porcentaje,
            descuento_monto=precio.descuento_monto,
            cliente_id=precio.cliente_id,
            categoria_id=precio.categoria_id,
            cantidad_minima=precio.cantidad_minima,
            cantidad_maxima=precio.cantidad_maxima,
            fecha_inicio=precio.fecha_inicio,
            fecha_fin=precio.fecha_fin,
            nombre=precio.nombre,
            descripcion=precio.descripcion,
            prioridad=precio.prioridad,
            creado_por=creado_por
        )
        
        db.add(db_precio)
        db.commit()
        db.refresh(db_precio)
        
        # Registrar en historial
        PrecioService._registrar_historial(
            db, precio.producto_id, "creacion", None, db_precio.precio_especial,
            None, db_precio.descuento_porcentaje, db_precio.id, "precios_producto",
            creado_por, "Precio creado"
        )
        
        return db_precio
    
    @staticmethod
    def obtener_precios_producto(
        db: Session,
        filtros: Optional[PrecioFiltros] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[PrecioProducto]:
        """Obtiene precios de producto con filtros"""
        query = db.query(PrecioProducto)
        
        if filtros:
            if filtros.producto_id:
                query = query.filter(PrecioProducto.producto_id == filtros.producto_id)
            if filtros.cliente_id:
                query = query.filter(PrecioProducto.cliente_id == filtros.cliente_id)
            if filtros.categoria_id:
                query = query.filter(PrecioProducto.categoria_id == filtros.categoria_id)
            if filtros.tipo:
                query = query.filter(PrecioProducto.tipo == filtros.tipo)
            if filtros.estado:
                query = query.filter(PrecioProducto.estado == filtros.estado)
            if filtros.fecha_desde:
                query = query.filter(PrecioProducto.fecha_inicio >= filtros.fecha_desde)
            if filtros.fecha_hasta:
                query = query.filter(PrecioProducto.fecha_inicio <= filtros.fecha_hasta)
            if filtros.solo_activos:
                query = query.filter(PrecioProducto.activo == True)
            if filtros.solo_vigentes:
                now = datetime.utcnow()
                query = query.filter(
                    and_(
                        PrecioProducto.fecha_inicio <= now,
                        or_(
                            PrecioProducto.fecha_fin.is_(None),
                            PrecioProducto.fecha_fin >= now
                        )
                    )
                )
        
        return query.order_by(
            PrecioProducto.prioridad.asc(),
            desc(PrecioProducto.fecha_creacion)
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def actualizar_precio_producto(
        db: Session,
        precio_id: int,
        precio_update: PrecioProductoUpdate,
        usuario_id: Optional[int] = None
    ) -> Optional[PrecioProducto]:
        """Actualiza un precio de producto"""
        db_precio = db.query(PrecioProducto).filter(PrecioProducto.id == precio_id).first()
        
        if not db_precio:
            return None
        
        # Guardar valores anteriores para historial
        precio_anterior = db_precio.precio_especial
        descuento_anterior = db_precio.descuento_porcentaje
        
        # Actualizar campos
        for field, value in precio_update.dict(exclude_unset=True).items():
            setattr(db_precio, field, value)
        
        db_precio.fecha_actualizacion = datetime.utcnow()
        
        db.commit()
        db.refresh(db_precio)
        
        # Registrar en historial
        PrecioService._registrar_historial(
            db, db_precio.producto_id, "actualizacion", precio_anterior, db_precio.precio_especial,
            descuento_anterior, db_precio.descuento_porcentaje, db_precio.id, "precios_producto",
            usuario_id, "Precio actualizado"
        )
        
        return db_precio
    
    # === PRECIOS POR VOLUMEN ===
    
    @staticmethod
    def crear_precio_volumen(
        db: Session,
        precio: PrecioVolumenCreate,
        creado_por: Optional[int] = None
    ) -> PrecioVolumen:
        """Crea un nuevo precio por volumen"""
        db_precio = PrecioVolumen(
            producto_id=precio.producto_id,
            cantidad_minima=precio.cantidad_minima,
            cantidad_maxima=precio.cantidad_maxima,
            descuento_porcentaje=precio.descuento_porcentaje,
            descuento_monto=precio.descuento_monto,
            precio_especial=precio.precio_especial,
            cliente_id=precio.cliente_id,
            categoria_id=precio.categoria_id,
            fecha_inicio=precio.fecha_inicio,
            fecha_fin=precio.fecha_fin,
            nombre=precio.nombre,
            descripcion=precio.descripcion,
            prioridad=precio.prioridad,
            creado_por=creado_por
        )
        
        db.add(db_precio)
        db.commit()
        db.refresh(db_precio)
        
        return db_precio
    
    @staticmethod
    def obtener_precios_volumen(
        db: Session,
        filtros: Optional[PrecioFiltros] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[PrecioVolumen]:
        """Obtiene precios por volumen con filtros"""
        query = db.query(PrecioVolumen)
        
        if filtros:
            if filtros.producto_id:
                query = query.filter(PrecioVolumen.producto_id == filtros.producto_id)
            if filtros.cliente_id:
                query = query.filter(PrecioVolumen.cliente_id == filtros.cliente_id)
            if filtros.categoria_id:
                query = query.filter(PrecioVolumen.categoria_id == filtros.categoria_id)
            if filtros.fecha_desde:
                query = query.filter(PrecioVolumen.fecha_inicio >= filtros.fecha_desde)
            if filtros.fecha_hasta:
                query = query.filter(PrecioVolumen.fecha_inicio <= filtros.fecha_hasta)
            if filtros.solo_activos:
                query = query.filter(PrecioVolumen.activo == True)
            if filtros.solo_vigentes:
                now = datetime.utcnow()
                query = query.filter(
                    and_(
                        PrecioVolumen.fecha_inicio <= now,
                        or_(
                            PrecioVolumen.fecha_fin.is_(None),
                            PrecioVolumen.fecha_fin >= now
                        )
                    )
                )
        
        return query.order_by(
            PrecioVolumen.prioridad.asc(),
            PrecioVolumen.cantidad_minima.asc()
        ).offset(skip).limit(limit).all()
    
    # === PRECIOS POR CATEGORÍA ===
    
    @staticmethod
    def crear_precio_categoria(
        db: Session,
        precio: PrecioCategoriaCreate,
        creado_por: Optional[int] = None
    ) -> PrecioCategoria:
        """Crea un nuevo precio por categoría"""
        db_precio = PrecioCategoria(
            categoria_id=precio.categoria_id,
            descuento_porcentaje=precio.descuento_porcentaje,
            descuento_monto=precio.descuento_monto,
            multiplicador=precio.multiplicador,
            cliente_id=precio.cliente_id,
            producto_id=precio.producto_id,
            fecha_inicio=precio.fecha_inicio,
            fecha_fin=precio.fecha_fin,
            nombre=precio.nombre,
            descripcion=precio.descripcion,
            prioridad=precio.prioridad,
            creado_por=creado_por
        )
        
        db.add(db_precio)
        db.commit()
        db.refresh(db_precio)
        
        return db_precio
    
    @staticmethod
    def obtener_precios_categoria(
        db: Session,
        filtros: Optional[PrecioFiltros] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[PrecioCategoria]:
        """Obtiene precios por categoría con filtros"""
        query = db.query(PrecioCategoria)
        
        if filtros:
            if filtros.categoria_id:
                query = query.filter(PrecioCategoria.categoria_id == filtros.categoria_id)
            if filtros.cliente_id:
                query = query.filter(PrecioCategoria.cliente_id == filtros.cliente_id)
            if filtros.producto_id:
                query = query.filter(PrecioCategoria.producto_id == filtros.producto_id)
            if filtros.fecha_desde:
                query = query.filter(PrecioCategoria.fecha_inicio >= filtros.fecha_desde)
            if filtros.fecha_hasta:
                query = query.filter(PrecioCategoria.fecha_inicio <= filtros.fecha_hasta)
            if filtros.solo_activos:
                query = query.filter(PrecioCategoria.activo == True)
            if filtros.solo_vigentes:
                now = datetime.utcnow()
                query = query.filter(
                    and_(
                        PrecioCategoria.fecha_inicio <= now,
                        or_(
                            PrecioCategoria.fecha_fin.is_(None),
                            PrecioCategoria.fecha_fin >= now
                        )
                    )
                )
        
        return query.order_by(
            PrecioCategoria.prioridad.asc(),
            desc(PrecioCategoria.fecha_creacion)
        ).offset(skip).limit(limit).all()
    
    # === PRECIOS ESTACIONALES ===
    
    @staticmethod
    def crear_precio_estacional(
        db: Session,
        precio: PrecioEstacionalCreate,
        creado_por: Optional[int] = None
    ) -> PrecioEstacional:
        """Crea un nuevo precio estacional"""
        db_precio = PrecioEstacional(
            producto_id=precio.producto_id,
            nombre_temporada=precio.nombre_temporada,
            descuento_porcentaje=precio.descuento_porcentaje,
            descuento_monto=precio.descuento_monto,
            precio_especial=precio.precio_especial,
            cliente_id=precio.cliente_id,
            categoria_id=precio.categoria_id,
            fecha_inicio=precio.fecha_inicio,
            fecha_fin=precio.fecha_fin,
            descripcion=precio.descripcion,
            prioridad=precio.prioridad,
            creado_por=creado_por
        )
        
        db.add(db_precio)
        db.commit()
        db.refresh(db_precio)
        
        return db_precio
    
    @staticmethod
    def obtener_precios_estacionales(
        db: Session,
        filtros: Optional[PrecioFiltros] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[PrecioEstacional]:
        """Obtiene precios estacionales con filtros"""
        query = db.query(PrecioEstacional)
        
        if filtros:
            if filtros.producto_id:
                query = query.filter(PrecioEstacional.producto_id == filtros.producto_id)
            if filtros.cliente_id:
                query = query.filter(PrecioEstacional.cliente_id == filtros.cliente_id)
            if filtros.categoria_id:
                query = query.filter(PrecioEstacional.categoria_id == filtros.categoria_id)
            if filtros.fecha_desde:
                query = query.filter(PrecioEstacional.fecha_inicio >= filtros.fecha_desde)
            if filtros.fecha_hasta:
                query = query.filter(PrecioEstacional.fecha_inicio <= filtros.fecha_hasta)
            if filtros.solo_activos:
                query = query.filter(PrecioEstacional.activo == True)
            if filtros.solo_vigentes:
                today = date.today()
                query = query.filter(
                    and_(
                        PrecioEstacional.fecha_inicio <= today,
                        PrecioEstacional.fecha_fin >= today
                    )
                )
        
        return query.order_by(
            PrecioEstacional.prioridad.asc(),
            PrecioEstacional.fecha_inicio.asc()
        ).offset(skip).limit(limit).all()
    
    # === APLICACIÓN DE PRECIOS ===
    
    @staticmethod
    def aplicar_precio_dinamico(
        db: Session,
        request: PrecioAplicarRequest
    ) -> PrecioAplicarResponse:
        """Aplica el mejor precio dinámico para un producto"""
        now = datetime.utcnow()
        today = date.today()
        
        # Obtener precio base
        precio_base = request.precio_base
        precio_final = precio_base
        descuento_aplicado = 0.0
        porcentaje_descuento = 0.0
        tipo_precio = "base"
        precio_id = None
        mensaje = "Precio base aplicado"
        
        # 1. Verificar precios por cliente (mayor prioridad)
        if request.cliente_id:
            precio_cliente = db.query(PrecioProducto).filter(
                and_(
                    PrecioProducto.producto_id == request.producto_id,
                    PrecioProducto.cliente_id == request.cliente_id,
                    PrecioProducto.tipo == TipoPrecio.CLIENTE,
                    PrecioProducto.activo == True,
                    PrecioProducto.fecha_inicio <= now,
                    or_(
                        PrecioProducto.fecha_fin.is_(None),
                        PrecioProducto.fecha_fin >= now
                    )
                )
            ).order_by(PrecioProducto.prioridad.asc()).first()
            
            if precio_cliente:
                precio_final, descuento_aplicado, porcentaje_descuento = PrecioService._calcular_precio_final(
                    precio_base, precio_cliente.precio_especial, precio_cliente.descuento_porcentaje,
                    precio_cliente.descuento_monto
                )
                tipo_precio = "cliente"
                precio_id = precio_cliente.id
                mensaje = f"Precio especial por cliente aplicado (ID: {precio_cliente.id})"
        
        # 2. Verificar precios por volumen
        if precio_final == precio_base:  # Solo si no se aplicó precio por cliente
            precio_volumen = db.query(PrecioVolumen).filter(
                and_(
                    PrecioVolumen.producto_id == request.producto_id,
                    PrecioVolumen.cantidad_minima <= request.cantidad,
                    or_(
                        PrecioVolumen.cantidad_maxima.is_(None),
                        PrecioVolumen.cantidad_maxima >= request.cantidad
                    ),
                    PrecioVolumen.activo == True,
                    PrecioVolumen.fecha_inicio <= now,
                    or_(
                        PrecioVolumen.fecha_fin.is_(None),
                        PrecioVolumen.fecha_fin >= now
                    )
                )
            ).order_by(PrecioVolumen.prioridad.asc(), PrecioVolumen.cantidad_minima.desc()).first()
            
            if precio_volumen:
                precio_final, descuento_aplicado, porcentaje_descuento = PrecioService._calcular_precio_final(
                    precio_base, precio_volumen.precio_especial, precio_volumen.descuento_porcentaje,
                    precio_volumen.descuento_monto
                )
                tipo_precio = "volumen"
                precio_id = precio_volumen.id
                mensaje = f"Precio por volumen aplicado (ID: {precio_volumen.id})"
        
        # 3. Verificar precios estacionales
        if precio_final == precio_base:  # Solo si no se aplicó precio anterior
            precio_estacional = db.query(PrecioEstacional).filter(
                and_(
                    PrecioEstacional.producto_id == request.producto_id,
                    PrecioEstacional.fecha_inicio <= today,
                    PrecioEstacional.fecha_fin >= today,
                    PrecioEstacional.activo == True
                )
            ).order_by(PrecioEstacional.prioridad.asc()).first()
            
            if precio_estacional:
                precio_final, descuento_aplicado, porcentaje_descuento = PrecioService._calcular_precio_final(
                    precio_base, precio_estacional.precio_especial, precio_estacional.descuento_porcentaje,
                    precio_estacional.descuento_monto
                )
                tipo_precio = "estacional"
                precio_id = precio_estacional.id
                mensaje = f"Precio estacional aplicado (ID: {precio_estacional.id})"
        
        # 4. Registrar precio aplicado
        if precio_final != precio_base:
            precio_aplicado = PrecioAplicado(
                venta_id=request.venta_id,
                producto_id=request.producto_id,
                cliente_id=request.cliente_id,
                precio_base=precio_base,
                precio_final=precio_final,
                descuento_aplicado=descuento_aplicado,
                porcentaje_descuento=porcentaje_descuento,
                tipo_precio=tipo_precio,
                precio_id=precio_id,
                precio_tabla=f"precios_{tipo_precio}",
                cantidad=request.cantidad,
                subtotal=precio_final * request.cantidad
            )
            
            db.add(precio_aplicado)
            db.commit()
        
        return PrecioAplicarResponse(
            aplicado=precio_final != precio_base,
            precio_base=precio_base,
            precio_final=precio_final,
            descuento_aplicado=descuento_aplicado if precio_final != precio_base else None,
            porcentaje_descuento=porcentaje_descuento if precio_final != precio_base else None,
            tipo_precio=tipo_precio if precio_final != precio_base else None,
            precio_id=precio_id if precio_final != precio_base else None,
            mensaje=mensaje
        )
    
    @staticmethod
    def _calcular_precio_final(
        precio_base: float,
        precio_especial: Optional[float],
        descuento_porcentaje: Optional[float],
        descuento_monto: Optional[float]
    ) -> Tuple[float, float, float]:
        """Calcula el precio final basado en las reglas de descuento"""
        if precio_especial is not None:
            descuento_aplicado = precio_base - precio_especial
            porcentaje_descuento = (descuento_aplicado / precio_base) * 100
            return precio_especial, descuento_aplicado, porcentaje_descuento
        
        elif descuento_porcentaje is not None:
            descuento_aplicado = precio_base * (descuento_porcentaje / 100)
            precio_final = precio_base - descuento_aplicado
            return precio_final, descuento_aplicado, descuento_porcentaje
        
        elif descuento_monto is not None:
            descuento_aplicado = min(descuento_monto, precio_base)
            precio_final = precio_base - descuento_aplicado
            porcentaje_descuento = (descuento_aplicado / precio_base) * 100
            return precio_final, descuento_aplicado, porcentaje_descuento
        
        return precio_base, 0.0, 0.0
    
    # === HISTORIAL ===
    
    @staticmethod
    def _registrar_historial(
        db: Session,
        producto_id: int,
        tipo_cambio: str,
        precio_anterior: Optional[float],
        precio_nuevo: Optional[float],
        descuento_anterior: Optional[float],
        descuento_nuevo: Optional[float],
        precio_id: Optional[int],
        precio_tabla: Optional[str],
        usuario_id: Optional[int],
        motivo: Optional[str]
    ):
        """Registra un cambio en el historial de precios"""
        historial = PrecioHistorial(
            producto_id=producto_id,
            tipo_cambio=tipo_cambio,
            precio_anterior=precio_anterior,
            precio_nuevo=precio_nuevo,
            descuento_anterior=descuento_anterior,
            descuento_nuevo=descuento_nuevo,
            precio_id=precio_id,
            precio_tabla=precio_tabla,
            motivo=motivo,
            usuario_id=usuario_id
        )
        
        db.add(historial)
        db.commit()
    
    @staticmethod
    def obtener_historial_precios(
        db: Session,
        producto_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[PrecioHistorial]:
        """Obtiene el historial de precios"""
        query = db.query(PrecioHistorial)
        
        if producto_id:
            query = query.filter(PrecioHistorial.producto_id == producto_id)
        
        return query.order_by(desc(PrecioHistorial.fecha_cambio)).offset(skip).limit(limit).all()
    
    # === RESUMEN Y ESTADÍSTICAS ===
    
    @staticmethod
    def obtener_resumen_precios(db: Session) -> PrecioResumen:
        """Obtiene resumen de precios"""
        # Contar precios por tipo
        total_precios = db.query(PrecioProducto).count()
        precios_activos = db.query(PrecioProducto).filter(PrecioProducto.activo == True).count()
        
        # Contar por tipo
        precios_por_tipo = {}
        for tipo in TipoPrecio:
            count = db.query(PrecioProducto).filter(PrecioProducto.tipo == tipo).count()
            precios_por_tipo[tipo.value] = count
        
        # Contar precios por cliente
        precios_por_cliente = db.query(PrecioProducto).filter(
            PrecioProducto.cliente_id.isnot(None)
        ).count()
        
        # Contar precios por volumen
        precios_por_volumen = db.query(PrecioVolumen).count()
        
        # Contar precios estacionales
        precios_estacionales = db.query(PrecioEstacional).count()
        
        # Calcular descuento promedio
        descuento_promedio = db.query(func.avg(PrecioProducto.descuento_porcentaje)).filter(
            PrecioProducto.descuento_porcentaje.isnot(None)
        ).scalar() or 0.0
        
        return PrecioResumen(
            total_precios=total_precios,
            precios_activos=precios_activos,
            precios_por_tipo=precios_por_tipo,
            precios_por_cliente=precios_por_cliente,
            precios_por_volumen=precios_por_volumen,
            precios_estacionales=precios_estacionales,
            descuento_promedio=descuento_promedio,
            ahorro_total=0.0  # Se calcularía con datos reales
        )
    
    @staticmethod
    def obtener_estadisticas_precios(db: Session) -> PrecioEstadisticas:
        """Obtiene estadísticas detalladas de precios"""
        resumen = PrecioService.obtener_resumen_precios(db)
        
        # Estadísticas por estado
        precios_por_estado = {}
        for estado in EstadoPrecio:
            count = db.query(PrecioProducto).filter(PrecioProducto.estado == estado).count()
            precios_por_estado[estado.value] = count
        
        # Descuento promedio por tipo
        descuento_promedio_por_tipo = {}
        for tipo in TipoPrecio:
            avg = db.query(func.avg(PrecioProducto.descuento_porcentaje)).filter(
                and_(
                    PrecioProducto.tipo == tipo,
                    PrecioProducto.descuento_porcentaje.isnot(None)
                )
            ).scalar() or 0.0
            descuento_promedio_por_tipo[tipo.value] = avg
        
        return PrecioEstadisticas(
            total_precios=resumen.total_precios,
            precios_por_tipo=resumen.precios_por_tipo,
            precios_por_estado=precios_por_estado,
            descuento_promedio_por_tipo=descuento_promedio_por_tipo,
            productos_mas_descontados=[],  # Se implementaría con consultas más complejas
            clientes_mas_descontados=[],  # Se implementaría con consultas más complejas
            tendencia_precios=[],  # Se implementaría con análisis temporal
            ahorro_total_mes=0.0,  # Se calcularía con datos reales
            ahorro_promedio_por_venta=0.0  # Se calcularía con datos reales
        )
