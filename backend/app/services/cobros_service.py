# app/services/cobros_service.py
"""
Servicio para gestión de cobros y cálculo de saldos
"""

from decimal import Decimal
from typing import Optional, Any
from datetime import datetime
from fastapi import HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.cobro_model import Cobro, MedioCobro, EstadoCobro
from app.models.venta_model import Venta
from app.models.cliente_model import Cliente
from app.models.auditoria import AuditAction
from app.services.auditoria_service import create_audit_log, get_client_ip


def crear_cobro(
    db: Session,
    venta_id: int,
    medio: str,
    importe: float,
    referencia: Optional[str] = None,
    observaciones: Optional[str] = None,
    user: Optional[Any] = None,
    request: Optional[Request] = None,
) -> Cobro:
    """
    Crea un cobro para una venta.
    
    Args:
        db: Sesión de base de datos
        venta_id: ID de la venta
        medio: Medio de cobro (EFECTIVO, TRANSFERENCIA, etc.)
        importe: Importe cobrado
        referencia: Referencia (nro de transferencia, MP, etc.)
        observaciones: Observaciones adicionales
        user: Usuario que crea el cobro
        request: Request object para auditoría
    
    Returns:
        Cobro creado
    """
    # Validar venta existe
    venta = db.query(Venta).filter(Venta.id == venta_id).first()
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    
    # Validar importe > 0
    if importe <= 0:
        raise HTTPException(status_code=400, detail="El importe debe ser mayor a 0")
    
    # Validar medio de cobro
    try:
        medio_enum = MedioCobro(medio)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Medio de cobro inválido: {medio}")
    
    # Crear cobro
    cobro = Cobro(
        venta_id=venta_id,
        medio=medio_enum,
        importe=Decimal(str(importe)),
        referencia=referencia,
        observaciones=observaciones,
        estado=EstadoCobro.CONFIRMADO,
        user_id=getattr(user, "id", None) if user else None,
    )
    
    db.add(cobro)
    
    # Auditoría
    try:
        create_audit_log(
            db,
            user_id=getattr(user, "id", None) if user else None,
            username=getattr(user, "username", None) if user else None,
            table_name="cobros",
            action=AuditAction.CREATE,
            record_id=None,  # Se setea después del flush
            details={
                "venta_id": venta_id,
                "medio": medio,
                "importe": float(importe),
                "referencia": referencia,
            },
            path=request.url.path if request else None,
            method=request.method if request else None,
            ip=get_client_ip(request) if request else None,
        )
    except Exception as e:
        print(f"[auditoria] Error al registrar creación de cobro: {e}")
    
    db.commit()
    db.refresh(cobro)
    
    return cobro


def anular_cobro(
    db: Session,
    cobro_id: int,
    user: Optional[Any] = None,
    request: Optional[Request] = None,
) -> Cobro:
    """
    Anula un cobro (no lo borra, lo marca como ANULADO).
    
    Args:
        db: Sesión de base de datos
        cobro_id: ID del cobro a anular
        user: Usuario que anula el cobro
        request: Request object para auditoría
    
    Returns:
        Cobro anulado
    """
    cobro = db.query(Cobro).filter(Cobro.id == cobro_id).first()
    if not cobro:
        raise HTTPException(status_code=404, detail="Cobro no encontrado")
    
    if cobro.estado == EstadoCobro.ANULADO:
        raise HTTPException(status_code=400, detail="El cobro ya está anulado")
    
    # Marcar como anulado
    cobro.estado = EstadoCobro.ANULADO
    
    # Auditoría
    try:
        create_audit_log(
            db,
            user_id=getattr(user, "id", None) if user else None,
            username=getattr(user, "username", None) if user else None,
            table_name="cobros",
            action=AuditAction.UPDATE,
            record_id=str(cobro.id),
            details={
                "action": "ANULAR",
                "venta_id": cobro.venta_id,
                "importe": float(cobro.importe),
            },
            path=request.url.path if request else None,
            method=request.method if request else None,
            ip=get_client_ip(request) if request else None,
        )
    except Exception as e:
        print(f"[auditoria] Error al registrar anulación de cobro: {e}")
    
    db.commit()
    db.refresh(cobro)
    
    return cobro


