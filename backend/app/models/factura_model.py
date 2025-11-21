# app/models/factura_model.py
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum, func, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class TipoComprobante(enum.Enum):
    """Tipos de comprobante según AFIP"""
    FACTURA_A = 1
    FACTURA_B = 6
    FACTURA_C = 11
    NOTA_CREDITO_A = 3
    NOTA_CREDITO_B = 8
    NOTA_CREDITO_C = 13
    NOTA_DEBITO_A = 2
    NOTA_DEBITO_B = 7
    NOTA_DEBITO_C = 12


class TipoDocumento(enum.Enum):
    """Tipos de documento según AFIP"""
    CUIT = 80
    CUIL = 86
    CDI = 87
    LE = 89
    LC = 90
    CI_EXTRANJERA = 91
    EN_TRAMITE = 92
    ACTA_NACIMIENTO = 93
    CI_BS_AS_RNP = 95
    DNI = 96
    PASAPORTE = 94
    CI_POLICIA_FEDERAL = 0
    CI_BUENOS_AIRES = 1
    CI_CATAMARCA = 2
    CONSUMIDOR_FINAL = 99


class ConceptoFactura(enum.Enum):
    """Concepto del comprobante"""
    PRODUCTOS = 1
    SERVICIOS = 2
    PRODUCTOS_Y_SERVICIOS = 3


class ResultadoAFIP(enum.Enum):
    """Resultado de la solicitud a AFIP"""
    APROBADO = "A"
    RECHAZADO = "R"
    OBSERVADO = "O"  # Puede tener observaciones pero estar aprobado


class AlicuotaIVA(enum.Enum):
    """Alícuotas de IVA"""
    IVA_0 = 0.0
    IVA_10_5 = 10.5
    IVA_21 = 21.0
    IVA_27 = 27.0


class Factura(Base):
    __tablename__ = "facturas"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Vinculación con Venta o Pedido (al menos uno)
    venta_id = Column(Integer, ForeignKey("ventas.id", ondelete="SET NULL"), nullable=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Datos del comprobante AFIP
    tipo_cbte = Column(Integer, nullable=False, index=True)  # 1=A, 6=B, 11=C
    pto_vta = Column(Integer, nullable=False, index=True)
    nro_cbte = Column(Integer, nullable=False)
    
    # Concepto
    concepto = Column(Integer, default=1, nullable=False)  # 1=Productos, 2=Servicios, 3=Mixto
    
    # Documento del receptor
    doc_tipo = Column(Integer, nullable=False)  # 80=CUIT, 96=DNI, 99=CF
    doc_nro = Column(String, nullable=False)
    
    # Importes
    imp_neto = Column(Numeric(12, 2), nullable=False)
    imp_iva = Column(Numeric(12, 2), default=0, nullable=False)
    imp_total = Column(Numeric(12, 2), nullable=False)
    imp_exento = Column(Numeric(12, 2), default=0, nullable=False)
    
    # Moneda y cotización
    moneda = Column(String(3), default="ARS", nullable=False)
    cotiz = Column(Numeric(10, 3), default=1.000, nullable=False)
    
    # Respuesta AFIP
    cae = Column(String(14), nullable=True, index=True)
    cae_vto = Column(String(10), nullable=True)  # Formato YYYYMMDD
    resultado = Column(String(1), nullable=True)  # A/R/O
    obs = Column(Text, nullable=True)  # Observaciones de AFIP
    
    # QR AFIP (JSON payload para generar URL)
    qr_json = Column(JSONB, nullable=True)
    
    # Relaciones
    venta = relationship("Venta", back_populates="facturas")
    pedido = relationship("Pedido", back_populates="facturas")
    items = relationship("FacturaItem", back_populates="factura", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("imp_neto >= 0", name="ck_facturas_imp_neto_pos"),
        CheckConstraint("imp_iva >= 0", name="ck_facturas_imp_iva_pos"),
        CheckConstraint("imp_total >= 0", name="ck_facturas_imp_total_pos"),
        CheckConstraint("imp_exento >= 0", name="ck_facturas_imp_exento_pos"),
        # Al menos uno de venta_id o pedido_id debe estar presente
        CheckConstraint("(venta_id IS NOT NULL) OR (pedido_id IS NOT NULL)", name="ck_facturas_origen"),
    )


class FacturaItem(Base):
    __tablename__ = "factura_items"

    id = Column(Integer, primary_key=True, index=True)
    factura_id = Column(Integer, ForeignKey("facturas.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Producto (puede ser null si es un servicio o concepto sin producto en el sistema)
    producto_id = Column(Integer, ForeignKey("productos.id", ondelete="SET NULL"), nullable=True)
    descripcion = Column(String, nullable=False)
    
    # Cantidad y precios
    cantidad = Column(Numeric(10, 2), nullable=False)
    precio_unitario = Column(Numeric(12, 2), nullable=False)
    
    # Alícuota de IVA aplicada
    alic_iva = Column(Numeric(5, 2), default=21.0, nullable=False)  # 0, 10.5, 21, 27
    
    # Importes
    subtotal = Column(Numeric(12, 2), nullable=False)
    iva_monto = Column(Numeric(12, 2), default=0, nullable=False)
    
    # Relaciones
    factura = relationship("Factura", back_populates="items")
    producto = relationship("Producto")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="ck_factura_items_cantidad_pos"),
        CheckConstraint("precio_unitario >= 0", name="ck_factura_items_precio_pos"),
        CheckConstraint("alic_iva >= 0", name="ck_factura_items_alic_iva_pos"),
        CheckConstraint("subtotal >= 0", name="ck_factura_items_subtotal_pos"),
        CheckConstraint("iva_monto >= 0", name="ck_factura_items_iva_monto_pos"),
    )

