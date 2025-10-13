# backend/app/routers/permiso_router.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.deps import get_current_user, require_admin
from app.schemas.permiso_schema import (
    RoleCreate, RoleUpdate, RoleOut, 
    PermissionCreate, PermissionUpdate, PermissionOut,
    UserPermissionsOut
)
from app.services.permiso_service import permiso_service
from app.services.auditoria_service import log_action
from app.models.auditoria import AuditAction

router = APIRouter(prefix="/permisos", tags=["Permisos y Roles"])

# Endpoints para Permisos
@router.get("/permissions", response_model=List[PermissionOut])
def listar_permisos(db: Session = Depends(get_db)):
    """Listar todos los permisos disponibles"""
    return permiso_service.get_all_permissions(db)

@router.get("/permissions/module/{module}", response_model=List[PermissionOut])
def listar_permisos_por_modulo(module: str, db: Session = Depends(get_db)):
    """Listar permisos de un módulo específico"""
    return permiso_service.get_permissions_by_module(db, module)

@router.post("/permissions", response_model=PermissionOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_admin)])
def crear_permiso(
    data: PermissionCreate,
    request: Request,
    db: Session = Depends(get_db),
    admin = Depends(get_current_user),
):
    """Crear un nuevo permiso"""
    try:
        permission = permiso_service.create_permission(db, data)
        log_action(
            db,
            user=admin,
            table_name="permissions",
            action=AuditAction.CREATE,
            record_id=permission.id,
            request=request,
            after=permission,
        )
        return permission
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/permissions/{permission_id}", response_model=PermissionOut,
            dependencies=[Depends(require_admin)])
def actualizar_permiso(
    permission_id: int,
    data: PermissionUpdate,
    request: Request,
    db: Session = Depends(get_db),
    admin = Depends(get_current_user),
):
    """Actualizar un permiso existente"""
    before = permiso_service.get_permission_by_id(db, permission_id)
    if not before:
        raise HTTPException(status_code=404, detail="Permiso no encontrado")
    
    permission = permiso_service.update_permission(db, permission_id, data)
    if not permission:
        raise HTTPException(status_code=400, detail="Error al actualizar el permiso")
    
    log_action(
        db,
        user=admin,
        table_name="permissions",
        action=AuditAction.UPDATE,
        record_id=permission_id,
        request=request,
        before=before,
        after=permission,
    )
    return permission

@router.delete("/permissions/{permission_id}", status_code=204,
               dependencies=[Depends(require_admin)])
def eliminar_permiso(
    permission_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin = Depends(get_current_user),
):
    """Eliminar un permiso (desactivar)"""
    before = permiso_service.get_permission_by_id(db, permission_id)
    if not before:
        raise HTTPException(status_code=404, detail="Permiso no encontrado")
    
    success = permiso_service.delete_permission(db, permission_id)
    if not success:
        raise HTTPException(status_code=400, detail="Error al eliminar el permiso")
    
    log_action(
        db,
        user=admin,
        table_name="permissions",
        action=AuditAction.DELETE,
        record_id=permission_id,
        request=request,
        before=before,
    )

# Endpoints para Roles
@router.get("/roles", response_model=List[RoleOut])
def listar_roles(db: Session = Depends(get_db)):
    """Listar todos los roles disponibles"""
    return permiso_service.get_all_roles(db)

@router.post("/roles", response_model=RoleOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_admin)])
def crear_rol(
    data: RoleCreate,
    request: Request,
    db: Session = Depends(get_db),
    admin = Depends(get_current_user),
):
    """Crear un nuevo rol"""
    try:
        role = permiso_service.create_role(db, data)
        log_action(
            db,
            user=admin,
            table_name="roles",
            action=AuditAction.CREATE,
            record_id=role.id,
            request=request,
            after=role,
        )
        return role
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/roles/{role_id}", response_model=RoleOut,
            dependencies=[Depends(require_admin)])
def actualizar_rol(
    role_id: int,
    data: RoleUpdate,
    request: Request,
    db: Session = Depends(get_db),
    admin = Depends(get_current_user),
):
    """Actualizar un rol existente"""
    before = permiso_service.get_role_by_id(db, role_id)
    if not before:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    
    role = permiso_service.update_role(db, role_id, data)
    if not role:
        raise HTTPException(status_code=400, detail="Error al actualizar el rol")
    
    log_action(
        db,
        user=admin,
        table_name="roles",
        action=AuditAction.UPDATE,
        record_id=role_id,
        request=request,
        before=before,
        after=role,
    )
    return role

@router.delete("/roles/{role_id}", status_code=204,
               dependencies=[Depends(require_admin)])
def eliminar_rol(
    role_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin = Depends(get_current_user),
):
    """Eliminar un rol (desactivar)"""
    before = permiso_service.get_role_by_id(db, role_id)
    if not before:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    
    success = permiso_service.delete_role(db, role_id)
    if not success:
        raise HTTPException(status_code=400, detail="Error al eliminar el rol")
    
    log_action(
        db,
        user=admin,
        table_name="roles",
        action=AuditAction.DELETE,
        record_id=role_id,
        request=request,
        before=before,
    )

# Endpoints para verificación de permisos
@router.get("/user/{user_id}/permissions", response_model=UserPermissionsOut)
def obtener_permisos_usuario(
    user_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Obtener permisos de un usuario específico"""
    # Solo el propio usuario o un admin puede ver los permisos
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="No tienes permisos para ver esta información")
    
    from app.services.user_service import user_service
    user = user_service.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    permissions = permiso_service.get_user_permissions(db, user.role)
    modules_access = permiso_service.get_user_modules_access(db, user.role)
    
    return UserPermissionsOut(
        user_id=user.id,
        username=user.username,
        role=user.role,
        permissions=permissions,
        modules_access=modules_access
    )

@router.get("/check/{permission_name}")
def verificar_permiso(
    permission_name: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Verificar si el usuario actual tiene un permiso específico"""
    has_permission = permiso_service.user_has_permission(db, current_user.role, permission_name)
    return {
        "permission": permission_name,
        "has_permission": has_permission,
        "user_role": current_user.role
    }

@router.post("/initialize", status_code=200, dependencies=[Depends(require_admin)])
def inicializar_permisos_por_defecto(
    db: Session = Depends(get_db),
    admin = Depends(get_current_user),
):
    """Inicializar permisos y roles por defecto del sistema"""
    try:
        permiso_service.initialize_default_permissions(db)
        permiso_service.initialize_default_roles(db)
        return {"message": "Permisos y roles inicializados correctamente"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al inicializar: {str(e)}")




