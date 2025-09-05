# app/services/descuento_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, text
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple
import json

from app.models.descuento_model import Descuento, DescuentoUso, Promocion, TipoDescuento, EstadoDescuento
from app.schemas.descuento_schema import (
    DescuentoCreate, DescuentoUpdate, DescuentoAplicacion, 
    DescuentoResultado, DescuentoEstadisticas, DescuentoFiltros
)

class DescuentoService:
    
    @staticmethod
    def crear_descuento(db: Session, descuento: DescuentoCreate, creado_por: int) -> Descuento:
        """Crea un nuevo descuento"""
        # Convertir listas a JSON strings
        productos_json = json.dumps(descuento.productos_ids) if descuento.productos_ids else None
        clientes_json = json.dumps(descuento.clientes_ids) if descuento.clientes_ids else None
        categorias_json = json.dumps(descuento.categorias_ids) if descuento.categorias_ids else None
        
        db_descuento = Descuento(
            codigo=descuento.codigo.upper().strip(),
            nombre=descuento.nombre,
            descripcion=descuento.descripcion,
            tipo=descuento.tipo.value,  # Ya es string
            valor=descuento.valor,
            valor_minimo=descuento.valor_minimo,
            valor_maximo=descuento.valor_maximo,
            limite_usos=descuento.limite_usos,
            usos_por_cliente=descuento.usos_por_cliente,
            fecha_inicio=descuento.fecha_inicio,
            fecha_fin=descuento.fecha_fin,
            aplica_envio=descuento.aplica_envio,
            aplica_impuestos=descuento.aplica_impuestos,
            productos_ids=productos_json,
            clientes_ids=clientes_json,
            categorias_ids=categorias_json,
            notas_internas=descuento.notas_internas,
            creado_por=creado_por,
            estado=EstadoDescuento.ACTIVO.value,  # Convertir a string
            es_activo=True
        )
        
        db.add(db_descuento)
        db.commit()
        db.refresh(db_descuento)
        
        return db_descuento
    
    @staticmethod
    def obtener_descuentos(
        db: Session, 
        filtros: Optional[DescuentoFiltros] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Descuento]:
        """Obtiene descuentos con filtros"""
        query = db.query(Descuento)
        
        if filtros:
            if filtros.codigo:
                query = query.filter(Descuento.codigo.ilike(f"%{filtros.codigo}%"))
            if filtros.tipo:
                query = query.filter(Descuento.tipo == filtros.tipo)
            if filtros.estado:
                query = query.filter(Descuento.estado == filtros.estado)
            if filtros.es_activo is not None:
                query = query.filter(Descuento.es_activo == filtros.es_activo)
            if filtros.fecha_desde:
                query = query.filter(Descuento.fecha_inicio >= filtros.fecha_desde)
            if filtros.fecha_hasta:
                query = query.filter(Descuento.fecha_inicio <= filtros.fecha_hasta)
            if filtros.cliente_id:
                query = query.filter(
                    or_(
                        Descuento.clientes_ids.is_(None),  # Descuentos globales
                        Descuento.clientes_ids.contains(f'"{filtros.cliente_id}"')
                    )
                )
            if filtros.producto_id:
                query = query.filter(
                    or_(
                        Descuento.productos_ids.is_(None),  # Descuentos globales
                        Descuento.productos_ids.contains(f'"{filtros.producto_id}"')
                    )
                )
        
        return query.order_by(desc(Descuento.fecha_creacion)).offset(skip).limit(limit).all()
    
    @staticmethod
    def obtener_descuento_por_codigo(db: Session, codigo: str) -> Optional[Descuento]:
        """Obtiene un descuento por su código"""
        return db.query(Descuento).filter(
            Descuento.codigo == codigo.upper().strip()
        ).first()
    
    @staticmethod
    def obtener_descuento(db: Session, descuento_id: int) -> Optional[Descuento]:
        """Obtiene un descuento por ID"""
        return db.query(Descuento).filter(Descuento.id == descuento_id).first()
    
    @staticmethod
    def actualizar_descuento(
        db: Session, 
        descuento_id: int, 
        descuento_update: DescuentoUpdate
    ) -> Optional[Descuento]:
        """Actualiza un descuento"""
        db_descuento = db.query(Descuento).filter(Descuento.id == descuento_id).first()
        
        if not db_descuento:
            return None
        
        # Actualizar campos
        for field, value in descuento_update.dict(exclude_unset=True).items():
            if field in ['productos_ids', 'clientes_ids', 'categorias_ids']:
                # Convertir listas a JSON
                setattr(db_descuento, field, json.dumps(value) if value else None)
            else:
                setattr(db_descuento, field, value)
        
        # Actualizar estado si es necesario
        if descuento_update.estado:
            db_descuento.estado = descuento_update.estado
            db_descuento.es_activo = descuento_update.estado == EstadoDescuento.ACTIVO
        
        db.commit()
        db.refresh(db_descuento)
        
        return db_descuento
    
    @staticmethod
    def aplicar_descuento(
        db: Session, 
        aplicacion: DescuentoAplicacion
    ) -> DescuentoResultado:
        """Aplica un descuento a una compra"""
        descuento = DescuentoService.obtener_descuento_por_codigo(db, aplicacion.codigo)
        
        if not descuento:
            return DescuentoResultado(
                aplicable=False,
                monto_final=aplicacion.monto_total,
                mensaje="Código de descuento no encontrado"
            )
        
        # Verificar si el descuento está activo
        if not descuento.es_activo or descuento.estado != EstadoDescuento.ACTIVO:
            return DescuentoResultado(
                aplicable=False,
                monto_final=aplicacion.monto_total,
                mensaje="El descuento no está activo"
            )
        
        # Verificar fechas
        ahora = datetime.utcnow()
        if descuento.fecha_inicio > ahora:
            return DescuentoResultado(
                aplicable=False,
                monto_final=aplicacion.monto_total,
                mensaje="El descuento aún no está disponible"
            )
        
        if descuento.fecha_fin and descuento.fecha_fin < ahora:
            return DescuentoResultado(
                aplicable=False,
                monto_final=aplicacion.monto_total,
                mensaje="El descuento ha expirado"
            )
        
        # Verificar límite de usos
        if descuento.limite_usos and descuento.usos_actuales >= descuento.limite_usos:
            return DescuentoResultado(
                aplicable=False,
                monto_final=aplicacion.monto_total,
                mensaje="El descuento ha alcanzado su límite de usos"
            )
        
        # Verificar compra mínima
        if descuento.valor_minimo and aplicacion.monto_total < descuento.valor_minimo:
            return DescuentoResultado(
                aplicable=False,
                monto_final=aplicacion.monto_total,
                mensaje=f"Compra mínima requerida: ${descuento.valor_minimo:,.2f}"
            )
        
        # Verificar restricciones de productos
        if descuento.productos_ids:
            productos_permitidos = json.loads(descuento.productos_ids)
            if not any(pid in productos_permitidos for pid in aplicacion.productos_ids):
                return DescuentoResultado(
                    aplicable=False,
                    monto_final=aplicacion.monto_total,
                    mensaje="El descuento no aplica para estos productos"
                )
        
        # Verificar restricciones de cliente
        if descuento.clientes_ids and aplicacion.cliente_id:
            clientes_permitidos = json.loads(descuento.clientes_ids)
            if aplicacion.cliente_id not in clientes_permitidos:
                return DescuentoResultado(
                    aplicable=False,
                    monto_final=aplicacion.monto_total,
                    mensaje="El descuento no aplica para este cliente"
                )
        
        # Calcular descuento
        monto_descuento = DescuentoService._calcular_descuento(
            descuento, aplicacion.monto_total
        )
        
        # Aplicar límite máximo
        if descuento.valor_maximo and monto_descuento > descuento.valor_maximo:
            monto_descuento = descuento.valor_maximo
        
        monto_final = aplicacion.monto_total - monto_descuento
        
        return DescuentoResultado(
            aplicable=True,
            monto_descuento=monto_descuento,
            monto_final=monto_final,
            mensaje="Descuento aplicado correctamente",
            descuento=descuento
        )
    
    @staticmethod
    def _calcular_descuento(descuento: Descuento, monto: float) -> float:
        """Calcula el monto del descuento según el tipo"""
        if descuento.tipo == TipoDescuento.PORCENTAJE:
            return monto * (descuento.valor / 100)
        elif descuento.tipo == TipoDescuento.MONTO_FIJO:
            return min(descuento.valor, monto)
        elif descuento.tipo == TipoDescuento.DESCUENTO_VOLUMEN:
            # Descuento por volumen (ej: 10% si compras más de $1000)
            if monto >= descuento.valor_minimo:
                return monto * (descuento.valor / 100)
            return 0.0
        elif descuento.tipo == TipoDescuento.DESCUENTO_CLIENTE:
            # Descuento específico para cliente
            return monto * (descuento.valor / 100)
        elif descuento.tipo == TipoDescuento.PROMOCION_TEMPORAL:
            # Promoción temporal
            return monto * (descuento.valor / 100)
        
        return 0.0
    
    @staticmethod
    def registrar_uso_descuento(
        db: Session,
        descuento_id: int,
        cliente_id: Optional[int],
        venta_id: Optional[int],
        monto_original: float,
        monto_descuento: float,
        monto_final: float,
        ip_cliente: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> DescuentoUso:
        """Registra el uso de un descuento"""
        # Crear registro de uso
        uso = DescuentoUso(
            descuento_id=descuento_id,
            cliente_id=cliente_id,
            venta_id=venta_id,
            monto_original=monto_original,
            monto_descuento=monto_descuento,
            monto_final=monto_final,
            ip_cliente=ip_cliente,
            user_agent=user_agent
        )
        
        db.add(uso)
        
        # Actualizar contador de usos
        descuento = db.query(Descuento).filter(Descuento.id == descuento_id).first()
        if descuento:
            descuento.usos_actuales += 1
            
            # Verificar si se alcanzó el límite
            if descuento.limite_usos and descuento.usos_actuales >= descuento.limite_usos:
                descuento.estado = EstadoDescuento.AGOTADO
                descuento.es_activo = False
        
        db.commit()
        db.refresh(uso)
        
        return uso
    
    @staticmethod
    def obtener_estadisticas(db: Session) -> DescuentoEstadisticas:
        """Obtiene estadísticas de descuentos"""
        # Estadísticas básicas
        total_descuentos = db.query(Descuento).count()
        descuentos_activos = db.query(Descuento).filter(Descuento.es_activo == True).count()
        descuentos_expirados = db.query(Descuento).filter(Descuento.estado == EstadoDescuento.EXPIRADO).count()
        
        # Estadísticas de usos
        total_usos = db.query(DescuentoUso).count()
        monto_total_descuentado = db.query(func.sum(DescuentoUso.monto_descuento)).scalar() or 0.0
        
        # Descuentos por tipo
        descuentos_por_tipo = {}
        for tipo in TipoDescuento:
            count = db.query(Descuento).filter(Descuento.tipo == tipo).count()
            descuentos_por_tipo[tipo.value] = count
        
        # Top descuentos por uso
        top_descuentos = db.query(
            Descuento.codigo,
            Descuento.nombre,
            func.count(DescuentoUso.id).label('usos'),
            func.sum(DescuentoUso.monto_descuento).label('monto_descuentado')
        ).join(DescuentoUso, Descuento.id == DescuentoUso.descuento_id)\
         .group_by(Descuento.id, Descuento.codigo, Descuento.nombre)\
         .order_by(desc('usos'))\
         .limit(10).all()
        
        top_descuentos_list = [
            {
                "codigo": row.codigo,
                "nombre": row.nombre,
                "usos": row.usos,
                "monto_descuentado": round(row.monto_descuentado or 0.0, 2)
            }
            for row in top_descuentos
        ]
        
        # Usos por mes (últimos 12 meses)
        fecha_inicio = datetime.utcnow() - timedelta(days=365)
        usos_por_mes = db.query(
            func.date_trunc('month', DescuentoUso.fecha_uso).label('mes'),
            func.count(DescuentoUso.id).label('usos'),
            func.sum(DescuentoUso.monto_descuento).label('monto_descuentado')
        ).filter(DescuentoUso.fecha_uso >= fecha_inicio)\
         .group_by(func.date_trunc('month', DescuentoUso.fecha_uso))\
         .order_by('mes').all()
        
        usos_por_mes_list = [
            {
                "mes": row.mes.strftime("%Y-%m"),
                "usos": row.usos,
                "monto_descuentado": round(row.monto_descuentado or 0.0, 2)
            }
            for row in usos_por_mes
        ]
        
        return DescuentoEstadisticas(
            total_descuentos=total_descuentos,
            descuentos_activos=descuentos_activos,
            descuentos_expirados=descuentos_expirados,
            total_usos=total_usos,
            monto_total_descuentado=round(monto_total_descuentado, 2),
            descuentos_por_tipo=descuentos_por_tipo,
            top_descuentos=top_descuentos_list,
            usos_por_mes=usos_por_mes_list
        )
    
    @staticmethod
    def actualizar_estados_descuentos(db: Session) -> int:
        """Actualiza los estados de los descuentos según las fechas"""
        ahora = datetime.utcnow()
        
        # Marcar como expirados
        expirados = db.query(Descuento).filter(
            and_(
                Descuento.estado == EstadoDescuento.ACTIVO,
                Descuento.fecha_fin < ahora
            )
        ).update({
            Descuento.estado: EstadoDescuento.EXPIRADO,
            Descuento.es_activo: False
        })
        
        # Marcar como activos los que están en rango
        activos = db.query(Descuento).filter(
            and_(
                Descuento.estado == EstadoDescuento.INACTIVO,
                Descuento.fecha_inicio <= ahora,
                or_(
                    Descuento.fecha_fin.is_(None),
                    Descuento.fecha_fin > ahora
                )
            )
        ).update({
            Descuento.estado: EstadoDescuento.ACTIVO,
            Descuento.es_activo: True
        })
        
        db.commit()
        
        return expirados + activos
