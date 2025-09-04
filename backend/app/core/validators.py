# app/core/validators.py
from typing import Any, Dict, List
from fastapi import HTTPException, status
import re
from decimal import Decimal, InvalidOperation

class BusinessValidators:
    """Validador de reglas de negocio"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Valida formato de email"""
        if not email:
            return True  # Email opcional
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Valida formato de teléfono"""
        if not phone:
            return True  # Teléfono opcional
        # Acepta números, guiones, paréntesis y espacios
        pattern = r'^[\d\s\-\(\)\+]+$'
        return bool(re.match(pattern, phone)) and len(phone) >= 7
    
    @staticmethod
    def validate_price(price: float) -> bool:
        """Valida que el precio sea positivo"""
        return price > 0
    
    @staticmethod
    def validate_quantity(quantity: float) -> bool:
        """Valida que la cantidad sea positiva"""
        return quantity > 0
    
    @staticmethod
    def validate_decimal_precision(value: float, max_decimals: int = 2) -> bool:
        """Valida que el número decimal no tenga más de max_decimals decimales"""
        try:
            decimal_value = Decimal(str(value))
            return len(decimal_value.as_tuple().digits) - decimal_value.as_tuple().exponent <= max_decimals
        except (InvalidOperation, ValueError):
            return False
    
    @staticmethod
    def validate_string_length(text: str, min_length: int = 1, max_length: int = 255) -> bool:
        """Valida longitud de string"""
        if not text:
            return min_length == 0
        return min_length <= len(text) <= max_length
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Valida formato de username"""
        if not username:
            return False
        # Solo letras, números, guiones y guiones bajos
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, username)) and 3 <= len(username) <= 50
    
    @staticmethod
    def validate_password_strength(password: str) -> bool:
        """Valida fortaleza de contraseña"""
        if not password:
            return False
        # Al menos 8 caracteres, una mayúscula, una minúscula y un número
        if len(password) < 8:
            return False
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        return has_upper and has_lower and has_digit

def validate_product_data(data: Dict[str, Any]) -> None:
    """Valida datos de producto"""
    if not BusinessValidators.validate_string_length(data.get("nombre", ""), 1, 100):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre del producto debe tener entre 1 y 100 caracteres"
        )
    
    if not BusinessValidators.validate_price(data.get("precio", 0)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El precio debe ser mayor a 0"
        )
    
    if not BusinessValidators.validate_decimal_precision(data.get("precio", 0), 2):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El precio no puede tener más de 2 decimales"
        )

def validate_client_data(data: Dict[str, Any]) -> None:
    """Valida datos de cliente"""
    if not BusinessValidators.validate_string_length(data.get("nombre", ""), 1, 100):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre del cliente debe tener entre 1 y 100 caracteres"
        )
    
    email = data.get("email")
    if email and not BusinessValidators.validate_email(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de email inválido"
        )
    
    phone = data.get("telefono")
    if phone and not BusinessValidators.validate_phone(phone):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de teléfono inválido"
        )

def validate_supplier_data(data: Dict[str, Any]) -> None:
    """Valida datos de proveedor"""
    if not BusinessValidators.validate_string_length(data.get("nombre", ""), 1, 100):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre del proveedor debe tener entre 1 y 100 caracteres"
        )
    
    email = data.get("email")
    if email and not BusinessValidators.validate_email(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de email inválido"
        )

def validate_user_data(data: Dict[str, Any]) -> None:
    """Valida datos de usuario"""
    username = data.get("username")
    if not BusinessValidators.validate_username(username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El username debe tener entre 3 y 50 caracteres y solo contener letras, números, guiones y guiones bajos"
        )
    
    password = data.get("password")
    if password and not BusinessValidators.validate_password_strength(password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula y un número"
        )

def validate_sale_data(data: Dict[str, Any]) -> None:
    """Valida datos de venta"""
    items = data.get("items", [])
    if not items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La venta debe tener al menos un item"
        )
    
    for item in items:
        if not BusinessValidators.validate_quantity(item.get("cantidad", 0)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La cantidad debe ser mayor a 0"
            )
        
        precio_unitario = item.get("precio_unitario")
        if precio_unitario is not None:
            if not BusinessValidators.validate_price(precio_unitario):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El precio unitario debe ser mayor a 0"
                )
            
            if not BusinessValidators.validate_decimal_precision(precio_unitario, 2):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El precio unitario no puede tener más de 2 decimales"
                )

def validate_purchase_data(data: Dict[str, Any]) -> None:
    """Valida datos de compra"""
    items = data.get("items", [])
    if not items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La compra debe tener al menos un item"
        )
    
    for item in items:
        if not BusinessValidators.validate_quantity(item.get("cantidad", 0)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La cantidad debe ser mayor a 0"
            )
        
        costo_unitario = item.get("costo_unitario", 0)
        if not BusinessValidators.validate_price(costo_unitario):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El costo unitario debe ser mayor a 0"
            )
        
        if not BusinessValidators.validate_decimal_precision(costo_unitario, 2):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El costo unitario no puede tener más de 2 decimales"
            )
