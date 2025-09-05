# app/models/precio_model.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date
from enum import Enum as PyEnum
from app.db.database import Base

class TipoPrecio(str, PyEnum):
    """Tipos de precios dinámicos"""
    BASE = "base"  # Precio base del producto
    CLIENTE = "cliente"  # Precio específico por cliente
    VOLUMEN = "volumen"  # Precio por cantidad
    CATEGORIA = "categoria"  # Precio por categoría
    ESTACIONAL = "estacional"  # Precio por temporada
    PROMOCIONAL = "promocional"  # Precio promocional

class EstadoPrecio(str, PyEnum):
    """Estados de los precios"""
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    EXPIRADO = "expirado"
    SUSPENDIDO = "suspendido"

class PrecioProducto(Base):
    __tablename__ = "precios_producto"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False, index=True)
    
    # Configuración del precio
    tipo = Column(String(50), nullable=False, index=True)
    estado = Column(String(20), default=EstadoPrecio.ACTIVO.value, index=True)
    
    # Valores del precio
    precio_base = Column(Float, nullable=False)  # Precio base del producto
    precio_especial = Column(Float, nullable=True)  # Precio especial aplicado
    descuento_porcentaje = Column(Float, nullable=True)  # Descuento en porcentaje
    descuento_monto = Column(Float, nullable=True)  # Descuento en monto fijo
    
    # Condiciones de aplicación
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True, index=True)
    categoria_id = Column(Integer, nullable=True, index=True)  # ID de categoría
    cantidad_minima = Column(Float, nullable=True)  # Cantidad mínima para aplicar
    cantidad_maxima = Column(Float, nullable=True)  # Cantidad máxima para aplicar
    
    # Fechas de vigencia
    fecha_inicio = Column(DateTime, nullable=False, index=True)
    fecha_fin = Column(DateTime, nullable=True, index=True)
    
    # Metadatos
    nombre = Column(String(255), nullable=True)  # Nombre descriptivo del precio
    descripcion = Column(Text, nullable=True)  # Descripción del precio
    creado_por = Column(Integer, ForeignKey("users.id"), nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    activo = Column(Boolean, default=True, index=True)
    
    # Prioridad para resolución de conflictos
    prioridad = Column(Integer, default=1, index=True)  # 1=alta, 2=media, 3=baja
    
    # Relaciones
    producto = relationship("Producto", backref="precios_producto")
    cliente = relationship("Cliente", backref="precios_cliente")
    creador = relationship("User", backref="precios_creados")
    
    def __repr__(self):
        return f"<PrecioProducto(id={self.id}, producto_id={self.producto_id}, tipo='{self.tipo}', precio_especial={self.precio_especial})>"

class PrecioVolumen(Base):
    __tablename__ = "precios_volumen"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False, index=True)
    
    # Configuración del precio por volumen
    cantidad_minima = Column(Float, nullable=False, index=True)
    cantidad_maxima = Column(Float, nullable=True, index=True)
    descuento_porcentaje = Column(Float, nullable=True)
    descuento_monto = Column(Float, nullable=True)
    precio_especial = Column(Float, nullable=True)
    
    # Aplicación
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True, index=True)
    categoria_id = Column(Integer, nullable=True, index=True)
    
    # Fechas de vigencia
    fecha_inicio = Column(DateTime, nullable=False, index=True)
    fecha_fin = Column(DateTime, nullable=True, index=True)
    
    # Metadatos
    nombre = Column(String(255), nullable=True)
    descripcion = Column(Text, nullable=True)
    creado_por = Column(Integer, ForeignKey("users.id"), nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    activo = Column(Boolean, default=True, index=True)
    prioridad = Column(Integer, default=1, index=True)
    
    # Relaciones
    producto = relationship("Producto", backref="precios_volumen")
    cliente = relationship("Cliente", backref="precios_volumen_cliente")
    creador = relationship("User", backref="precios_volumen_creados")
    
    def __repr__(self):
        return f"<PrecioVolumen(id={self.id}, producto_id={self.producto_id}, cantidad_min={self.cantidad_minima}, descuento={self.descuento_porcentaje}%)>"

class PrecioCategoria(Base):
    __tablename__ = "precios_categoria"

    id = Column(Integer, primary_key=True, index=True)
    categoria_id = Column(Integer, nullable=False, index=True)
    
    # Configuración del precio por categoría
    descuento_porcentaje = Column(Float, nullable=True)
    descuento_monto = Column(Float, nullable=True)
    multiplicador = Column(Float, nullable=True)  # Multiplicador del precio base
    
    # Aplicación
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=True, index=True)
    
    # Fechas de vigencia
    fecha_inicio = Column(DateTime, nullable=False, index=True)
    fecha_fin = Column(DateTime, nullable=True, index=True)
    
    # Metadatos
    nombre = Column(String(255), nullable=True)
    descripcion = Column(Text, nullable=True)
    creado_por = Column(Integer, ForeignKey("users.id"), nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    activo = Column(Boolean, default=True, index=True)
    prioridad = Column(Integer, default=1, index=True)
    
    # Relaciones
    cliente = relationship("Cliente", backref="precios_categoria_cliente")
    producto = relationship("Producto", backref="precios_categoria_producto")
    creador = relationship("User", backref="precios_categoria_creados")
    
    def __repr__(self):
        return f"<PrecioCategoria(id={self.id}, categoria_id={self.categoria_id}, descuento={self.descuento_porcentaje}%)>"

class PrecioEstacional(Base):
    __tablename__ = "precios_estacionales"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False, index=True)
    
    # Configuración del precio estacional
    nombre_temporada = Column(String(100), nullable=False, index=True)
    descuento_porcentaje = Column(Float, nullable=True)
    descuento_monto = Column(Float, nullable=True)
    precio_especial = Column(Float, nullable=True)
    
    # Aplicación
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True, index=True)
    categoria_id = Column(Integer, nullable=True, index=True)
    
    # Fechas de vigencia
    fecha_inicio = Column(Date, nullable=False, index=True)
    fecha_fin = Column(Date, nullable=False, index=True)
    
    # Metadatos
    descripcion = Column(Text, nullable=True)
    creado_por = Column(Integer, ForeignKey("users.id"), nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    activo = Column(Boolean, default=True, index=True)
    prioridad = Column(Integer, default=1, index=True)
    
    # Relaciones
    producto = relationship("Producto", backref="precios_estacionales")
    cliente = relationship("Cliente", backref="precios_estacionales_cliente")
    creador = relationship("User", backref="precios_estacionales_creados")
    
    def __repr__(self):
        return f"<PrecioEstacional(id={self.id}, producto_id={self.producto_id}, temporada='{self.nombre_temporada}')>"

class PrecioHistorial(Base):
    __tablename__ = "precio_historial"

    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False, index=True)
    
    # Información del cambio
    tipo_cambio = Column(String(50), nullable=False, index=True)  # 'creacion', 'actualizacion', 'activacion', 'desactivacion'
    precio_anterior = Column(Float, nullable=True)
    precio_nuevo = Column(Float, nullable=True)
    descuento_anterior = Column(Float, nullable=True)
    descuento_nuevo = Column(Float, nullable=True)
    
    # Referencia al precio modificado
    precio_id = Column(Integer, nullable=True, index=True)
    precio_tabla = Column(String(50), nullable=True)  # Tabla del precio modificado
    
    # Metadatos
    motivo = Column(Text, nullable=True)
    usuario_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    fecha_cambio = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Relaciones
    producto = relationship("Producto", backref="precio_historial")
    usuario = relationship("User", backref="precio_historial_cambios")
    
    def __repr__(self):
        return f"<PrecioHistorial(id={self.id}, producto_id={self.producto_id}, tipo='{self.tipo_cambio}', fecha={self.fecha_cambio})>"

class PrecioAplicado(Base):
    __tablename__ = "precios_aplicados"

    id = Column(Integer, primary_key=True, index=True)
    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=False, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=True, index=True)
    
    # Precios aplicados
    precio_base = Column(Float, nullable=False)
    precio_final = Column(Float, nullable=False)
    descuento_aplicado = Column(Float, nullable=True)
    porcentaje_descuento = Column(Float, nullable=True)
    
    # Información del precio aplicado
    tipo_precio = Column(String(50), nullable=False, index=True)
    precio_id = Column(Integer, nullable=True, index=True)
    precio_tabla = Column(String(50), nullable=True)
    
    # Metadatos
    cantidad = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    fecha_aplicacion = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relaciones
    venta = relationship("Venta", backref="precios_aplicados")
    producto = relationship("Producto", backref="precios_aplicados")
    cliente = relationship("Cliente", backref="precios_aplicados")
    
    def __repr__(self):
        return f"<PrecioAplicado(id={self.id}, venta_id={self.venta_id}, producto_id={self.producto_id}, precio_final={self.precio_final})>"
