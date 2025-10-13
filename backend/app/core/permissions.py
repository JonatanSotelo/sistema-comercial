# backend/app/core/permissions.py
from functools import wraps
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.core.deps import get_current_user
from app.services.permiso_service import permiso_service
from app.models.user_model import User

def require_permission(permission_name: str):
    """
    Decorador para verificar que el usuario tenga un permiso específico
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Obtener el usuario actual y la base de datos
            db = None
            current_user = None
            
            # Buscar db y current_user en los argumentos
            for arg in args:
                if isinstance(arg, Session):
                    db = arg
                    break
            
            for key, value in kwargs.items():
                if key == 'db' and isinstance(value, Session):
                    db = value
                elif key == 'current_user' and isinstance(value, User):
                    current_user = value
            
            if not db or not current_user:
                raise HTTPException(status_code=500, detail="Error interno: no se pudo obtener usuario o base de datos")
            
            # Verificar si el usuario tiene el permiso
            has_permission = permiso_service.user_has_permission(db, current_user.role, permission_name)
            
            if not has_permission:
                raise HTTPException(
                    status_code=403, 
                    detail=f"No tienes permisos para realizar esta acción. Permiso requerido: {permission_name}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_any_permission(permissions: List[str]):
    """
    Decorador para verificar que el usuario tenga al menos uno de los permisos especificados
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            db = None
            current_user = None
            
            for arg in args:
                if isinstance(arg, Session):
                    db = arg
                    break
            
            for key, value in kwargs.items():
                if key == 'db' and isinstance(value, Session):
                    db = value
                elif key == 'current_user' and isinstance(value, User):
                    current_user = value
            
            if not db or not current_user:
                raise HTTPException(status_code=500, detail="Error interno: no se pudo obtener usuario o base de datos")
            
            # Verificar si el usuario tiene al menos uno de los permisos
            has_any_permission = any(
                permiso_service.user_has_permission(db, current_user.role, perm) 
                for perm in permissions
            )
            
            if not has_any_permission:
                raise HTTPException(
                    status_code=403, 
                    detail=f"No tienes permisos para realizar esta acción. Permisos requeridos: {', '.join(permissions)}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_module_access(module: str):
    """
    Decorador para verificar que el usuario tenga acceso a un módulo específico
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            db = None
            current_user = None
            
            for arg in args:
                if isinstance(arg, Session):
                    db = arg
                    break
            
            for key, value in kwargs.items():
                if key == 'db' and isinstance(value, Session):
                    db = value
                elif key == 'current_user' and isinstance(value, User):
                    current_user = value
            
            if not db or not current_user:
                raise HTTPException(status_code=500, detail="Error interno: no se pudo obtener usuario o base de datos")
            
            # Verificar si el usuario tiene acceso al módulo
            user_modules = permiso_service.get_user_modules_access(db, current_user.role)
            
            if module not in user_modules:
                raise HTTPException(
                    status_code=403, 
                    detail=f"No tienes acceso al módulo {module}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Funciones de dependencia para FastAPI
def get_permission_checker(permission_name: str):
    """
    Función de dependencia para verificar permisos en endpoints de FastAPI
    """
    def check_permission(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        has_permission = permiso_service.user_has_permission(db, current_user.role, permission_name)
        if not has_permission:
            raise HTTPException(
                status_code=403, 
                detail=f"No tienes permisos para realizar esta acción. Permiso requerido: {permission_name}"
            )
        return current_user
    return check_permission

def get_module_access_checker(module: str):
    """
    Función de dependencia para verificar acceso a módulos en endpoints de FastAPI
    """
    def check_module_access(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        user_modules = permiso_service.get_user_modules_access(db, current_user.role)
        if module not in user_modules:
            raise HTTPException(
                status_code=403, 
                detail=f"No tienes acceso al módulo {module}"
            )
        return current_user
    return check_module_access




