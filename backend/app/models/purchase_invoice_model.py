# app/models/purchase_invoice_model.py
"""
Modelo minimal para Libro IVA Compras
Registro manual de facturas de compra recibidas
"""
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.orm import relationship
from app.db.database import Base


class PurchaseInvoice(Base):
    __tablename__ = "purchase_invoices"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Proveedor (opcional FK si existe, sino texto libre)
    proveedor_id = Column(Integer, ForeignKey("proveedores.id", ondelete="SET NULL"), nullable=True, index=True)
    proveedor_nombre = Column(String, nullable=True)  # Si no hay FK
    
    # Fecha de la factura
    fecha = Column(Date, nullable=False, index=True)
    
    # Datos del comprobante
    tipo_cbte = Column(Integer, nullable=False, index=True)  # 1=A, 6=B, 11=C
    pto_vta = Column(Integer, nullable=False)
    nro_cbte = Column(Integer, nullable=False)
    
    # Documento del proveedor
    doc_tipo = Column(Integer, nullable=True)  # 80=CUIT, 96=DNI, 99=CF
    doc_nro = Column(String, nullable=True)
    
    # Importes
    imp_neto = Column(Numeric(12, 2), nullable=False)
    imp_iva = Column(Numeric(12, 2), default=0, nullable=False)
    imp_exento = Column(Numeric(12, 2), default=0, nullable=False)
    imp_total = Column(Numeric(12, 2), nullable=False)
    
    # Alícuota principal (para reporte)
    alicuota_principal = Column(Numeric(5, 2), default=21.0, nullable=False)  # 0, 10.5, 21, 27
    
    # Moneda
    moneda = Column(String(3), default="ARS", nullable=False)
    cotiz = Column(Numeric(10, 3), default=1.000, nullable=False)
    
    # Link opcional a compra del sistema
    compra_id = Column(Integer, ForeignKey("compras.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Relaciones
    proveedor = relationship("Proveedor", foreign_keys=[proveedor_id])
    compra = relationship("Compra", foreign_keys=[compra_id])
    
    # Constraints
    __table_args__ = (
        CheckConstraint("imp_neto >= 0", name="ck_purchase_invoices_imp_neto_pos"),
        CheckConstraint("imp_iva >= 0", name="ck_purchase_invoices_imp_iva_pos"),
        CheckConstraint("imp_exento >= 0", name="ck_purchase_invoices_imp_exento_pos"),
        CheckConstraint("imp_total >= 0", name="ck_purchase_invoices_imp_total_pos"),
        CheckConstraint("alicuota_principal >= 0", name="ck_purchase_invoices_alic_pos"),
    )

