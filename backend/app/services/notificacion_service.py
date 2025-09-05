# app/services/notificacion_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import json

from app.models.notificacion_model import Notificacion, NotificacionUsuario, TipoNotificacion, EstadoNotificacion
from app.schemas.notificacion_schema import (
    NotificacionCreate, NotificacionUpdate, NotificacionResumen, 
    NotificacionFiltros, NotificacionStats, NotificacionTemplate
)

class NotificacionService:
    
    @staticmethod
    def crear_notificacion(db: Session, notificacion: NotificacionCreate) -> Notificacion:
        """Crea una nueva notificación"""
        # Convertir datos_adicionales a JSON string si existe
        datos_json = None
        if notificacion.datos_adicionales:
            datos_json = json.dumps(notificacion.datos_adicionales)
        
        db_notificacion = Notificacion(
            titulo=notificacion.titulo,
            mensaje=notificacion.mensaje,
            tipo=notificacion.tipo,
            es_urgente=notificacion.es_urgente,
            requiere_accion=notificacion.requiere_accion,
            usuario_id=notificacion.usuario_id,
            entidad_tipo=notificacion.entidad_tipo,
            entidad_id=notificacion.entidad_id,
            datos_adicionales=datos_json,
            estado=EstadoNotificacion.PENDIENTE
        )
        
        db.add(db_notificacion)
        db.commit()
        db.refresh(db_notificacion)
        
        return db_notificacion
    
    @staticmethod
    def obtener_notificaciones(
        db: Session, 
        usuario_id: Optional[int] = None,
        filtros: Optional[NotificacionFiltros] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Notificacion]:
        """Obtiene notificaciones con filtros"""
        query = db.query(Notificacion)
        
        # Filtrar por usuario (notificaciones globales + del usuario)
        if usuario_id:
            query = query.filter(
                or_(
                    Notificacion.usuario_id == usuario_id,
                    Notificacion.usuario_id.is_(None)  # Notificaciones globales
                )
            )
        
        # Aplicar filtros adicionales
        if filtros:
            if filtros.tipo:
                query = query.filter(Notificacion.tipo == filtros.tipo)
            if filtros.estado:
                query = query.filter(Notificacion.estado == filtros.estado)
            if filtros.es_urgente is not None:
                query = query.filter(Notificacion.es_urgente == filtros.es_urgente)
            if filtros.fecha_desde:
                query = query.filter(Notificacion.fecha_creacion >= filtros.fecha_desde)
            if filtros.fecha_hasta:
                query = query.filter(Notificacion.fecha_creacion <= filtros.fecha_hasta)
        
        return query.order_by(desc(Notificacion.fecha_creacion)).offset(skip).limit(limit).all()
    
    @staticmethod
    def obtener_notificacion(db: Session, notificacion_id: int) -> Optional[Notificacion]:
        """Obtiene una notificación por ID"""
        return db.query(Notificacion).filter(Notificacion.id == notificacion_id).first()
    
    @staticmethod
    def actualizar_notificacion(
        db: Session, 
        notificacion_id: int, 
        notificacion_update: NotificacionUpdate
    ) -> Optional[Notificacion]:
        """Actualiza una notificación"""
        db_notificacion = db.query(Notificacion).filter(Notificacion.id == notificacion_id).first()
        
        if not db_notificacion:
            return None
        
        if notificacion_update.estado:
            db_notificacion.estado = notificacion_update.estado
            
            # Si se marca como enviada, actualizar fecha_envio
            if notificacion_update.estado == EstadoNotificacion.ENVIADA:
                db_notificacion.fecha_envio = datetime.utcnow()
            
            # Si se marca como leída, actualizar fecha_lectura
            if notificacion_update.estado == EstadoNotificacion.LEIDA:
                db_notificacion.fecha_lectura = notificacion_update.fecha_lectura or datetime.utcnow()
        
        if notificacion_update.fecha_lectura:
            db_notificacion.fecha_lectura = notificacion_update.fecha_lectura
        
        db.commit()
        db.refresh(db_notificacion)
        
        return db_notificacion
    
    @staticmethod
    def marcar_como_leida(db: Session, notificacion_id: int, usuario_id: Optional[int] = None) -> bool:
        """Marca una notificación como leída"""
        db_notificacion = db.query(Notificacion).filter(Notificacion.id == notificacion_id).first()
        
        if not db_notificacion:
            return False
        
        # Verificar que el usuario tenga acceso a la notificación
        if usuario_id and db_notificacion.usuario_id and db_notificacion.usuario_id != usuario_id:
            return False
        
        db_notificacion.estado = EstadoNotificacion.LEIDA
        db_notificacion.fecha_lectura = datetime.utcnow()
        
        db.commit()
        return True
    
    @staticmethod
    def obtener_resumen(db: Session, usuario_id: Optional[int] = None) -> NotificacionResumen:
        """Obtiene resumen de notificaciones"""
        query = db.query(Notificacion)
        
        # Filtrar por usuario
        if usuario_id:
            query = query.filter(
                or_(
                    Notificacion.usuario_id == usuario_id,
                    Notificacion.usuario_id.is_(None)
                )
            )
        
        # Contar totales
        total = query.count()
        pendientes = query.filter(Notificacion.estado == EstadoNotificacion.PENDIENTE).count()
        leidas = query.filter(Notificacion.estado == EstadoNotificacion.LEIDA).count()
        urgentes = query.filter(Notificacion.es_urgente == True).count()
        
        # Contar por tipo
        por_tipo = {}
        for tipo in TipoNotificacion:
            count = query.filter(Notificacion.tipo == tipo).count()
            por_tipo[tipo.value] = count
        
        return NotificacionResumen(
            total=total,
            pendientes=pendientes,
            leidas=leidas,
            urgentes=urgentes,
            por_tipo=por_tipo
        )
    
    @staticmethod
    def obtener_estadisticas(db: Session, usuario_id: Optional[int] = None) -> NotificacionStats:
        """Obtiene estadísticas detalladas de notificaciones"""
        query = db.query(Notificacion)
        
        # Filtrar por usuario
        if usuario_id:
            query = query.filter(
                or_(
                    Notificacion.usuario_id == usuario_id,
                    Notificacion.usuario_id.is_(None)
                )
            )
        
        # Estadísticas básicas
        total_notificaciones = query.count()
        
        # Notificaciones por período
        hoy = datetime.utcnow().date()
        semana_pasada = hoy - timedelta(days=7)
        mes_pasado = hoy - timedelta(days=30)
        
        notificaciones_hoy = query.filter(func.date(Notificacion.fecha_creacion) == hoy).count()
        notificaciones_semana = query.filter(Notificacion.fecha_creacion >= semana_pasada).count()
        notificaciones_mes = query.filter(Notificacion.fecha_creacion >= mes_pasado).count()
        
        # Tasa de lectura
        leidas = query.filter(Notificacion.estado == EstadoNotificacion.LEIDA).count()
        tasa_lectura = (leidas / total_notificaciones * 100) if total_notificaciones > 0 else 0.0
        
        # Por tipo
        notificaciones_por_tipo = {}
        for tipo in TipoNotificacion:
            count = query.filter(Notificacion.tipo == tipo).count()
            notificaciones_por_tipo[tipo.value] = count
        
        # Urgentes y pendientes
        notificaciones_urgentes = query.filter(Notificacion.es_urgente == True).count()
        notificaciones_pendientes = query.filter(Notificacion.estado == EstadoNotificacion.PENDIENTE).count()
        
        return NotificacionStats(
            total_notificaciones=total_notificaciones,
            notificaciones_hoy=notificaciones_hoy,
            notificaciones_semana=notificaciones_semana,
            notificaciones_mes=notificaciones_mes,
            tasa_lectura=round(tasa_lectura, 2),
            notificaciones_por_tipo=notificaciones_por_tipo,
            notificaciones_urgentes=notificaciones_urgentes,
            notificaciones_pendientes=notificaciones_pendientes
        )
    
    @staticmethod
    def crear_notificacion_stock_bajo(
        db: Session, 
        producto_id: int, 
        producto_nombre: str, 
        stock_actual: float, 
        stock_minimo: float
    ) -> Notificacion:
        """Crea notificación automática de stock bajo"""
        notificacion = NotificacionCreate(
            titulo=f"Stock bajo: {producto_nombre}",
            mensaje=f"El producto '{producto_nombre}' tiene stock bajo. Actual: {stock_actual}, Mínimo: {stock_minimo}",
            tipo=TipoNotificacion.STOCK_BAJO,
            es_urgente=True,
            requiere_accion=True,
            entidad_tipo="producto",
            entidad_id=producto_id,
            datos_adicionales={
                "producto_id": producto_id,
                "producto_nombre": producto_nombre,
                "stock_actual": stock_actual,
                "stock_minimo": stock_minimo,
                "diferencia": stock_actual - stock_minimo
            }
        )
        
        return NotificacionService.crear_notificacion(db, notificacion)
    
    @staticmethod
    def crear_notificacion_venta_importante(
        db: Session, 
        venta_id: int, 
        monto: float, 
        cliente_nombre: Optional[str] = None
    ) -> Notificacion:
        """Crea notificación automática de venta importante"""
        titulo = f"Venta importante: ${monto:,.2f}"
        mensaje = f"Se realizó una venta importante por ${monto:,.2f}"
        
        if cliente_nombre:
            mensaje += f" al cliente {cliente_nombre}"
        
        notificacion = NotificacionCreate(
            titulo=titulo,
            mensaje=mensaje,
            tipo=TipoNotificacion.VENTA_IMPORTANTE,
            es_urgente=monto > 10000,  # Urgente si es mayor a $10,000
            requiere_accion=False,
            entidad_tipo="venta",
            entidad_id=venta_id,
            datos_adicionales={
                "venta_id": venta_id,
                "monto": monto,
                "cliente_nombre": cliente_nombre
            }
        )
        
        return NotificacionService.crear_notificacion(db, notificacion)
    
    @staticmethod
    def crear_notificacion_sistema(
        db: Session, 
        titulo: str, 
        mensaje: str, 
        es_urgente: bool = False
    ) -> Notificacion:
        """Crea notificación del sistema"""
        notificacion = NotificacionCreate(
            titulo=titulo,
            mensaje=mensaje,
            tipo=TipoNotificacion.SISTEMA,
            es_urgente=es_urgente,
            requiere_accion=False
        )
        
        return NotificacionService.crear_notificacion(db, notificacion)
    
    @staticmethod
    def limpiar_notificaciones_antiguas(db: Session, dias: int = 30) -> int:
        """Limpia notificaciones antiguas (más de X días)"""
        fecha_limite = datetime.utcnow() - timedelta(days=dias)
        
        # Solo eliminar notificaciones leídas y no urgentes
        notificaciones_eliminadas = db.query(Notificacion).filter(
            and_(
                Notificacion.fecha_creacion < fecha_limite,
                Notificacion.estado == EstadoNotificacion.LEIDA,
                Notificacion.es_urgente == False
            )
        ).delete()
        
        db.commit()
        return notificaciones_eliminadas
