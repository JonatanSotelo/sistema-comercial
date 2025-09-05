# app/services/inventario_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, text
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
import json

from app.models.inventario_model import (
    ConfiguracionInventario, AlertaInventario, MovimientoInventario, 
    ReordenAutomatico, TipoAlertaInventario, EstadoAlerta
)
from app.schemas.inventario_schema import (
    ConfiguracionInventarioCreate, ConfiguracionInventarioUpdate,
    AlertaInventarioCreate, AlertaInventarioUpdate,
    MovimientoInventarioCreate, ReordenAutomaticoCreate,
    InventarioResumen, InventarioFiltros, InventarioEstadisticas
)

class InventarioService:
    
    @staticmethod
    def crear_configuracion(
        db: Session, 
        configuracion: ConfiguracionInventarioCreate
    ) -> ConfiguracionInventario:
        """Crea una nueva configuración de inventario"""
        db_configuracion = ConfiguracionInventario(
            producto_id=configuracion.producto_id,
            stock_minimo=configuracion.stock_minimo,
            stock_maximo=configuracion.stock_maximo,
            punto_reorden=configuracion.punto_reorden,
            cantidad_reorden=configuracion.cantidad_reorden,
            alerta_stock_bajo=configuracion.alerta_stock_bajo,
            alerta_stock_critico=configuracion.alerta_stock_critico,
            alerta_vencimiento=configuracion.alerta_vencimiento,
            dias_vencimiento_alerta=configuracion.dias_vencimiento_alerta,
            alerta_movimiento_grande=configuracion.alerta_movimiento_grande,
            umbral_movimiento_grande=configuracion.umbral_movimiento_grande
        )
        
        db.add(db_configuracion)
        db.commit()
        db.refresh(db_configuracion)
        
        return db_configuracion
    
    @staticmethod
    def obtener_configuraciones(
        db: Session,
        filtros: Optional[InventarioFiltros] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ConfiguracionInventario]:
        """Obtiene configuraciones de inventario con filtros"""
        query = db.query(ConfiguracionInventario)
        
        if filtros:
            if filtros.producto_id:
                query = query.filter(ConfiguracionInventario.producto_id == filtros.producto_id)
            if filtros.solo_activos:
                query = query.filter(ConfiguracionInventario.activo == True)
        
        return query.order_by(desc(ConfiguracionInventario.fecha_creacion)).offset(skip).limit(limit).all()
    
    @staticmethod
    def actualizar_configuracion(
        db: Session,
        configuracion_id: int,
        configuracion_update: ConfiguracionInventarioUpdate
    ) -> Optional[ConfiguracionInventario]:
        """Actualiza una configuración de inventario"""
        db_configuracion = db.query(ConfiguracionInventario).filter(
            ConfiguracionInventario.id == configuracion_id
        ).first()
        
        if not db_configuracion:
            return None
        
        for field, value in configuracion_update.dict(exclude_unset=True).items():
            setattr(db_configuracion, field, value)
        
        db_configuracion.fecha_actualizacion = datetime.utcnow()
        
        db.commit()
        db.refresh(db_configuracion)
        
        return db_configuracion
    
    @staticmethod
    def crear_movimiento(
        db: Session,
        movimiento: MovimientoInventarioCreate,
        usuario_id: Optional[int] = None
    ) -> MovimientoInventario:
        """Crea un movimiento de inventario"""
        # Obtener stock actual del producto
        from app.models.producto_model import Producto
        producto = db.query(Producto).filter(Producto.id == movimiento.producto_id).first()
        
        if not producto:
            raise ValueError("Producto no encontrado")
        
        cantidad_anterior = producto.stock or 0.0
        cantidad_nueva = cantidad_anterior + movimiento.cantidad
        
        # Crear movimiento
        db_movimiento = MovimientoInventario(
            producto_id=movimiento.producto_id,
            tipo_movimiento=movimiento.tipo_movimiento,
            cantidad=movimiento.cantidad,
            cantidad_anterior=cantidad_anterior,
            cantidad_nueva=cantidad_nueva,
            referencia_tipo=movimiento.referencia_tipo,
            referencia_id=movimiento.referencia_id,
            motivo=movimiento.motivo,
            costo_unitario=movimiento.costo_unitario,
            costo_total=movimiento.costo_total,
            usuario_id=usuario_id
        )
        
        db.add(db_movimiento)
        
        # Actualizar stock del producto
        producto.stock = cantidad_nueva
        
        db.commit()
        db.refresh(db_movimiento)
        
        # Verificar si se debe crear una alerta
        InventarioService._verificar_alertas_stock(db, movimiento.producto_id, cantidad_nueva)
        
        return db_movimiento
    
    @staticmethod
    def _verificar_alertas_stock(db: Session, producto_id: int, stock_actual: float):
        """Verifica si se deben crear alertas de stock"""
        configuracion = db.query(ConfiguracionInventario).filter(
            and_(
                ConfiguracionInventario.producto_id == producto_id,
                ConfiguracionInventario.activo == True
            )
        ).first()
        
        if not configuracion:
            return
        
        # Verificar stock bajo
        if configuracion.alerta_stock_bajo and stock_actual <= configuracion.stock_minimo:
            InventarioService._crear_alerta_stock_bajo(
                db, producto_id, stock_actual, configuracion.stock_minimo
            )
        
        # Verificar stock crítico (50% del mínimo)
        stock_critico = configuracion.stock_minimo * 0.5
        if configuracion.alerta_stock_critico and stock_actual <= stock_critico:
            InventarioService._crear_alerta_stock_critico(
                db, producto_id, stock_actual, stock_critico
            )
        
        # Verificar stock agotado
        if stock_actual <= 0:
            InventarioService._crear_alerta_stock_agotado(db, producto_id)
    
    @staticmethod
    def _crear_alerta_stock_bajo(
        db: Session, 
        producto_id: int, 
        stock_actual: float, 
        stock_minimo: float
    ):
        """Crea alerta de stock bajo"""
        # Verificar si ya existe una alerta pendiente
        alerta_existente = db.query(AlertaInventario).filter(
            and_(
                AlertaInventario.producto_id == producto_id,
                AlertaInventario.tipo == TipoAlertaInventario.STOCK_BAJO,
                AlertaInventario.estado == EstadoAlerta.PENDIENTE
            )
        ).first()
        
        if alerta_existente:
            return
        
        alerta = AlertaInventario(
            producto_id=producto_id,
            tipo=TipoAlertaInventario.STOCK_BAJO,
            titulo=f"Stock bajo - Producto {producto_id}",
            mensaje=f"El producto tiene stock bajo. Actual: {stock_actual}, Mínimo: {stock_minimo}",
            prioridad=2,
            stock_actual=stock_actual,
            stock_minimo=stock_minimo
        )
        
        db.add(alerta)
        db.commit()
    
    @staticmethod
    def _crear_alerta_stock_critico(
        db: Session, 
        producto_id: int, 
        stock_actual: float, 
        stock_critico: float
    ):
        """Crea alerta de stock crítico"""
        alerta_existente = db.query(AlertaInventario).filter(
            and_(
                AlertaInventario.producto_id == producto_id,
                AlertaInventario.tipo == TipoAlertaInventario.STOCK_CRITICO,
                AlertaInventario.estado == EstadoAlerta.PENDIENTE
            )
        ).first()
        
        if alerta_existente:
            return
        
        alerta = AlertaInventario(
            producto_id=producto_id,
            tipo=TipoAlertaInventario.STOCK_CRITICO,
            titulo=f"Stock crítico - Producto {producto_id}",
            mensaje=f"El producto tiene stock crítico. Actual: {stock_actual}, Crítico: {stock_critico}",
            prioridad=1,
            stock_actual=stock_actual,
            stock_critico=stock_critico
        )
        
        db.add(alerta)
        db.commit()
    
    @staticmethod
    def _crear_alerta_stock_agotado(db: Session, producto_id: int):
        """Crea alerta de stock agotado"""
        alerta_existente = db.query(AlertaInventario).filter(
            and_(
                AlertaInventario.producto_id == producto_id,
                AlertaInventario.tipo == TipoAlertaInventario.STOCK_AGOTADO,
                AlertaInventario.estado == EstadoAlerta.PENDIENTE
            )
        ).first()
        
        if alerta_existente:
            return
        
        alerta = AlertaInventario(
            producto_id=producto_id,
            tipo=TipoAlertaInventario.STOCK_AGOTADO,
            titulo=f"Stock agotado - Producto {producto_id}",
            mensaje="El producto se ha agotado completamente",
            prioridad=1,
            stock_actual=0.0
        )
        
        db.add(alerta)
        db.commit()
    
    @staticmethod
    def obtener_alertas(
        db: Session,
        filtros: Optional[InventarioFiltros] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AlertaInventario]:
        """Obtiene alertas de inventario con filtros"""
        query = db.query(AlertaInventario)
        
        if filtros:
            if filtros.producto_id:
                query = query.filter(AlertaInventario.producto_id == filtros.producto_id)
            if filtros.tipo_alerta:
                query = query.filter(AlertaInventario.tipo == filtros.tipo_alerta)
            if filtros.estado_alerta:
                query = query.filter(AlertaInventario.estado == filtros.estado_alerta)
            if filtros.prioridad:
                query = query.filter(AlertaInventario.prioridad == filtros.prioridad)
            if filtros.fecha_desde:
                query = query.filter(AlertaInventario.fecha_creacion >= filtros.fecha_desde)
            if filtros.fecha_hasta:
                query = query.filter(AlertaInventario.fecha_creacion <= filtros.fecha_hasta)
        
        return query.order_by(
            AlertaInventario.prioridad.asc(),
            desc(AlertaInventario.fecha_creacion)
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def resolver_alerta(
        db: Session,
        alerta_id: int,
        resolutor_id: int,
        notas: Optional[str] = None
    ) -> Optional[AlertaInventario]:
        """Resuelve una alerta de inventario"""
        alerta = db.query(AlertaInventario).filter(AlertaInventario.id == alerta_id).first()
        
        if not alerta:
            return None
        
        alerta.estado = EstadoAlerta.RESUELTA
        alerta.fecha_resolucion = datetime.utcnow()
        alerta.resuelta_por = resolutor_id
        alerta.notas_resolucion = notas
        
        db.commit()
        db.refresh(alerta)
        
        return alerta
    
    @staticmethod
    def obtener_resumen(db: Session) -> InventarioResumen:
        """Obtiene resumen del inventario"""
        # Contar productos
        from app.models.producto_model import Producto
        total_productos = db.query(Producto).count()
        
        # Contar configuraciones activas
        configuraciones_activas = db.query(ConfiguracionInventario).filter(
            ConfiguracionInventario.activo == True
        ).count()
        
        # Contar alertas
        alertas_pendientes = db.query(AlertaInventario).filter(
            AlertaInventario.estado == EstadoAlerta.PENDIENTE
        ).count()
        
        alertas_urgentes = db.query(AlertaInventario).filter(
            and_(
                AlertaInventario.estado == EstadoAlerta.PENDIENTE,
                AlertaInventario.prioridad == 1
            )
        ).count()
        
        # Contar productos con stock bajo (simulado)
        productos_stock_bajo = 0
        productos_stock_critico = 0
        productos_agotados = 0
        
        # Contar movimientos de hoy
        hoy = datetime.utcnow().date()
        movimientos_hoy = db.query(MovimientoInventario).filter(
            func.date(MovimientoInventario.fecha_movimiento) == hoy
        ).count()
        
        # Contar reordenes pendientes
        reordenes_pendientes = db.query(ReordenAutomatico).filter(
            ReordenAutomatico.estado == "pendiente"
        ).count()
        
        return InventarioResumen(
            total_productos=total_productos,
            productos_stock_bajo=productos_stock_bajo,
            productos_stock_critico=productos_stock_critico,
            productos_agotados=productos_agotados,
            alertas_pendientes=alertas_pendientes,
            alertas_urgentes=alertas_urgentes,
            valor_total_inventario=0.0,  # Se calcularía con precios
            movimientos_hoy=movimientos_hoy,
            reordenes_pendientes=reordenes_pendientes
        )
    
    @staticmethod
    def generar_reorden_automatico(
        db: Session,
        producto_id: int
    ) -> Optional[ReordenAutomatico]:
        """Genera un reorden automático para un producto"""
        configuracion = db.query(ConfiguracionInventario).filter(
            and_(
                ConfiguracionInventario.producto_id == producto_id,
                ConfiguracionInventario.activo == True
            )
        ).first()
        
        if not configuracion or not configuracion.punto_reorden:
            return None
        
        # Obtener stock actual
        from app.models.producto_model import Producto
        producto = db.query(Producto).filter(Producto.id == producto_id).first()
        
        if not producto or (producto.stock or 0) > configuracion.punto_reorden:
            return None
        
        # Verificar si ya existe un reorden pendiente
        reorden_existente = db.query(ReordenAutomatico).filter(
            and_(
                ReordenAutomatico.producto_id == producto_id,
                ReordenAutomatico.estado == "pendiente"
            )
        ).first()
        
        if reorden_existente:
            return reorden_existente
        
        # Crear reorden automático
        reorden = ReordenAutomatico(
            producto_id=producto_id,
            cantidad_sugerida=configuracion.cantidad_reorden or configuracion.stock_minimo * 2,
            fecha_sugerida=datetime.utcnow() + timedelta(days=7),
            notas="Reorden automático generado por sistema"
        )
        
        db.add(reorden)
        db.commit()
        db.refresh(reorden)
        
        return reorden
    
    @staticmethod
    def procesar_alertas_pendientes(db: Session) -> int:
        """Procesa todas las alertas pendientes del sistema"""
        alertas_procesadas = 0
        
        # Obtener configuraciones activas
        configuraciones = db.query(ConfiguracionInventario).filter(
            ConfiguracionInventario.activo == True
        ).all()
        
        for config in configuraciones:
            # Obtener stock actual del producto
            from app.models.producto_model import Producto
            producto = db.query(Producto).filter(Producto.id == config.producto_id).first()
            
            if producto:
                stock_actual = producto.stock or 0.0
                InventarioService._verificar_alertas_stock(db, config.producto_id, stock_actual)
                alertas_procesadas += 1
        
        return alertas_procesadas
