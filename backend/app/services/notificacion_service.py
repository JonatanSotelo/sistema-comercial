from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, timedelta
import json

from app.models.notificacion_model import Notificacion
from app.schemas.notificacion_schema import (
    NotificacionCreate, 
    NotificacionUpdate, 
    NotificacionFiltros,
    NotificacionStats
)

class NotificacionService:
    @staticmethod
    def create(db: Session, notificacion: NotificacionCreate) -> Notificacion:
        """Crear una nueva notificación"""
        db_notificacion = Notificacion(**notificacion.dict())
        db.add(db_notificacion)
        db.commit()
        db.refresh(db_notificacion)
        return db_notificacion

    @staticmethod
    def get_by_id(db: Session, notificacion_id: int) -> Optional[Notificacion]:
        """Obtener notificación por ID"""
        return db.query(Notificacion).filter(Notificacion.id == notificacion_id).first()

    @staticmethod
    def get_all(db: Session, filtros: NotificacionFiltros) -> List[Notificacion]:
        """Obtener todas las notificaciones con filtros"""
        query = db.query(Notificacion)

        # Aplicar filtros
        if filtros.tipo:
            query = query.filter(Notificacion.tipo == filtros.tipo)
        
        if filtros.estado:
            query = query.filter(Notificacion.estado == filtros.estado)
        
        if filtros.es_urgente is not None:
            query = query.filter(Notificacion.es_urgente == filtros.es_urgente)
        
        if filtros.requiere_accion is not None:
            query = query.filter(Notificacion.requiere_accion == filtros.requiere_accion)
        
        if filtros.usuario_id:
            query = query.filter(Notificacion.usuario_id == filtros.usuario_id)
        
        if filtros.entidad_tipo:
            query = query.filter(Notificacion.entidad_tipo == filtros.entidad_tipo)
        
        if filtros.fecha_desde:
            query = query.filter(Notificacion.fecha_creacion >= filtros.fecha_desde)
        
        if filtros.fecha_hasta:
            query = query.filter(Notificacion.fecha_creacion <= filtros.fecha_hasta)

        # Ordenar por fecha de creación (más recientes primero)
        query = query.order_by(desc(Notificacion.fecha_creacion))

        # Paginación
        offset = (filtros.page - 1) * filtros.per_page
        return query.offset(offset).limit(filtros.per_page).all()

    @staticmethod
    def get_pendientes(db: Session, usuario_id: Optional[int] = None) -> List[Notificacion]:
        """Obtener notificaciones pendientes (no leídas)"""
        query = db.query(Notificacion).filter(Notificacion.estado != "LEIDA")
        
        if usuario_id:
            query = query.filter(Notificacion.usuario_id == usuario_id)
        
        return query.order_by(desc(Notificacion.fecha_creacion)).all()

    @staticmethod
    def get_urgentes(db: Session, usuario_id: Optional[int] = None) -> List[Notificacion]:
        """Obtener notificaciones urgentes"""
        query = db.query(Notificacion).filter(Notificacion.es_urgente == True)
        
        if usuario_id:
            query = query.filter(Notificacion.usuario_id == usuario_id)
        
        return query.order_by(desc(Notificacion.fecha_creacion)).all()

    @staticmethod
    def marcar_como_leida(db: Session, notificacion_id: int) -> Optional[Notificacion]:
        """Marcar notificación como leída"""
        notificacion = db.query(Notificacion).filter(Notificacion.id == notificacion_id).first()
        if notificacion:
            notificacion.estado = "LEIDA"
            notificacion.fecha_lectura = datetime.utcnow()
            db.commit()
            db.refresh(notificacion)
        return notificacion

    @staticmethod
    def marcar_todas_como_leidas(db: Session, usuario_id: Optional[int] = None) -> int:
        """Marcar todas las notificaciones como leídas"""
        query = db.query(Notificacion).filter(Notificacion.estado != "LEIDA")
        
        if usuario_id:
            query = query.filter(Notificacion.usuario_id == usuario_id)
        
        notificaciones = query.all()
        for notif in notificaciones:
            notif.estado = "LEIDA"
            notif.fecha_lectura = datetime.utcnow()
        
        db.commit()
        return len(notificaciones)

    @staticmethod
    def marcar_como_procesada(db: Session, notificacion_id: int) -> Optional[Notificacion]:
        """Marcar notificación como procesada"""
        notificacion = db.query(Notificacion).filter(Notificacion.id == notificacion_id).first()
        if notificacion:
            notificacion.procesada = True
            notificacion.fecha_procesamiento = datetime.utcnow()
            db.commit()
            db.refresh(notificacion)
        return notificacion

    @staticmethod
    def delete(db: Session, notificacion_id: int) -> bool:
        """Eliminar notificación"""
        notificacion = db.query(Notificacion).filter(Notificacion.id == notificacion_id).first()
        if notificacion:
            db.delete(notificacion)
            db.commit()
            return True
        return False

    @staticmethod
    def get_stats(db: Session, usuario_id: Optional[int] = None) -> NotificacionStats:
        """Obtener estadísticas de notificaciones"""
        query = db.query(Notificacion)
        
        if usuario_id:
            query = query.filter(Notificacion.usuario_id == usuario_id)
        
        # Total de notificaciones
        total = query.count()
        
        # No leídas
        no_leidas = query.filter(Notificacion.estado != "LEIDA").count()
        
        # Urgentes
        urgentes = query.filter(Notificacion.es_urgente == True).count()
        
        # Por tipo
        por_tipo = {}
        tipos = db.query(Notificacion.tipo, func.count(Notificacion.id)).group_by(Notificacion.tipo).all()
        for tipo, count in tipos:
            por_tipo[tipo] = count
        
        # Por estado
        por_estado = {}
        estados = db.query(Notificacion.estado, func.count(Notificacion.id)).group_by(Notificacion.estado).all()
        for estado, count in estados:
            por_estado[estado] = count
        
        return NotificacionStats(
            total=total,
            no_leidas=no_leidas,
            urgentes=urgentes,
            por_tipo=por_tipo,
            por_estado=por_estado
        )

    @staticmethod
    def crear_notificacion_stock_bajo(
        db: Session, 
        producto_id: int, 
        stock_actual: int, 
        stock_minimo: int,
        usuario_id: Optional[int] = None
    ) -> Notificacion:
        """Crear notificación de stock bajo"""
        diferencia = stock_minimo - stock_actual
        porcentaje = (diferencia / stock_minimo) * 100 if stock_minimo > 0 else 0
        
        es_urgente = porcentaje >= 50
        requiere_accion = porcentaje >= 25
        
        notificacion = NotificacionCreate(
            tipo="STOCK_BAJO",
            titulo=f"Stock bajo: Producto ID {producto_id}",
            mensaje=f"El producto tiene {stock_actual} unidades en stock, pero el mínimo es {stock_minimo}. Faltan {diferencia} unidades ({porcentaje:.1f}% por debajo del mínimo).",
            es_urgente=es_urgente,
            requiere_accion=requiere_accion,
            usuario_id=usuario_id,
            entidad_id=producto_id,
            entidad_tipo="producto",
            datos_adicionales=json.dumps({
                "producto_id": producto_id,
                "stock_actual": stock_actual,
                "stock_minimo": stock_minimo,
                "diferencia": diferencia,
                "porcentaje": porcentaje
            })
        )
        
        return NotificacionService.create(db, notificacion)

    @staticmethod
    def crear_notificacion_venta_nueva(
        db: Session,
        venta_id: int,
        monto: float,
        cliente_nombre: str,
        usuario_id: Optional[int] = None
    ) -> Notificacion:
        """Crear notificación de venta nueva"""
        notificacion = NotificacionCreate(
            tipo="VENTA_IMPORTANTE",
            titulo=f"Nueva venta: ${monto:,.2f}",
            mensaje=f"Se registró una nueva venta por ${monto:,.2f} al cliente {cliente_nombre}.",
            es_urgente=False,
            requiere_accion=False,
            usuario_id=usuario_id,
            entidad_id=venta_id,
            entidad_tipo="venta",
            datos_adicionales=json.dumps({
                "venta_id": venta_id,
                "monto": monto,
                "cliente_nombre": cliente_nombre
            })
        )
        
        return NotificacionService.create(db, notificacion)

    @staticmethod
    def crear_notificacion_sistema(
        db: Session,
        titulo: str,
        mensaje: str,
        es_urgente: bool = False,
        usuario_id: Optional[int] = None
    ) -> Notificacion:
        """Crear notificación del sistema"""
        notificacion = NotificacionCreate(
            tipo="SISTEMA",
            titulo=titulo,
            mensaje=mensaje,
            es_urgente=es_urgente,
            requiere_accion=False,
            usuario_id=usuario_id,
            entidad_tipo="sistema"
        )
        
        return NotificacionService.create(db, notificacion)

    @staticmethod
    def limpiar_notificaciones_antiguas(db: Session, dias: int = 30) -> int:
        """Limpiar notificaciones antiguas"""
        fecha_limite = datetime.utcnow() - timedelta(days=dias)
        notificaciones_antiguas = db.query(Notificacion).filter(
            and_(
                Notificacion.fecha_creacion < fecha_limite,
                Notificacion.estado == "LEIDA"
            )
        ).all()
        
        count = len(notificaciones_antiguas)
        for notif in notificaciones_antiguas:
            db.delete(notif)
        
        db.commit()
        return count