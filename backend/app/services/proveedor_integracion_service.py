# app/services/proveedor_integracion_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, text, extract
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any, Tuple
import json
import requests
import asyncio
import aiohttp
from enum import Enum

from app.models.proveedor_integracion_model import (
    ProveedorIntegracion, CatalogoProveedor, PedidoProveedor, PedidoProveedorItem,
    NotificacionProveedor, LogIntegracion, ConfiguracionIntegracion,
    TipoIntegracion, EstadoIntegracion, TipoSincronizacion, EstadoPedido
)
from app.schemas.proveedor_integracion_schema import (
    ProveedorIntegracionCreate, ProveedorIntegracionUpdate,
    CatalogoProveedorCreate, CatalogoProveedorUpdate,
    PedidoProveedorCreate, PedidoProveedorUpdate,
    NotificacionProveedorCreate, NotificacionProveedorUpdate,
    LogIntegracionCreate, ConfiguracionIntegracionCreate,
    IntegracionFiltros, CatalogoFiltros, PedidoFiltros, NotificacionFiltros,
    ResumenIntegracion, ResumenCatalogo, ResumenPedidos,
    DashboardProveedores, EstadisticasIntegracion
)

class ProveedorIntegracionService:
    
    # === INTEGRACIONES CON PROVEEDORES ===
    
    @staticmethod
    def crear_integracion(
        db: Session,
        integracion: ProveedorIntegracionCreate,
        creado_por: Optional[int] = None
    ) -> ProveedorIntegracion:
        """Crea una nueva integración con proveedor"""
        db_integracion = ProveedorIntegracion(
            proveedor_id=integracion.proveedor_id,
            tipo_integracion=integracion.tipo_integracion.value,
            nombre_integracion=integracion.nombre_integracion,
            descripcion=integracion.descripcion,
            endpoint_url=integracion.endpoint_url,
            api_key=integracion.api_key,
            username=integracion.username,
            password=integracion.password,
            headers=json.dumps(integracion.headers) if integracion.headers else None,
            parametros=json.dumps(integracion.parametros) if integracion.parametros else None,
            tipo_sincronizacion=integracion.tipo_sincronizacion.value,
            frecuencia_sincronizacion=integracion.frecuencia_sincronizacion,
            hora_sincronizacion=integracion.hora_sincronizacion,
            dias_sincronizacion=json.dumps(integracion.dias_sincronizacion) if integracion.dias_sincronizacion else None,
            sincronizar_productos=integracion.sincronizar_productos,
            sincronizar_precios=integracion.sincronizar_precios,
            sincronizar_stock=integracion.sincronizar_stock,
            sincronizar_categorias=integracion.sincronizar_categorias,
            permitir_pedidos_automaticos=integracion.permitir_pedidos_automaticos,
            pedido_minimo=integracion.pedido_minimo,
            tiempo_entrega_dias=integracion.tiempo_entrega_dias,
            creado_por=creado_por
        )
        
        db.add(db_integracion)
        db.commit()
        db.refresh(db_integracion)
        
        return db_integracion
    
    @staticmethod
    def obtener_integraciones(
        db: Session,
        filtros: Optional[IntegracionFiltros] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ProveedorIntegracion]:
        """Obtiene integraciones con filtros"""
        query = db.query(ProveedorIntegracion)
        
        if filtros:
            if filtros.proveedor_id:
                query = query.filter(ProveedorIntegracion.proveedor_id == filtros.proveedor_id)
            if filtros.tipo_integracion:
                query = query.filter(ProveedorIntegracion.tipo_integracion == filtros.tipo_integracion.value)
            if filtros.estado:
                query = query.filter(ProveedorIntegracion.estado == filtros.estado.value)
            if filtros.activo is not None:
                query = query.filter(ProveedorIntegracion.activo == filtros.activo)
            if filtros.sincronizar_productos is not None:
                query = query.filter(ProveedorIntegracion.sincronizar_productos == filtros.sincronizar_productos)
            if filtros.permitir_pedidos_automaticos is not None:
                query = query.filter(ProveedorIntegracion.permitir_pedidos_automaticos == filtros.permitir_pedidos_automaticos)
        
        return query.order_by(desc(ProveedorIntegracion.fecha_creacion)).offset(skip).limit(limit).all()
    
    @staticmethod
    def sincronizar_catalogo(
        db: Session,
        integracion_id: int,
        forzar_sincronizacion: bool = False
    ) -> Dict[str, Any]:
        """Sincroniza el catálogo de productos con el proveedor"""
        integracion = db.query(ProveedorIntegracion).filter(ProveedorIntegracion.id == integracion_id).first()
        
        if not integracion:
            raise ValueError("Integración no encontrada")
        
        if integracion.estado != EstadoIntegracion.ACTIVA.value and not forzar_sincronizacion:
            raise ValueError("La integración no está activa")
        
        try:
            # Actualizar estado a sincronizando
            integracion.estado = EstadoIntegracion.TESTING.value
            db.commit()
            
            # Obtener datos del proveedor según el tipo de integración
            if integracion.tipo_integracion == TipoIntegracion.API_REST.value:
                datos = ProveedorIntegracionService._sincronizar_api_rest(integracion)
            elif integracion.tipo_integracion == TipoIntegracion.API_SOAP.value:
                datos = ProveedorIntegracionService._sincronizar_api_soap(integracion)
            elif integracion.tipo_integracion == TipoIntegracion.FTP.value:
                datos = ProveedorIntegracionService._sincronizar_ftp(integracion)
            else:
                raise ValueError(f"Tipo de integración no soportado: {integracion.tipo_integracion}")
            
            # Procesar datos y actualizar catálogo
            productos_actualizados = 0
            productos_nuevos = 0
            productos_eliminados = 0
            
            for producto_data in datos.get('productos', []):
                catalogo = db.query(CatalogoProveedor).filter(
                    CatalogoProveedor.integracion_id == integracion_id,
                    CatalogoProveedor.codigo_proveedor == producto_data['codigo']
                ).first()
                
                if catalogo:
                    # Actualizar producto existente
                    catalogo.nombre_proveedor = producto_data.get('nombre', catalogo.nombre_proveedor)
                    catalogo.descripcion_proveedor = producto_data.get('descripcion', catalogo.descripcion_proveedor)
                    catalogo.precio_proveedor = producto_data.get('precio', catalogo.precio_proveedor)
                    catalogo.stock_proveedor = producto_data.get('stock', catalogo.stock_proveedor)
                    catalogo.disponible = producto_data.get('disponible', catalogo.disponible)
                    catalogo.fecha_ultima_sincronizacion = datetime.utcnow()
                    productos_actualizados += 1
                else:
                    # Crear nuevo producto
                    nuevo_catalogo = CatalogoProveedor(
                        integracion_id=integracion_id,
                        codigo_proveedor=producto_data['codigo'],
                        nombre_proveedor=producto_data.get('nombre', ''),
                        descripcion_proveedor=producto_data.get('descripcion'),
                        categoria_proveedor=producto_data.get('categoria'),
                        marca_proveedor=producto_data.get('marca'),
                        modelo_proveedor=producto_data.get('modelo'),
                        sku_proveedor=producto_data.get('sku'),
                        precio_proveedor=producto_data.get('precio'),
                        stock_proveedor=producto_data.get('stock'),
                        disponible=producto_data.get('disponible', True),
                        fecha_ultima_sincronizacion=datetime.utcnow()
                    )
                    db.add(nuevo_catalogo)
                    productos_nuevos += 1
            
            # Actualizar estadísticas de la integración
            integracion.total_sincronizaciones += 1
            integracion.sincronizaciones_exitosas += 1
            integracion.fecha_ultima_sincronizacion = datetime.utcnow()
            integracion.estado = EstadoIntegracion.ACTIVA.value
            integracion.ultimo_error = None
            
            db.commit()
            
            # Crear log de sincronización exitosa
            ProveedorIntegracionService._crear_log(
                db, integracion_id, "sincronizacion", "info",
                f"Sincronización exitosa: {productos_actualizados} actualizados, {productos_nuevos} nuevos",
                datos_enviados={"integracion_id": integracion_id},
                datos_recibidos={"productos_procesados": len(datos.get('productos', []))}
            )
            
            return {
                "exito": True,
                "productos_actualizados": productos_actualizados,
                "productos_nuevos": productos_nuevos,
                "productos_eliminados": productos_eliminados,
                "total_productos": len(datos.get('productos', [])),
                "fecha_sincronizacion": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            # Manejar errores
            integracion.estado = EstadoIntegracion.ERROR.value
            integracion.sincronizaciones_fallidas += 1
            integracion.ultimo_error = str(e)
            db.commit()
            
            # Crear log de error
            ProveedorIntegracionService._crear_log(
                db, integracion_id, "sincronizacion", "error",
                f"Error en sincronización: {str(e)}",
                error_detalle=str(e)
            )
            
            return {
                "exito": False,
                "error": str(e),
                "fecha_error": datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def crear_pedido_automatico(
        db: Session,
        integracion_id: int,
        items: List[Dict[str, Any]],
        prioridad: str = "normal"
    ) -> PedidoProveedor:
        """Crea un pedido automático a un proveedor"""
        integracion = db.query(ProveedorIntegracion).filter(ProveedorIntegracion.id == integracion_id).first()
        
        if not integracion:
            raise ValueError("Integración no encontrada")
        
        if not integracion.permitir_pedidos_automaticos:
            raise ValueError("Los pedidos automáticos no están permitidos para esta integración")
        
        # Generar número de pedido interno
        numero_pedido = f"PED-{integracion_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        # Crear pedido
        pedido = PedidoProveedor(
            integracion_id=integracion_id,
            numero_pedido_interno=numero_pedido,
            tipo_pedido="automatico",
            prioridad=prioridad,
            fecha_pedido=datetime.utcnow()
        )
        
        db.add(pedido)
        db.flush()  # Para obtener el ID
        
        # Crear items del pedido
        subtotal = 0.0
        for item_data in items:
            catalogo = db.query(CatalogoProveedor).filter(
                CatalogoProveedor.id == item_data['catalogo_id']
            ).first()
            
            if not catalogo:
                continue
            
            cantidad = item_data['cantidad']
            precio_unitario = item_data.get('precio', catalogo.precio_proveedor or 0)
            descuento_unitario = item_data.get('descuento', 0)
            precio_total = cantidad * (precio_unitario - descuento_unitario)
            
            item = PedidoProveedorItem(
                pedido_id=pedido.id,
                catalogo_id=catalogo.id,
                codigo_proveedor=catalogo.codigo_proveedor,
                nombre_producto=catalogo.nombre_proveedor,
                descripcion=catalogo.descripcion_proveedor,
                cantidad_solicitada=cantidad,
                precio_unitario=precio_unitario,
                descuento_unitario=descuento_unitario,
                precio_total=precio_total
            )
            
            db.add(item)
            subtotal += precio_total
        
        # Calcular totales
        pedido.subtotal = subtotal
        pedido.descuento = 0.0  # Se puede calcular basado en reglas de negocio
        pedido.impuestos = 0.0  # Se puede calcular basado en reglas de negocio
        pedido.total = subtotal - pedido.descuento + pedido.impuestos
        
        db.commit()
        db.refresh(pedido)
        
        # Crear notificación
        ProveedorIntegracionService._crear_notificacion(
            db, integracion_id, "pedido", "info",
            f"Pedido automático creado: {numero_pedido}",
            f"Se ha creado un pedido automático con {len(items)} productos por un total de ${pedido.total:.2f}",
            datos_adicionales={"pedido_id": pedido.id, "total": pedido.total}
        )
        
        return pedido
    
    @staticmethod
    def obtener_dashboard_proveedores(db: Session) -> DashboardProveedores:
        """Obtiene el dashboard de proveedores"""
        # Obtener métricas principales
        total_proveedores = db.query(ProveedorIntegracion).count()
        proveedores_activos = db.query(ProveedorIntegracion).filter(ProveedorIntegracion.activo == True).count()
        integraciones_activas = db.query(ProveedorIntegracion).filter(
            ProveedorIntegracion.estado == EstadoIntegracion.ACTIVA.value
        ).count()
        productos_sincronizados = db.query(CatalogoProveedor).filter(CatalogoProveedor.activo == True).count()
        
        # Calcular tasa de sincronización exitosa
        total_sincronizaciones = db.query(func.sum(ProveedorIntegracion.total_sincronizaciones)).scalar() or 0
        sincronizaciones_exitosas = db.query(func.sum(ProveedorIntegracion.sincronizaciones_exitosas)).scalar() or 0
        tasa_exito = (sincronizaciones_exitosas / total_sincronizaciones * 100) if total_sincronizaciones > 0 else 0.0
        
        # Obtener pedidos pendientes
        pedidos_pendientes = db.query(PedidoProveedor).filter(
            PedidoProveedor.estado.in_([EstadoPedido.PENDIENTE.value, EstadoPedido.ENVIADO.value])
        ).count()
        
        # Obtener notificaciones pendientes
        notificaciones_pendientes = db.query(NotificacionProveedor).filter(
            NotificacionProveedor.leida == False
        ).count()
        
        # Obtener top performers (simulación)
        proveedores_mas_utilizados = ProveedorIntegracionService._obtener_proveedores_mas_utilizados(db)
        productos_mas_solicitados = ProveedorIntegracionService._obtener_productos_mas_solicitados(db)
        categorias_mas_populares = ProveedorIntegracionService._obtener_categorias_mas_populares(db)
        
        # Generar alertas
        alertas = ProveedorIntegracionService._generar_alertas_proveedores(db)
        
        # Calcular tendencias (simulación)
        tendencia_pedidos = "creciente"  # Se calcularía con datos reales
        tendencia_sincronizaciones = "estable"  # Se calcularía con datos reales
        tendencia_precios = "decreciente"  # Se calcularía con datos reales
        
        return DashboardProveedores(
            total_proveedores=total_proveedores,
            proveedores_activos=proveedores_activos,
            integraciones_activas=integraciones_activas,
            productos_sincronizados=productos_sincronizados,
            tasa_sincronizacion_exitosa=tasa_exito,
            tiempo_promedio_sincronizacion=0.0,  # Se calcularía con datos reales
            pedidos_pendientes=pedidos_pendientes,
            notificaciones_pendientes=notificaciones_pendientes,
            proveedores_mas_utilizados=proveedores_mas_utilizados,
            productos_mas_solicitados=productos_mas_solicitados,
            categorias_mas_populares=categorias_mas_populares,
            alertas=alertas,
            tendencia_pedidos=tendencia_pedidos,
            tendencia_sincronizaciones=tendencia_sincronizaciones,
            tendencia_precios=tendencia_precios
        )
    
    # === MÉTODOS AUXILIARES PRIVADOS ===
    
    @staticmethod
    def _sincronizar_api_rest(integracion: ProveedorIntegracion) -> Dict[str, Any]:
        """Sincroniza datos mediante API REST"""
        # Simulación de llamada a API REST
        # En implementación real se haría la llamada HTTP real
        return {
            "productos": [
                {
                    "codigo": "PROD001",
                    "nombre": "Producto 1",
                    "descripcion": "Descripción del producto 1",
                    "categoria": "Categoría A",
                    "marca": "Marca X",
                    "precio": 100.0,
                    "stock": 50,
                    "disponible": True
                },
                {
                    "codigo": "PROD002",
                    "nombre": "Producto 2",
                    "descripcion": "Descripción del producto 2",
                    "categoria": "Categoría B",
                    "marca": "Marca Y",
                    "precio": 200.0,
                    "stock": 25,
                    "disponible": True
                }
            ]
        }
    
    @staticmethod
    def _sincronizar_api_soap(integracion: ProveedorIntegracion) -> Dict[str, Any]:
        """Sincroniza datos mediante API SOAP"""
        # Simulación de llamada a API SOAP
        return {"productos": []}
    
    @staticmethod
    def _sincronizar_ftp(integracion: ProveedorIntegracion) -> Dict[str, Any]:
        """Sincroniza datos mediante FTP"""
        # Simulación de descarga desde FTP
        return {"productos": []}
    
    @staticmethod
    def _crear_log(
        db: Session,
        integracion_id: int,
        tipo_operacion: str,
        nivel: str,
        mensaje: str,
        endpoint: Optional[str] = None,
        metodo_http: Optional[str] = None,
        codigo_respuesta: Optional[int] = None,
        tiempo_respuesta_ms: Optional[int] = None,
        datos_enviados: Optional[Dict[str, Any]] = None,
        datos_recibidos: Optional[Dict[str, Any]] = None,
        error_detalle: Optional[str] = None
    ) -> LogIntegracion:
        """Crea un log de integración"""
        log = LogIntegracion(
            integracion_id=integracion_id,
            tipo_operacion=tipo_operacion,
            nivel=nivel,
            mensaje=mensaje,
            endpoint=endpoint,
            metodo_http=metodo_http,
            codigo_respuesta=codigo_respuesta,
            tiempo_respuesta_ms=tiempo_respuesta_ms,
            datos_enviados=json.dumps(datos_enviados) if datos_enviados else None,
            datos_recibidos=json.dumps(datos_recibidos) if datos_recibidos else None,
            error_detalle=error_detalle
        )
        
        db.add(log)
        db.commit()
        db.refresh(log)
        
        return log
    
    @staticmethod
    def _crear_notificacion(
        db: Session,
        integracion_id: int,
        tipo: str,
        titulo: str,
        mensaje: str,
        prioridad: str = "normal",
        datos_adicionales: Optional[Dict[str, Any]] = None,
        accion_requerida: Optional[str] = None,
        usuario_asignado: Optional[int] = None
    ) -> NotificacionProveedor:
        """Crea una notificación de proveedor"""
        notificacion = NotificacionProveedor(
            integracion_id=integracion_id,
            tipo=tipo,
            titulo=titulo,
            mensaje=mensaje,
            prioridad=prioridad,
            datos_adicionales=json.dumps(datos_adicionales) if datos_adicionales else None,
            accion_requerida=accion_requerida,
            usuario_asignado=usuario_asignado
        )
        
        db.add(notificacion)
        db.commit()
        db.refresh(notificacion)
        
        return notificacion
    
    @staticmethod
    def _obtener_proveedores_mas_utilizados(db: Session) -> List[Dict[str, Any]]:
        """Obtiene los proveedores más utilizados"""
        # Simulación de datos
        return [
            {"nombre": "Proveedor A", "pedidos": 150, "valor_total": 50000.0},
            {"nombre": "Proveedor B", "pedidos": 120, "valor_total": 45000.0},
            {"nombre": "Proveedor C", "pedidos": 100, "valor_total": 40000.0}
        ]
    
    @staticmethod
    def _obtener_productos_mas_solicitados(db: Session) -> List[Dict[str, Any]]:
        """Obtiene los productos más solicitados"""
        # Simulación de datos
        return [
            {"nombre": "Producto A", "cantidad": 500, "valor_total": 25000.0},
            {"nombre": "Producto B", "cantidad": 400, "valor_total": 20000.0},
            {"nombre": "Producto C", "cantidad": 300, "valor_total": 15000.0}
        ]
    
    @staticmethod
    def _obtener_categorias_mas_populares(db: Session) -> List[Dict[str, Any]]:
        """Obtiene las categorías más populares"""
        # Simulación de datos
        return [
            {"nombre": "Categoría A", "productos": 50, "valor_total": 30000.0},
            {"nombre": "Categoría B", "productos": 40, "valor_total": 25000.0},
            {"nombre": "Categoría C", "productos": 30, "valor_total": 20000.0}
        ]
    
    @staticmethod
    def _generar_alertas_proveedores(db: Session) -> List[Dict[str, Any]]:
        """Genera alertas para proveedores"""
        alertas = []
        
        # Verificar integraciones con errores
        integraciones_con_error = db.query(ProveedorIntegracion).filter(
            ProveedorIntegracion.estado == EstadoIntegracion.ERROR.value
        ).count()
        
        if integraciones_con_error > 0:
            alertas.append({
                "tipo": "error",
                "mensaje": f"{integraciones_con_error} integraciones con errores",
                "accion": "Revisar configuraciones de integración"
            })
        
        # Verificar productos sin stock
        productos_sin_stock = db.query(CatalogoProveedor).filter(
            CatalogoProveedor.stock_proveedor == 0,
            CatalogoProveedor.disponible == True
        ).count()
        
        if productos_sin_stock > 0:
            alertas.append({
                "tipo": "warning",
                "mensaje": f"{productos_sin_stock} productos sin stock",
                "accion": "Revisar disponibilidad con proveedores"
            })
        
        return alertas

