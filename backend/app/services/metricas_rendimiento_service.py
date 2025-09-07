# app/services/metricas_rendimiento_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, text, extract
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any, Tuple
import json
import statistics
from enum import Enum

from app.models.metricas_rendimiento_model import (
    MetricaRendimiento, MedicionMetrica, AlertaMetrica, ActivacionAlerta,
    BenchmarkMetrica, DashboardMetricas, DashboardMetrica, ReporteMetricas,
    TipoMetrica, CategoriaMetrica, TipoCalculo, FrecuenciaMedicion,
    EstadoAlerta, TipoAlerta
)
from app.schemas.metricas_rendimiento_schema import (
    MetricaRendimientoCreate, MetricaRendimientoUpdate,
    MedicionMetricaCreate, MedicionMetricaUpdate,
    AlertaMetricaCreate, AlertaMetricaUpdate,
    ActivacionAlertaCreate, ActivacionAlertaUpdate,
    BenchmarkMetricaCreate, BenchmarkMetricaUpdate,
    DashboardMetricasCreate, DashboardMetricasUpdate,
    DashboardMetricaCreate, DashboardMetricaUpdate,
    ReporteMetricasCreate, ReporteMetricasUpdate,
    MetricaFiltros, MedicionFiltros, AlertaFiltros,
    ResumenMetricas, EstadisticasMetrica, DashboardEjecutivo
)