def get_saldo_venta(db: Session, venta_id: int) -> float:
    """
    Calcula el saldo pendiente de una venta.
    Saldo = Total Venta - Suma(Cobros Confirmados)
    
    Args:
        db: Sesión de base de datos
        venta_id: ID de la venta
    
    Returns:
        Saldo pendiente (puede ser 0 si está totalmente cobrado)
    """
    venta = db.query(Venta).filter(Venta.id == venta_id).first()
    if not venta:
        return 0.0
    
    total_venta = float(venta.total)
    
    # Sumar cobros confirmados
    total_cobrado = db.query(func.sum(Cobro.importe)).filter(
        Cobro.venta_id == venta_id,
        Cobro.estado == EstadoCobro.CONFIRMADO
    ).scalar() or 0.0
    
    saldo = total_venta - float(total_cobrado)
    
    return max(0.0, saldo)  # No retornar saldos negativos


def get_saldo_cliente(db: Session, cliente_id: int) -> float:
    """
    Calcula el saldo total pendiente de un cliente.
    Suma los saldos de todas sus ventas.
    
    Args:
        db: Sesión de base de datos
        cliente_id: ID del cliente
    
    Returns:
        Saldo total pendiente del cliente
    """
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        return 0.0
    
    # Obtener todas las ventas del cliente
    ventas = db.query(Venta).filter(Venta.cliente_id == cliente_id).all()
    
    saldo_total = 0.0
    for venta in ventas:
        saldo_total += get_saldo_venta(db, venta.id)
    
    return saldo_total


def get_cuentas_corrientes(db: Session, cliente_id: Optional[int] = None, desde: Optional[str] = None, hasta: Optional[str] = None):
    """
    Genera reporte de cuentas corrientes: movimientos (ventas=débitos, cobros=créditos) + saldo.
    v0.9.1
    """
    movimientos = []
    
    # Parsear fechas string a datetime para comparaciones SQL correctas
    desde_dt = None
    hasta_dt = None
    if desde:
        try:
            desde_dt = datetime.fromisoformat(desde.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            # Fallback: intentar formato simple YYYY-MM-DD
            try:
                desde_dt = datetime.strptime(desde[:10], "%Y-%m-%d") if len(desde) >= 10 else None
            except:
                desde_dt = None
    
    if hasta:
        try:
            hasta_dt = datetime.fromisoformat(hasta.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            try:
                hasta_dt = datetime.strptime(hasta[:10], "%Y-%m-%d") if len(hasta) >= 10 else None
            except:
                hasta_dt = None
    
    # Construir query base para ventas
    query_ventas = db.query(Venta).join(Cliente)
    if cliente_id:
        query_ventas = query_ventas.filter(Venta.cliente_id == cliente_id)
    if desde_dt:
        query_ventas = query_ventas.filter(Venta.created_at >= desde_dt)
    if hasta_dt:
        query_ventas = query_ventas.filter(Venta.created_at <= hasta_dt)
    
    ventas = query_ventas.all()
    
    for venta in ventas:
        saldo_venta = get_saldo_venta(db, venta.id)
        movimientos.append({
            "fecha": venta.created_at.strftime("%Y-%m-%d %H:%M:%S") if venta.created_at else "",
            "cliente_id": venta.cliente_id,
            "cliente_nombre": venta.cliente.nombre if venta.cliente else "N/A",
            "tipo": "VENTA",
            "referencia": f"Venta #{venta.id}",
            "debito": float(venta.total),
            "credito": 0,
            "saldo": float(saldo_venta),
        })
    
    # Construir query base para cobros
    query_cobros = db.query(Cobro).join(Venta).join(Cliente)
    if cliente_id:
        query_cobros = query_cobros.filter(Venta.cliente_id == cliente_id)
    if desde_dt:
        query_cobros = query_cobros.filter(Cobro.created_at >= desde_dt)
    if hasta_dt:
        query_cobros = query_cobros.filter(Cobro.created_at <= hasta_dt)
    query_cobros = query_cobros.filter(Cobro.estado == EstadoCobro.CONFIRMADO)
    
    cobros = query_cobros.all()
    
    for cobro in cobros:
        movimientos.append({
            "fecha": cobro.created_at.strftime("%Y-%m-%d %H:%M:%S") if cobro.created_at else "",
            "cliente_id": cobro.venta.cliente_id,
            "cliente_nombre": cobro.venta.cliente.nombre if cobro.venta.cliente else "N/A",
            "tipo": "COBRO",
            "referencia": f"Cobro #{cobro.id} (Venta #{cobro.venta_id})",
            "debito": 0,
            "credito": float(cobro.importe),
            "saldo": 0,  # Se calcula al final
        })
    
    # Ordenar por fecha
    movimientos.sort(key=lambda x: x["fecha"])
    
    # Calcular saldo acumulado si es por cliente
    if cliente_id:
        saldo_acum = 0
        for mov in movimientos:
            saldo_acum += mov["debito"] - mov["credito"]
            mov["saldo"] = saldo_acum
    
    return movimientos
