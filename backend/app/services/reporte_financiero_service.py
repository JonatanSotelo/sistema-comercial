# app/services/reporte_financiero_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, text, extract
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any, Tuple
import json
import math

from app.models.reporte_financiero_model import (
    ReporteFinanciero, EstadoResultados, FlujoCaja, AnalisisRentabilidad,
    ProyeccionFinanciera, MetricaFinanciera, TipoReporteFinanciero, 
    PeriodoReporte, EstadoReporte
)
from app.schemas.reporte_financiero_schema import (
    ReporteFinancieroCreate, ReporteFinancieroUpdate,
    EstadoResultadosCreate, FlujoCajaCreate, AnalisisRentabilidadCreate,
    ProyeccionFinancieraCreate, MetricaFinancieraCreate,
    ReporteFiltros, ReporteResumen, DashboardFinanciero,
    ReporteComparativo, ExportacionReporte
)

class ReporteFinancieroService:
    
    # === REPORTES FINANCIEROS ===
    
    @staticmethod
    def crear_reporte_financiero(
        db: Session,
        reporte: ReporteFinancieroCreate,
        creado_por: Optional[int] = None
    ) -> ReporteFinanciero:
        """Crea un nuevo reporte financiero"""
        # Calcular fecha de expiración (30 días por defecto)
        fecha_expiracion = datetime.utcnow() + timedelta(days=30)
        
        db_reporte = ReporteFinanciero(
            nombre=reporte.nombre,
            tipo=reporte.tipo,
            periodo=reporte.periodo,
            fecha_inicio=reporte.fecha_inicio,
            fecha_fin=reporte.fecha_fin,
            incluir_detalles=reporte.incluir_detalles,
            incluir_proyecciones=reporte.incluir_proyecciones,
            incluir_comparaciones=reporte.incluir_comparaciones,
            formato_salida=reporte.formato_salida,
            descripcion=reporte.descripcion,
            parametros_personalizados=json.dumps(reporte.parametros_personalizados) if reporte.parametros_personalizados else None,
            filtro_productos=json.dumps(reporte.filtro_productos) if reporte.filtro_productos else None,
            filtro_clientes=json.dumps(reporte.filtro_clientes) if reporte.filtro_clientes else None,
            filtro_categorias=json.dumps(reporte.filtro_categorias) if reporte.filtro_categorias else None,
            filtro_proveedores=json.dumps(reporte.filtro_proveedores) if reporte.filtro_proveedores else None,
            creado_por=creado_por,
            fecha_expiracion=fecha_expiracion
        )
        
        db.add(db_reporte)
        db.commit()
        db.refresh(db_reporte)
        
        return db_reporte
    
    @staticmethod
    def obtener_reportes_financieros(
        db: Session,
        filtros: Optional[ReporteFiltros] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ReporteFinanciero]:
        """Obtiene reportes financieros con filtros"""
        query = db.query(ReporteFinanciero)
        
        if filtros:
            if filtros.tipo:
                query = query.filter(ReporteFinanciero.tipo == filtros.tipo)
            if filtros.periodo:
                query = query.filter(ReporteFinanciero.periodo == filtros.periodo)
            if filtros.estado:
                query = query.filter(ReporteFinanciero.estado == filtros.estado)
            if filtros.fecha_desde:
                query = query.filter(ReporteFinanciero.fecha_inicio >= filtros.fecha_desde)
            if filtros.fecha_hasta:
                query = query.filter(ReporteFinanciero.fecha_inicio <= filtros.fecha_hasta)
            if filtros.creado_por:
                query = query.filter(ReporteFinanciero.creado_por == filtros.creado_por)
            if filtros.solo_activos:
                query = query.filter(ReporteFinanciero.estado != EstadoReporte.EXPIRADO)
        
        return query.order_by(desc(ReporteFinanciero.fecha_generacion)).offset(skip).limit(limit).all()
    
    @staticmethod
    def generar_estado_resultados(
        db: Session,
        reporte_id: int,
        periodo_desde: date,
        periodo_hasta: date
    ) -> EstadoResultados:
        """Genera un estado de resultados para un período específico"""
        # Obtener datos de ventas
        ventas_data = ReporteFinancieroService._obtener_datos_ventas(db, periodo_desde, periodo_hasta)
        costos_data = ReporteFinancieroService._obtener_datos_costos(db, periodo_desde, periodo_hasta)
        gastos_data = ReporteFinancieroService._obtener_datos_gastos(db, periodo_desde, periodo_hasta)
        
        # Calcular ventas netas
        ventas_brutas = ventas_data.get('ventas_brutas', 0.0)
        descuentos_ventas = ventas_data.get('descuentos', 0.0)
        devoluciones_ventas = ventas_data.get('devoluciones', 0.0)
        ventas_netas = ventas_brutas - descuentos_ventas - devoluciones_ventas
        
        # Calcular costo de ventas
        inventario_inicial = costos_data.get('inventario_inicial', 0.0)
        compras = costos_data.get('compras', 0.0)
        inventario_final = costos_data.get('inventario_final', 0.0)
        costo_ventas = inventario_inicial + compras - inventario_final
        
        # Calcular utilidad bruta
        utilidad_bruta = ventas_netas - costo_ventas
        margen_bruto_porcentaje = (utilidad_bruta / ventas_netas * 100) if ventas_netas > 0 else 0.0
        
        # Calcular gastos operativos
        gastos_administrativos = gastos_data.get('administrativos', 0.0)
        gastos_ventas = gastos_data.get('ventas', 0.0)
        gastos_generales = gastos_data.get('generales', 0.0)
        total_gastos_operativos = gastos_administrativos + gastos_ventas + gastos_generales
        
        # Calcular utilidad operativa
        utilidad_operativa = utilidad_bruta - total_gastos_operativos
        margen_operativo_porcentaje = (utilidad_operativa / ventas_netas * 100) if ventas_netas > 0 else 0.0
        
        # Otros ingresos y gastos
        otros_ingresos = gastos_data.get('otros_ingresos', 0.0)
        otros_gastos = gastos_data.get('otros_gastos', 0.0)
        intereses = gastos_data.get('intereses', 0.0)
        impuestos = gastos_data.get('impuestos', 0.0)
        
        # Calcular utilidad neta
        utilidad_neta = utilidad_operativa + otros_ingresos - otros_gastos - intereses - impuestos
        margen_neto_porcentaje = (utilidad_neta / ventas_netas * 100) if ventas_netas > 0 else 0.0
        
        # Crear estado de resultados
        estado_resultados = EstadoResultados(
            reporte_id=reporte_id,
            ventas_brutas=ventas_brutas,
            descuentos_ventas=descuentos_ventas,
            devoluciones_ventas=devoluciones_ventas,
            ventas_netas=ventas_netas,
            inventario_inicial=inventario_inicial,
            compras=compras,
            inventario_final=inventario_final,
            costo_ventas=costo_ventas,
            utilidad_bruta=utilidad_bruta,
            margen_bruto_porcentaje=margen_bruto_porcentaje,
            gastos_administrativos=gastos_administrativos,
            gastos_ventas=gastos_ventas,
            gastos_generales=gastos_generales,
            total_gastos_operativos=total_gastos_operativos,
            utilidad_operativa=utilidad_operativa,
            margen_operativo_porcentaje=margen_operativo_porcentaje,
            otros_ingresos=otros_ingresos,
            otros_gastos=otros_gastos,
            intereses=intereses,
            impuestos=impuestos,
            utilidad_neta=utilidad_neta,
            margen_neto_porcentaje=margen_neto_porcentaje,
            periodo_desde=periodo_desde,
            periodo_hasta=periodo_hasta
        )
        
        db.add(estado_resultados)
        db.commit()
        db.refresh(estado_resultados)
        
        return estado_resultados
    
    @staticmethod
    def generar_flujo_caja(
        db: Session,
        reporte_id: int,
        periodo_desde: date,
        periodo_hasta: date
    ) -> FlujoCaja:
        """Genera un flujo de caja para un período específico"""
        # Obtener datos de flujo de caja
        flujo_data = ReporteFinancieroService._obtener_datos_flujo_caja(db, periodo_desde, periodo_hasta)
        
        # Flujo operativo
        ingresos_operativos = flujo_data.get('ingresos_operativos', 0.0)
        pagos_proveedores = flujo_data.get('pagos_proveedores', 0.0)
        pagos_empleados = flujo_data.get('pagos_empleados', 0.0)
        pagos_impuestos = flujo_data.get('pagos_impuestos', 0.0)
        otros_pagos_operativos = flujo_data.get('otros_pagos_operativos', 0.0)
        flujo_operativo = ingresos_operativos - pagos_proveedores - pagos_empleados - pagos_impuestos - otros_pagos_operativos
        
        # Flujo de inversión
        compras_activos = flujo_data.get('compras_activos', 0.0)
        ventas_activos = flujo_data.get('ventas_activos', 0.0)
        inversiones = flujo_data.get('inversiones', 0.0)
        flujo_inversion = ventas_activos - compras_activos - inversiones
        
        # Flujo de financiamiento
        prestamos_recibidos = flujo_data.get('prestamos_recibidos', 0.0)
        pagos_prestamos = flujo_data.get('pagos_prestamos', 0.0)
        dividendos_pagados = flujo_data.get('dividendos_pagados', 0.0)
        flujo_financiamiento = prestamos_recibidos - pagos_prestamos - dividendos_pagados
        
        # Flujo de caja neto
        flujo_caja_neto = flujo_operativo + flujo_inversion + flujo_financiamiento
        
        # Saldos de caja
        saldo_caja_inicial = flujo_data.get('saldo_caja_inicial', 0.0)
        saldo_caja_final = saldo_caja_inicial + flujo_caja_neto
        
        # Crear flujo de caja
        flujo_caja = FlujoCaja(
            reporte_id=reporte_id,
            ingresos_operativos=ingresos_operativos,
            pagos_proveedores=pagos_proveedores,
            pagos_empleados=pagos_empleados,
            pagos_impuestos=pagos_impuestos,
            otros_pagos_operativos=otros_pagos_operativos,
            flujo_operativo=flujo_operativo,
            compras_activos=compras_activos,
            ventas_activos=ventas_activos,
            inversiones=inversiones,
            flujo_inversion=flujo_inversion,
            prestamos_recibidos=prestamos_recibidos,
            pagos_prestamos=pagos_prestamos,
            dividendos_pagados=dividendos_pagados,
            flujo_financiamiento=flujo_financiamiento,
            flujo_caja_neto=flujo_caja_neto,
            saldo_caja_inicial=saldo_caja_inicial,
            saldo_caja_final=saldo_caja_final,
            periodo_desde=periodo_desde,
            periodo_hasta=periodo_hasta
        )
        
        db.add(flujo_caja)
        db.commit()
        db.refresh(flujo_caja)
        
        return flujo_caja
    
    @staticmethod
    def generar_analisis_rentabilidad(
        db: Session,
        reporte_id: int,
        tipo_entidad: str,
        periodo_desde: date,
        periodo_hasta: date
    ) -> List[AnalisisRentabilidad]:
        """Genera análisis de rentabilidad por entidad"""
        analisis_list = []
        
        if tipo_entidad == "producto":
            productos = ReporteFinancieroService._obtener_productos_rentabilidad(db, periodo_desde, periodo_hasta)
            for producto in productos:
                analisis = ReporteFinancieroService._calcular_rentabilidad_producto(
                    db, reporte_id, producto, periodo_desde, periodo_hasta
                )
                analisis_list.append(analisis)
        
        elif tipo_entidad == "cliente":
            clientes = ReporteFinancieroService._obtener_clientes_rentabilidad(db, periodo_desde, periodo_hasta)
            for cliente in clientes:
                analisis = ReporteFinancieroService._calcular_rentabilidad_cliente(
                    db, reporte_id, cliente, periodo_desde, periodo_hasta
                )
                analisis_list.append(analisis)
        
        elif tipo_entidad == "categoria":
            categorias = ReporteFinancieroService._obtener_categorias_rentabilidad(db, periodo_desde, periodo_hasta)
            for categoria in categorias:
                analisis = ReporteFinancieroService._calcular_rentabilidad_categoria(
                    db, reporte_id, categoria, periodo_desde, periodo_hasta
                )
                analisis_list.append(analisis)
        
        # Ordenar por rentabilidad y asignar ranking
        analisis_list.sort(key=lambda x: x.margen_bruto_porcentaje, reverse=True)
        for i, analisis in enumerate(analisis_list, 1):
            analisis.ranking = i
        
        db.add_all(analisis_list)
        db.commit()
        
        return analisis_list
    
    @staticmethod
    def generar_proyeccion_financiera(
        db: Session,
        reporte_id: int,
        tipo_proyeccion: str,
        horizonte_meses: int,
        metodo_calculo: str,
        periodo_historico_desde: date,
        periodo_historico_hasta: date
    ) -> ProyeccionFinanciera:
        """Genera una proyección financiera"""
        # Obtener datos históricos
        datos_historicos = ReporteFinancieroService._obtener_datos_historicos(
            db, tipo_proyeccion, periodo_historico_desde, periodo_historico_hasta
        )
        
        # Calcular tendencia
        tendencia = ReporteFinancieroService._calcular_tendencia(datos_historicos, metodo_calculo)
        
        # Generar proyecciones
        proyecciones = ReporteFinancieroService._generar_proyecciones(
            datos_historicos, tendencia, horizonte_meses
        )
        
        # Crear proyección financiera
        proyeccion = ProyeccionFinanciera(
            reporte_id=reporte_id,
            tipo_proyeccion=tipo_proyeccion,
            horizonte_meses=horizonte_meses,
            metodo_calculo=metodo_calculo,
            periodo_historico_desde=periodo_historico_desde,
            periodo_historico_hasta=periodo_historico_hasta,
            valor_historico_promedio=sum(datos_historicos) / len(datos_historicos) if datos_historicos else 0.0,
            tendencia_porcentaje=tendencia,
            proyeccion_mes_1=proyecciones.get(1),
            proyeccion_mes_2=proyecciones.get(2),
            proyeccion_mes_3=proyecciones.get(3),
            proyeccion_mes_6=proyecciones.get(6),
            proyeccion_mes_12=proyecciones.get(12),
            confianza_porcentaje=80.0,
            margen_error=abs(tendencia) * 0.1  # 10% del valor de tendencia como margen de error
        )
        
        db.add(proyeccion)
        db.commit()
        db.refresh(proyeccion)
        
        return proyeccion
    
    @staticmethod
    def obtener_dashboard_financiero(db: Session) -> DashboardFinanciero:
        """Obtiene el dashboard financiero en tiempo real"""
        # Obtener datos del mes actual
        hoy = date.today()
        inicio_mes_actual = hoy.replace(day=1)
        inicio_mes_anterior = (inicio_mes_actual - timedelta(days=1)).replace(day=1)
        fin_mes_anterior = inicio_mes_actual - timedelta(days=1)
        
        # Datos del mes actual
        datos_actual = ReporteFinancieroService._obtener_datos_periodo(db, inicio_mes_actual, hoy)
        datos_anterior = ReporteFinancieroService._obtener_datos_periodo(db, inicio_mes_anterior, fin_mes_anterior)
        
        # Calcular métricas principales
        ingresos_actual = datos_actual.get('ingresos', 0.0)
        ingresos_anterior = datos_anterior.get('ingresos', 0.0)
        crecimiento_ingresos = ((ingresos_actual - ingresos_anterior) / ingresos_anterior * 100) if ingresos_anterior > 0 else 0.0
        
        costos_actual = datos_actual.get('costos', 0.0)
        costos_anterior = datos_anterior.get('costos', 0.0)
        crecimiento_costos = ((costos_actual - costos_anterior) / costos_anterior * 100) if costos_anterior > 0 else 0.0
        
        utilidad_actual = ingresos_actual - costos_actual
        utilidad_anterior = ingresos_anterior - costos_anterior
        crecimiento_utilidad = ((utilidad_actual - utilidad_anterior) / utilidad_anterior * 100) if utilidad_anterior > 0 else 0.0
        
        # Calcular ratios
        margen_bruto = (utilidad_actual / ingresos_actual * 100) if ingresos_actual > 0 else 0.0
        margen_neto = (utilidad_actual / ingresos_actual * 100) if ingresos_actual > 0 else 0.0
        
        # Obtener top performers
        top_productos = ReporteFinancieroService._obtener_top_productos_rentables(db, inicio_mes_actual, hoy)
        top_clientes = ReporteFinancieroService._obtener_top_clientes_rentables(db, inicio_mes_actual, hoy)
        top_categorias = ReporteFinancieroService._obtener_top_categorias_rentables(db, inicio_mes_actual, hoy)
        
        # Generar alertas
        alertas = ReporteFinancieroService._generar_alertas_financieras(
            ingresos_actual, costos_actual, utilidad_actual, margen_bruto
        )
        
        return DashboardFinanciero(
            ingresos_mes_actual=ingresos_actual,
            ingresos_mes_anterior=ingresos_anterior,
            crecimiento_ingresos=crecimiento_ingresos,
            costos_mes_actual=costos_actual,
            costos_mes_anterior=costos_anterior,
            crecimiento_costos=crecimiento_costos,
            utilidad_neta_mes=utilidad_actual,
            utilidad_neta_anterior=utilidad_anterior,
            crecimiento_utilidad=crecimiento_utilidad,
            margen_bruto=margen_bruto,
            margen_neto=margen_neto,
            rotacion_inventario=0.0,  # Se calcularía con datos reales
            dias_cobro_promedio=0.0,  # Se calcularía con datos reales
            dias_pago_promedio=0.0,   # Se calcularía con datos reales
            proyeccion_ventas_3_meses=0.0,  # Se calcularía con proyecciones
            proyeccion_utilidad_3_meses=0.0,  # Se calcularía con proyecciones
            tendencia_crecimiento="creciente" if crecimiento_ingresos > 0 else "decreciente" if crecimiento_ingresos < 0 else "estable",
            alertas=alertas,
            top_productos_rentables=top_productos,
            top_clientes_rentables=top_clientes,
            categorias_mas_rentables=top_categorias
        )
    
    # === MÉTODOS AUXILIARES PRIVADOS ===
    
    @staticmethod
    def _obtener_datos_ventas(db: Session, periodo_desde: date, periodo_hasta: date) -> Dict[str, float]:
        """Obtiene datos de ventas para un período"""
        # Simulación de datos - en implementación real se consultaría la base de datos
        return {
            'ventas_brutas': 100000.0,
            'descuentos': 5000.0,
            'devoluciones': 2000.0
        }
    
    @staticmethod
    def _obtener_datos_costos(db: Session, periodo_desde: date, periodo_hasta: date) -> Dict[str, float]:
        """Obtiene datos de costos para un período"""
        # Simulación de datos - en implementación real se consultaría la base de datos
        return {
            'inventario_inicial': 10000.0,
            'compras': 60000.0,
            'inventario_final': 8000.0
        }
    
    @staticmethod
    def _obtener_datos_gastos(db: Session, periodo_desde: date, periodo_hasta: date) -> Dict[str, float]:
        """Obtiene datos de gastos para un período"""
        # Simulación de datos - en implementación real se consultaría la base de datos
        return {
            'administrativos': 15000.0,
            'ventas': 10000.0,
            'generales': 5000.0,
            'otros_ingresos': 2000.0,
            'otros_gastos': 1000.0,
            'intereses': 500.0,
            'impuestos': 8000.0
        }
    
    @staticmethod
    def _obtener_datos_flujo_caja(db: Session, periodo_desde: date, periodo_hasta: date) -> Dict[str, float]:
        """Obtiene datos de flujo de caja para un período"""
        # Simulación de datos - en implementación real se consultaría la base de datos
        return {
            'ingresos_operativos': 95000.0,
            'pagos_proveedores': 55000.0,
            'pagos_empleados': 25000.0,
            'pagos_impuestos': 8000.0,
            'otros_pagos_operativos': 5000.0,
            'compras_activos': 10000.0,
            'ventas_activos': 2000.0,
            'inversiones': 5000.0,
            'prestamos_recibidos': 20000.0,
            'pagos_prestamos': 5000.0,
            'dividendos_pagados': 3000.0,
            'saldo_caja_inicial': 50000.0
        }
    
    @staticmethod
    def _obtener_datos_periodo(db: Session, periodo_desde: date, periodo_hasta: date) -> Dict[str, float]:
        """Obtiene datos consolidados para un período"""
        # Simulación de datos - en implementación real se consultaría la base de datos
        return {
            'ingresos': 100000.0,
            'costos': 70000.0,
            'gastos': 20000.0
        }
    
    @staticmethod
    def _obtener_productos_rentabilidad(db: Session, periodo_desde: date, periodo_hasta: date) -> List[Dict[str, Any]]:
        """Obtiene productos para análisis de rentabilidad"""
        # Simulación de datos - en implementación real se consultaría la base de datos
        return [
            {'id': 1, 'nombre': 'Producto A'},
            {'id': 2, 'nombre': 'Producto B'},
            {'id': 3, 'nombre': 'Producto C'}
        ]
    
    @staticmethod
    def _obtener_clientes_rentabilidad(db: Session, periodo_desde: date, periodo_hasta: date) -> List[Dict[str, Any]]:
        """Obtiene clientes para análisis de rentabilidad"""
        # Simulación de datos - en implementación real se consultaría la base de datos
        return [
            {'id': 1, 'nombre': 'Cliente A'},
            {'id': 2, 'nombre': 'Cliente B'},
            {'id': 3, 'nombre': 'Cliente C'}
        ]
    
    @staticmethod
    def _obtener_categorias_rentabilidad(db: Session, periodo_desde: date, periodo_hasta: date) -> List[Dict[str, Any]]:
        """Obtiene categorías para análisis de rentabilidad"""
        # Simulación de datos - en implementación real se consultaría la base de datos
        return [
            {'id': 1, 'nombre': 'Categoría A'},
            {'id': 2, 'nombre': 'Categoría B'},
            {'id': 3, 'nombre': 'Categoría C'}
        ]
    
    @staticmethod
    def _calcular_rentabilidad_producto(
        db: Session, reporte_id: int, producto: Dict[str, Any], 
        periodo_desde: date, periodo_hasta: date
    ) -> AnalisisRentabilidad:
        """Calcula rentabilidad de un producto"""
        # Simulación de cálculo - en implementación real se consultaría la base de datos
        ingresos = 10000.0
        costos = 7000.0
        utilidad_bruta = ingresos - costos
        margen_bruto = (utilidad_bruta / ingresos * 100) if ingresos > 0 else 0.0
        
        return AnalisisRentabilidad(
            reporte_id=reporte_id,
            tipo_entidad="producto",
            entidad_id=producto['id'],
            entidad_nombre=producto['nombre'],
            ingresos_totales=ingresos,
            costos_totales=costos,
            utilidad_bruta=utilidad_bruta,
            margen_bruto_porcentaje=margen_bruto,
            costo_productos=costos * 0.8,
            costo_mano_obra=costos * 0.15,
            costo_overhead=costos * 0.05,
            costo_marketing=0.0,
            cantidad_vendida=100.0,
            precio_promedio=ingresos / 100.0,
            ticket_promedio=ingresos / 100.0,
            periodo_desde=periodo_desde,
            periodo_hasta=periodo_hasta
        )
    
    @staticmethod
    def _calcular_rentabilidad_cliente(
        db: Session, reporte_id: int, cliente: Dict[str, Any], 
        periodo_desde: date, periodo_hasta: date
    ) -> AnalisisRentabilidad:
        """Calcula rentabilidad de un cliente"""
        # Simulación de cálculo - en implementación real se consultaría la base de datos
        ingresos = 15000.0
        costos = 10000.0
        utilidad_bruta = ingresos - costos
        margen_bruto = (utilidad_bruta / ingresos * 100) if ingresos > 0 else 0.0
        
        return AnalisisRentabilidad(
            reporte_id=reporte_id,
            tipo_entidad="cliente",
            entidad_id=cliente['id'],
            entidad_nombre=cliente['nombre'],
            ingresos_totales=ingresos,
            costos_totales=costos,
            utilidad_bruta=utilidad_bruta,
            margen_bruto_porcentaje=margen_bruto,
            costo_productos=costos * 0.8,
            costo_mano_obra=costos * 0.15,
            costo_overhead=costos * 0.05,
            costo_marketing=0.0,
            cantidad_vendida=50.0,
            precio_promedio=ingresos / 50.0,
            ticket_promedio=ingresos / 50.0,
            periodo_desde=periodo_desde,
            periodo_hasta=periodo_hasta
        )
    
    @staticmethod
    def _calcular_rentabilidad_categoria(
        db: Session, reporte_id: int, categoria: Dict[str, Any], 
        periodo_desde: date, periodo_hasta: date
    ) -> AnalisisRentabilidad:
        """Calcula rentabilidad de una categoría"""
        # Simulación de cálculo - en implementación real se consultaría la base de datos
        ingresos = 25000.0
        costos = 18000.0
        utilidad_bruta = ingresos - costos
        margen_bruto = (utilidad_bruta / ingresos * 100) if ingresos > 0 else 0.0
        
        return AnalisisRentabilidad(
            reporte_id=reporte_id,
            tipo_entidad="categoria",
            entidad_id=categoria['id'],
            entidad_nombre=categoria['nombre'],
            ingresos_totales=ingresos,
            costos_totales=costos,
            utilidad_bruta=utilidad_bruta,
            margen_bruto_porcentaje=margen_bruto,
            costo_productos=costos * 0.8,
            costo_mano_obra=costos * 0.15,
            costo_overhead=costos * 0.05,
            costo_marketing=0.0,
            cantidad_vendida=200.0,
            precio_promedio=ingresos / 200.0,
            ticket_promedio=ingresos / 200.0,
            periodo_desde=periodo_desde,
            periodo_hasta=periodo_hasta
        )
    
    @staticmethod
    def _obtener_datos_historicos(
        db: Session, tipo_proyeccion: str, periodo_desde: date, periodo_hasta: date
    ) -> List[float]:
        """Obtiene datos históricos para proyecciones"""
        # Simulación de datos históricos - en implementación real se consultaría la base de datos
        return [10000.0, 11000.0, 12000.0, 11500.0, 13000.0, 12500.0, 14000.0, 13500.0, 15000.0, 14500.0, 16000.0, 15500.0]
    
    @staticmethod
    def _calcular_tendencia(datos: List[float], metodo: str) -> float:
        """Calcula la tendencia de los datos"""
        if len(datos) < 2:
            return 0.0
        
        if metodo == "tendencia":
            # Regresión lineal simple
            n = len(datos)
            x = list(range(n))
            y = datos
            
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(x[i] * y[i] for i in range(n))
            sum_x2 = sum(x[i] ** 2 for i in range(n))
            
            pendiente = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
            return pendiente
        
        elif metodo == "estacional":
            # Análisis estacional
            if len(datos) >= 12:
                # Calcular promedio de cada mes
                promedios_mensuales = []
                for i in range(12):
                    valores_mes = [datos[j] for j in range(i, len(datos), 12)]
                    if valores_mes:
                        promedios_mensuales.append(sum(valores_mes) / len(valores_mes))
                
                if promedios_mensuales:
                    promedio_general = sum(promedios_mensuales) / len(promedios_mensuales)
                    return (promedios_mensuales[-1] - promedio_general) / promedio_general * 100
        
        return 0.0
    
    @staticmethod
    def _generar_proyecciones(datos: List[float], tendencia: float, horizonte: int) -> Dict[int, float]:
        """Genera proyecciones basadas en tendencia"""
        if not datos:
            return {}
        
        valor_base = datos[-1]  # Último valor conocido
        proyecciones = {}
        
        for mes in range(1, min(horizonte + 1, 13)):  # Máximo 12 meses
            proyeccion = valor_base * (1 + tendencia / 100) ** mes
            proyecciones[mes] = proyeccion
        
        return proyecciones
    
    @staticmethod
    def _obtener_top_productos_rentables(db: Session, periodo_desde: date, periodo_hasta: date) -> List[Dict[str, Any]]:
        """Obtiene top productos más rentables"""
        # Simulación de datos - en implementación real se consultaría la base de datos
        return [
            {'nombre': 'Producto A', 'margen': 35.5, 'ventas': 50000.0},
            {'nombre': 'Producto B', 'margen': 28.2, 'ventas': 35000.0},
            {'nombre': 'Producto C', 'margen': 22.8, 'ventas': 25000.0}
        ]
    
    @staticmethod
    def _obtener_top_clientes_rentables(db: Session, periodo_desde: date, periodo_hasta: date) -> List[Dict[str, Any]]:
        """Obtiene top clientes más rentables"""
        # Simulación de datos - en implementación real se consultaría la base de datos
        return [
            {'nombre': 'Cliente A', 'margen': 40.2, 'ventas': 75000.0},
            {'nombre': 'Cliente B', 'margen': 32.8, 'ventas': 60000.0},
            {'nombre': 'Cliente C', 'margen': 28.5, 'ventas': 45000.0}
        ]
    
    @staticmethod
    def _obtener_top_categorias_rentables(db: Session, periodo_desde: date, periodo_hasta: date) -> List[Dict[str, Any]]:
        """Obtiene top categorías más rentables"""
        # Simulación de datos - en implementación real se consultaría la base de datos
        return [
            {'nombre': 'Categoría A', 'margen': 38.5, 'ventas': 120000.0},
            {'nombre': 'Categoría B', 'margen': 30.2, 'ventas': 95000.0},
            {'nombre': 'Categoría C', 'margen': 25.8, 'ventas': 80000.0}
        ]
    
    @staticmethod
    def _generar_alertas_financieras(
        ingresos: float, costos: float, utilidad: float, margen_bruto: float
    ) -> List[Dict[str, Any]]:
        """Genera alertas financieras basadas en métricas"""
        alertas = []
        
        if margen_bruto < 20.0:
            alertas.append({
                'tipo': 'warning',
                'mensaje': f'Margen bruto bajo: {margen_bruto:.1f}%',
                'accion': 'Revisar costos y precios'
            })
        
        if utilidad < 0:
            alertas.append({
                'tipo': 'error',
                'mensaje': 'Pérdidas operativas detectadas',
                'accion': 'Revisar estrategia de precios y costos'
            })
        
        if costos > ingresos * 0.8:
            alertas.append({
                'tipo': 'warning',
                'mensaje': 'Costos representan más del 80% de los ingresos',
                'accion': 'Optimizar estructura de costos'
            })
        
        return alertas