class MetricasRendimientoService:
    
    # === MÉTRICAS DE RENDIMIENTO ===
    
    @staticmethod
    def crear_metrica(
        db: Session,
        metrica: MetricaRendimientoCreate,
        creado_por: Optional[int] = None
    ) -> MetricaRendimiento:
        """Crea una nueva métrica de rendimiento"""
        db_metrica = MetricaRendimiento(
            nombre=metrica.nombre,
            codigo=metrica.codigo.upper(),
            descripcion=metrica.descripcion,
            tipo_metrica=metrica.tipo_metrica.value,
            categoria=metrica.categoria.value,
            subcategoria=metrica.subcategoria,
            tipo_calculo=metrica.tipo_calculo.value,
            formula=metrica.formula,
            unidad_medida=metrica.unidad_medida,
            decimales=metrica.decimales,
            frecuencia_medicion=metrica.frecuencia_medicion.value,
            fuente_datos=metrica.fuente_datos,
            dependencias=json.dumps(metrica.dependencias) if metrica.dependencias else None,
            valor_objetivo=metrica.valor_objetivo,
            valor_minimo=metrica.valor_minimo,
            valor_maximo=metrica.valor_maximo,
            rango_optimo_inicio=metrica.rango_optimo_inicio,
            rango_optimo_fin=metrica.rango_optimo_fin,
            color_positivo=metrica.color_positivo,
            color_negativo=metrica.color_negativo,
            color_neutro=metrica.color_neutro,
            icono=metrica.icono,
            orden_display=metrica.orden_display,
            creado_por=creado_por
        )
        
        db.add(db_metrica)
        db.commit()
        db.refresh(db_metrica)
        
        return db_metrica
    
    @staticmethod
    def obtener_metricas(
        db: Session,
        filtros: Optional[MetricaFiltros] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[MetricaRendimiento]:
        """Obtiene métricas con filtros"""
        query = db.query(MetricaRendimiento)
        
        if filtros:
            if filtros.tipo_metrica:
                query = query.filter(MetricaRendimiento.tipo_metrica == filtros.tipo_metrica.value)
            if filtros.categoria:
                query = query.filter(MetricaRendimiento.categoria == filtros.categoria.value)
            if filtros.subcategoria:
                query = query.filter(MetricaRendimiento.subcategoria.ilike(f"%{filtros.subcategoria}%"))
            if filtros.frecuencia_medicion:
                query = query.filter(MetricaRendimiento.frecuencia_medicion == filtros.frecuencia_medicion.value)
            if filtros.activo is not None:
                query = query.filter(MetricaRendimiento.activo == filtros.activo)
            if filtros.creado_por:
                query = query.filter(MetricaRendimiento.creado_por == filtros.creado_por)
        
        return query.order_by(MetricaRendimiento.orden_display, MetricaRendimiento.nombre).offset(skip).limit(limit).all()
    
    @staticmethod
    def calcular_metrica(
        db: Session,
        metrica_id: int,
        fecha_medicion: Optional[datetime] = None,
        periodo_desde: Optional[datetime] = None,
        periodo_hasta: Optional[datetime] = None,
        calculado_por: Optional[int] = None
    ) -> MedicionMetrica:
        """Calcula el valor de una métrica para un período específico"""
        metrica = db.query(MetricaRendimiento).filter(MetricaRendimiento.id == metrica_id).first()
        
        if not metrica:
            raise ValueError("Métrica no encontrada")
        
        if not fecha_medicion:
            fecha_medicion = datetime.utcnow()
        
        # Calcular valor según el tipo de cálculo
        valor_actual = MetricasRendimientoService._calcular_valor_metrica(
            db, metrica, periodo_desde, periodo_hasta
        )
        
        # Obtener valor anterior para comparación
        valor_anterior = MetricasRendimientoService._obtener_valor_anterior(
            db, metrica_id, fecha_medicion
        )
        
        # Calcular variaciones
        variacion_absoluta = valor_actual - valor_anterior if valor_anterior else None
        variacion_porcentual = (variacion_absoluta / valor_anterior * 100) if valor_anterior and valor_anterior != 0 else None
        
        # Determinar tendencia
        tendencia = MetricasRendimientoService._determinar_tendencia(
            db, metrica_id, valor_actual, fecha_medicion
        )
        
        # Calcular percentil
        percentil = MetricasRendimientoService._calcular_percentil(
            db, metrica_id, valor_actual, fecha_medicion
        )
        
        # Calcular desviación estándar
        desviacion_estandar = MetricasRendimientoService._calcular_desviacion_estandar(
            db, metrica_id, fecha_medicion
        )
        
        # Crear medición
        medicion = MedicionMetrica(
            metrica_id=metrica_id,
            fecha_medicion=fecha_medicion,
            periodo_desde=periodo_desde,
            periodo_hasta=periodo_hasta,
            valor_actual=valor_actual,
            valor_anterior=valor_anterior,
            valor_objetivo=metrica.valor_objetivo,
            valor_historico_promedio=MetricasRendimientoService._calcular_promedio_historico(
                db, metrica_id, fecha_medicion
            ),
            variacion_absoluta=variacion_absoluta,
            variacion_porcentual=variacion_porcentual,
            tendencia=tendencia,
            velocidad_cambio=MetricasRendimientoService._calcular_velocidad_cambio(
                db, metrica_id, valor_actual, fecha_medicion
            ),
            percentil=percentil,
            desviacion_estandar=desviacion_estandar,
            calculado_por=calculado_por
        )
        
        db.add(medicion)
        db.commit()
        db.refresh(medicion)
        
        # Verificar alertas
        MetricasRendimientoService._verificar_alertas(db, metrica_id, medicion)
        
        return medicion
    
    @staticmethod
    def crear_alerta(
        db: Session,
        alerta: AlertaMetricaCreate,
        creado_por: Optional[int] = None
    ) -> AlertaMetrica:
        """Crea una nueva alerta para una métrica"""
        db_alerta = AlertaMetrica(
            metrica_id=alerta.metrica_id,
            nombre=alerta.nombre,
            descripcion=alerta.descripcion,
            tipo_alerta=alerta.tipo_alerta.value,
            condicion=alerta.condicion,
            umbral_minimo=alerta.umbral_minimo,
            umbral_maximo=alerta.umbral_maximo,
            umbral_porcentaje=alerta.umbral_porcentaje,
            ventana_tiempo=alerta.ventana_tiempo,
            notificar_email=alerta.notificar_email,
            notificar_dashboard=alerta.notificar_dashboard,
            notificar_movil=alerta.notificar_movil,
            usuarios_notificar=json.dumps(alerta.usuarios_notificar) if alerta.usuarios_notificar else None,
            frecuencia_verificacion=alerta.frecuencia_verificacion.value,
            max_alertas_por_dia=alerta.max_alertas_por_dia,
            cooldown_minutos=alerta.cooldown_minutos,
            creado_por=creado_por
        )
        
        db.add(db_alerta)
        db.commit()
        db.refresh(db_alerta)
        
        return db_alerta
    
    @staticmethod
    def obtener_dashboard_ejecutivo(db: Session) -> DashboardEjecutivo:
        """Obtiene el dashboard ejecutivo con métricas clave"""
        # Obtener métricas financieras (simulación)
        ingresos_mes = MetricasRendimientoService._obtener_ingresos_mes(db)
        ingresos_anio = MetricasRendimientoService._obtener_ingresos_anio(db)
        crecimiento_ingresos = MetricasRendimientoService._calcular_crecimiento_ingresos(db)
        margen_bruto = MetricasRendimientoService._obtener_margen_bruto(db)
        margen_neto = MetricasRendimientoService._obtener_margen_neto(db)
        rentabilidad_activos = MetricasRendimientoService._obtener_rentabilidad_activos(db)
        
        # Obtener métricas operativas (simulación)
        ventas_mes = MetricasRendimientoService._obtener_ventas_mes(db)
        clientes_activos = MetricasRendimientoService._obtener_clientes_activos(db)
        productos_vendidos = MetricasRendimientoService._obtener_productos_vendidos(db)
        ticket_promedio = MetricasRendimientoService._obtener_ticket_promedio(db)
        satisfaccion_cliente = MetricasRendimientoService._obtener_satisfaccion_cliente(db)
        
        # Obtener métricas de crecimiento (simulación)
        crecimiento_ventas = MetricasRendimientoService._calcular_crecimiento_ventas(db)
        crecimiento_clientes = MetricasRendimientoService._calcular_crecimiento_clientes(db)
        crecimiento_productos = MetricasRendimientoService._calcular_crecimiento_productos(db)
        penetracion_mercado = MetricasRendimientoService._obtener_penetracion_mercado(db)
        
        # Obtener alertas críticas
        alertas_criticas = MetricasRendimientoService._obtener_alertas_criticas(db)
        alertas_importantes = MetricasRendimientoService._obtener_alertas_importantes(db)
        
        # Calcular tendencias
        tendencia_ingresos = MetricasRendimientoService._calcular_tendencia_ingresos(db)
        tendencia_ventas = MetricasRendimientoService._calcular_tendencia_ventas(db)
        tendencia_clientes = MetricasRendimientoService._calcular_tendencia_clientes(db)
        tendencia_rentabilidad = MetricasRendimientoService._calcular_tendencia_rentabilidad(db)
        
        # Generar recomendaciones
        recomendaciones = MetricasRendimientoService._generar_recomendaciones(db)
        
        return DashboardEjecutivo(
            # Métricas financieras
            ingresos_mes=ingresos_mes,
            ingresos_anio=ingresos_anio,
            crecimiento_ingresos=crecimiento_ingresos,
            margen_bruto=margen_bruto,
            margen_neto=margen_neto,
            rentabilidad_activos=rentabilidad_activos,
            
            # Métricas operativas
            ventas_mes=ventas_mes,
            clientes_activos=clientes_activos,
            productos_vendidos=productos_vendidos,
            ticket_promedio=ticket_promedio,
            satisfaccion_cliente=satisfaccion_cliente,
            
            # Métricas de crecimiento
            crecimiento_ventas=crecimiento_ventas,
            crecimiento_clientes=crecimiento_clientes,
            crecimiento_productos=crecimiento_productos,
            penetracion_mercado=penetracion_mercado,
            
            # Alertas
            alertas_criticas=alertas_criticas,
            alertas_importantes=alertas_importantes,
            
            # Tendencias
            tendencia_ingresos=tendencia_ingresos,
            tendencia_ventas=tendencia_ventas,
            tendencia_clientes=tendencia_clientes,
            tendencia_rentabilidad=tendencia_rentabilidad,
            
            # Recomendaciones
            recomendaciones=recomendaciones,
            
            # Metadatos
            fecha_actualizacion=datetime.utcnow(),
            proxima_actualizacion=datetime.utcnow() + timedelta(hours=1)
        )
    
    @staticmethod
    def obtener_resumen_metricas(db: Session) -> ResumenMetricas:
        """Obtiene un resumen de todas las métricas"""
        total_metricas = db.query(MetricaRendimiento).count()
        metricas_activas = db.query(MetricaRendimiento).filter(MetricaRendimiento.activo == True).count()
        metricas_inactivas = total_metricas - metricas_activas
        
        total_mediciones = db.query(MedicionMetrica).count()
        mediciones_mes_actual = db.query(MedicionMetrica).filter(
            extract('month', MedicionMetrica.fecha_medicion) == datetime.utcnow().month,
            extract('year', MedicionMetrica.fecha_medicion) == datetime.utcnow().year
        ).count()
        
        total_alertas = db.query(AlertaMetrica).count()
        alertas_activas = db.query(AlertaMetrica).filter(AlertaMetrica.activo == True).count()
        alertas_disparadas = db.query(ActivacionAlerta).filter(
            ActivacionAlerta.fecha_activacion >= datetime.utcnow() - timedelta(days=30)
        ).count()
        
        total_dashboards = db.query(DashboardMetricas).count()
        dashboards_publicos = db.query(DashboardMetricas).filter(DashboardMetricas.es_publico == True).count()
        
        total_reportes = db.query(ReporteMetricas).count()
        reportes_programados = db.query(ReporteMetricas).filter(ReporteMetricas.programado == True).count()
        
        return ResumenMetricas(
            total_metricas=total_metricas,
            metricas_activas=metricas_activas,
            metricas_inactivas=metricas_inactivas,
            total_mediciones=total_mediciones,
            mediciones_mes_actual=mediciones_mes_actual,
            total_alertas=total_alertas,
            alertas_activas=alertas_activas,
            alertas_disparadas=alertas_disparadas,
            total_dashboards=total_dashboards,
            dashboards_publicos=dashboards_publicos,
            total_reportes=total_reportes,
            reportes_programados=reportes_programados
        )
    
    # === MÉTODOS AUXILIARES PRIVADOS ===
    
    @staticmethod
    def _calcular_valor_metrica(
        db: Session,
        metrica: MetricaRendimiento,
        periodo_desde: Optional[datetime] = None,
        periodo_hasta: Optional[datetime] = None
    ) -> float:
        """Calcula el valor de una métrica según su tipo de cálculo"""
        # Simulación de cálculo basado en el tipo de métrica
        if metrica.tipo_metrica == TipoMetrica.VENTAS.value:
            return MetricasRendimientoService._calcular_metricas_ventas(db, periodo_desde, periodo_hasta)
        elif metrica.tipo_metrica == TipoMetrica.RENTABILIDAD.value:
            return MetricasRendimientoService._calcular_metricas_rentabilidad(db, periodo_desde, periodo_hasta)
        elif metrica.tipo_metrica == TipoMetrica.CLIENTES.value:
            return MetricasRendimientoService._calcular_metricas_clientes(db, periodo_desde, periodo_hasta)
        elif metrica.tipo_metrica == TipoMetrica.PRODUCTOS.value:
            return MetricasRendimientoService._calcular_metricas_productos(db, periodo_desde, periodo_hasta)
        elif metrica.tipo_metrica == TipoMetrica.INVENTARIO.value:
            return MetricasRendimientoService._calcular_metricas_inventario(db, periodo_desde, periodo_hasta)
        elif metrica.tipo_metrica == TipoMetrica.FINANCIERO.value:
            return MetricasRendimientoService._calcular_metricas_financieras(db, periodo_desde, periodo_hasta)
        else:
            return 0.0
    
    @staticmethod
    def _calcular_metricas_ventas(db: Session, periodo_desde: Optional[datetime], periodo_hasta: Optional[datetime]) -> float:
        """Calcula métricas relacionadas con ventas"""
        # Simulación de cálculo de ventas
        return 150000.0
    
    @staticmethod
    def _calcular_metricas_rentabilidad(db: Session, periodo_desde: Optional[datetime], periodo_hasta: Optional[datetime]) -> float:
        """Calcula métricas relacionadas con rentabilidad"""
        # Simulación de cálculo de rentabilidad
        return 25.5
    
    @staticmethod
    def _calcular_metricas_clientes(db: Session, periodo_desde: Optional[datetime], periodo_hasta: Optional[datetime]) -> float:
        """Calcula métricas relacionadas con clientes"""
        # Simulación de cálculo de clientes
        return 1250.0
    
    @staticmethod
    def _calcular_metricas_productos(db: Session, periodo_desde: Optional[datetime], periodo_hasta: Optional[datetime]) -> float:
        """Calcula métricas relacionadas con productos"""
        # Simulación de cálculo de productos
        return 450.0
    
    @staticmethod
    def _calcular_metricas_inventario(db: Session, periodo_desde: Optional[datetime], periodo_hasta: Optional[datetime]) -> float:
        """Calcula métricas relacionadas con inventario"""
        # Simulación de cálculo de inventario
        return 85.0
    
    @staticmethod
    def _calcular_metricas_financieras(db: Session, periodo_desde: Optional[datetime], periodo_hasta: Optional[datetime]) -> float:
        """Calcula métricas relacionadas con finanzas"""
        # Simulación de cálculo financiero
        return 12.8
    
    @staticmethod
    def _obtener_valor_anterior(db: Session, metrica_id: int, fecha_medicion: datetime) -> Optional[float]:
        """Obtiene el valor anterior de una métrica"""
        medicion_anterior = db.query(MedicionMetrica).filter(
            MedicionMetrica.metrica_id == metrica_id,
            MedicionMetrica.fecha_medicion < fecha_medicion
        ).order_by(desc(MedicionMetrica.fecha_medicion)).first()
        
        return medicion_anterior.valor_actual if medicion_anterior else None
    
    @staticmethod
    def _determinar_tendencia(db: Session, metrica_id: int, valor_actual: float, fecha_medicion: datetime) -> str:
        """Determina la tendencia de una métrica"""
        # Obtener valores históricos recientes
        mediciones_recientes = db.query(MedicionMetrica).filter(
            MedicionMetrica.metrica_id == metrica_id,
            MedicionMetrica.fecha_medicion >= fecha_medicion - timedelta(days=30)
        ).order_by(desc(MedicionMetrica.fecha_medicion)).limit(5).all()
        
        if len(mediciones_recientes) < 3:
            return "estable"
        
        valores = [m.valor_actual for m in mediciones_recientes]
        
        # Calcular tendencia simple
        if valores[0] > valores[-1] * 1.05:  # 5% de crecimiento
            return "creciente"
        elif valores[0] < valores[-1] * 0.95:  # 5% de decrecimiento
            return "decreciente"
        else:
            return "estable"
    
    @staticmethod
    def _calcular_percentil(db: Session, metrica_id: int, valor_actual: float, fecha_medicion: datetime) -> Optional[float]:
        """Calcula el percentil de un valor respecto al histórico"""
        # Obtener valores históricos
        mediciones_historicas = db.query(MedicionMetrica).filter(
            MedicionMetrica.metrica_id == metrica_id,
            MedicionMetrica.fecha_medicion < fecha_medicion
        ).order_by(MedicionMetrica.valor_actual).all()
        
        if len(mediciones_historicas) < 10:
            return None
        
        valores = [m.valor_actual for m in mediciones_historicas]
        valores_menores = sum(1 for v in valores if v < valor_actual)
        
        return (valores_menores / len(valores)) * 100
    
    @staticmethod
    def _calcular_desviacion_estandar(db: Session, metrica_id: int, fecha_medicion: datetime) -> Optional[float]:
        """Calcula la desviación estándar de los valores históricos"""
        mediciones_historicas = db.query(MedicionMetrica).filter(
            MedicionMetrica.metrica_id == metrica_id,
            MedicionMetrica.fecha_medicion < fecha_medicion
        ).limit(30).all()
        
        if len(mediciones_historicas) < 3:
            return None
        
        valores = [m.valor_actual for m in mediciones_historicas]
        return statistics.stdev(valores) if len(valores) > 1 else None
    
    @staticmethod
    def _calcular_promedio_historico(db: Session, metrica_id: int, fecha_medicion: datetime) -> Optional[float]:
        """Calcula el promedio histórico de una métrica"""
        mediciones_historicas = db.query(MedicionMetrica).filter(
            MedicionMetrica.metrica_id == metrica_id,
            MedicionMetrica.fecha_medicion < fecha_medicion
        ).limit(30).all()
        
        if not mediciones_historicas:
            return None
        
        valores = [m.valor_actual for m in mediciones_historicas]
        return sum(valores) / len(valores)
    
    @staticmethod
    def _calcular_velocidad_cambio(db: Session, metrica_id: int, valor_actual: float, fecha_medicion: datetime) -> Optional[float]:
        """Calcula la velocidad de cambio de una métrica"""
        medicion_anterior = db.query(MedicionMetrica).filter(
            MedicionMetrica.metrica_id == metrica_id,
            MedicionMetrica.fecha_medicion < fecha_medicion
        ).order_by(desc(MedicionMetrica.fecha_medicion)).first()
        
        if not medicion_anterior:
            return None
        
        diferencia_tiempo = (fecha_medicion - medicion_anterior.fecha_medicion).total_seconds() / 3600  # En horas
        diferencia_valor = valor_actual - medicion_anterior.valor_actual
        
        return diferencia_valor / diferencia_tiempo if diferencia_tiempo > 0 else None
    
    @staticmethod
    def _verificar_alertas(db: Session, metrica_id: int, medicion: MedicionMetrica):
        """Verifica si se deben activar alertas para una medición"""
        alertas = db.query(AlertaMetrica).filter(
            AlertaMetrica.metrica_id == metrica_id,
            AlertaMetrica.activo == True,
            AlertaMetrica.estado == EstadoAlerta.ACTIVA.value
        ).all()
        
        for alerta in alertas:
            if MetricasRendimientoService._evaluar_condicion_alerta(alerta, medicion):
                MetricasRendimientoService._activar_alerta(db, alerta, medicion)
    
    @staticmethod
    def _evaluar_condicion_alerta(alerta: AlertaMetrica, medicion: MedicionMetrica) -> bool:
        """Evalúa si se debe activar una alerta"""
        valor = medicion.valor_actual
        
        if alerta.umbral_minimo is not None and valor < alerta.umbral_minimo:
            return True
        if alerta.umbral_maximo is not None and valor > alerta.umbral_maximo:
            return True
        if alerta.umbral_porcentaje is not None and medicion.variacion_porcentual:
            if abs(medicion.variacion_porcentual) > alerta.umbral_porcentaje:
                return True
        
        return False
    
    @staticmethod
    def _activar_alerta(db: Session, alerta: AlertaMetrica, medicion: MedicionMetrica):
        """Activa una alerta"""
        # Verificar cooldown
        ultima_activacion = db.query(ActivacionAlerta).filter(
            ActivacionAlerta.alerta_id == alerta.id,
            ActivacionAlerta.fecha_activacion >= datetime.utcnow() - timedelta(minutes=alerta.cooldown_minutos)
        ).first()
        
        if ultima_activacion:
            return
        
        # Crear activación
        activacion = ActivacionAlerta(
            alerta_id=alerta.id,
            medicion_id=medicion.id,
            valor_que_disparo=medicion.valor_actual,
            umbral_disparado=alerta.umbral_minimo or alerta.umbral_maximo,
            mensaje=f"Alerta {alerta.nombre}: {medicion.valor_actual}",
            severidad="media"
        )
        
        db.add(activacion)
        
        # Actualizar estadísticas de la alerta
        alerta.total_activaciones += 1
        alerta.activaciones_pendientes += 1
        alerta.fecha_ultima_activacion = datetime.utcnow()
        
        db.commit()
    
    # === MÉTODOS DE SIMULACIÓN PARA DASHBOARD EJECUTIVO ===
    
    @staticmethod
    def _obtener_ingresos_mes(db: Session) -> float:
        return 150000.0
    
    @staticmethod
    def _obtener_ingresos_anio(db: Session) -> float:
        return 1800000.0
    
    @staticmethod
    def _calcular_crecimiento_ingresos(db: Session) -> float:
        return 12.5
    
    @staticmethod
    def _obtener_margen_bruto(db: Session) -> float:
        return 35.2
    
    @staticmethod
    def _obtener_margen_neto(db: Session) -> float:
        return 18.7
    
    @staticmethod
    def _obtener_rentabilidad_activos(db: Session) -> float:
        return 15.3
    
    @staticmethod
    def _obtener_ventas_mes(db: Session) -> int:
        return 1250
    
    @staticmethod
    def _obtener_clientes_activos(db: Session) -> int:
        return 850
    
    @staticmethod
    def _obtener_productos_vendidos(db: Session) -> int:
        return 450
    
    @staticmethod
    def _obtener_ticket_promedio(db: Session) -> float:
        return 120.0
    
    @staticmethod
    def _obtener_satisfaccion_cliente(db: Session) -> float:
        return 4.2
    
    @staticmethod
    def _calcular_crecimiento_ventas(db: Session) -> float:
        return 8.5
    
    @staticmethod
    def _calcular_crecimiento_clientes(db: Session) -> float:
        return 15.2
    
    @staticmethod
    def _calcular_crecimiento_productos(db: Session) -> float:
        return 22.1
    
    @staticmethod
    def _obtener_penetracion_mercado(db: Session) -> float:
        return 12.8
    
    @staticmethod
    def _obtener_alertas_criticas(db: Session) -> List[Dict[str, Any]]:
        return [
            {"tipo": "rentabilidad", "mensaje": "Margen neto por debajo del objetivo", "severidad": "alta"},
            {"tipo": "inventario", "mensaje": "Stock bajo en productos críticos", "severidad": "media"}
        ]
    
    @staticmethod
    def _obtener_alertas_importantes(db: Session) -> List[Dict[str, Any]]:
        return [
            {"tipo": "clientes", "mensaje": "Satisfacción del cliente en descenso", "severidad": "media"},
            {"tipo": "ventas", "mensaje": "Tendencia de ventas estable", "severidad": "baja"}
        ]
    
    @staticmethod
    def _calcular_tendencia_ingresos(db: Session) -> str:
        return "creciente"
    
    @staticmethod
    def _calcular_tendencia_ventas(db: Session) -> str:
        return "estable"
    
    @staticmethod
    def _calcular_tendencia_clientes(db: Session) -> str:
        return "creciente"
    
    @staticmethod
    def _calcular_tendencia_rentabilidad(db: Session) -> str:
        return "decreciente"
    
    @staticmethod
    def _generar_recomendaciones(db: Session) -> List[str]:
        return [
            "Revisar estrategia de precios para mejorar margen neto",
            "Implementar programa de fidelización de clientes",
            "Optimizar gestión de inventario para reducir costos",
            "Considerar expansión a nuevos mercados"
        ]

