# backend/app/services/permiso_service.py
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.permiso_model import Role, Permission
from app.schemas.permiso_schema import RoleCreate, RoleUpdate, PermissionCreate, PermissionUpdate

class PermissionService:
    # Gestión de Permisos
    def create_permission(self, db: Session, permission_data: PermissionCreate) -> Permission:
        permission = Permission(**permission_data.model_dump())
        db.add(permission)
        db.commit()
        db.refresh(permission)
        return permission

    def get_permission_by_id(self, db: Session, permission_id: int) -> Optional[Permission]:
        return db.query(Permission).filter(Permission.id == permission_id).first()

    def get_all_permissions(self, db: Session) -> List[Permission]:
        return db.query(Permission).filter(Permission.is_active == True).all()

    def get_permissions_by_module(self, db: Session, module: str) -> List[Permission]:
        return db.query(Permission).filter(
            and_(Permission.module == module, Permission.is_active == True)
        ).all()

    def update_permission(self, db: Session, permission_id: int, permission_data: PermissionUpdate) -> Optional[Permission]:
        permission = self.get_permission_by_id(db, permission_id)
        if not permission:
            return None
        
        update_data = permission_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(permission, field, value)
        
        db.commit()
        db.refresh(permission)
        return permission

    def delete_permission(self, db: Session, permission_id: int) -> bool:
        permission = self.get_permission_by_id(db, permission_id)
        if not permission:
            return False
        
        permission.is_active = False
        db.commit()
        return True

    # Gestión de Roles
    def create_role(self, db: Session, role_data: RoleCreate) -> Role:
        role = Role(
            name=role_data.name,
            description=role_data.description
        )
        db.add(role)
        db.flush()  # Para obtener el ID
        
        # Asignar permisos
        if role_data.permission_ids:
            permissions = db.query(Permission).filter(
                Permission.id.in_(role_data.permission_ids)
            ).all()
            role.permissions = permissions
        
        db.commit()
        db.refresh(role)
        return role

    def get_role_by_id(self, db: Session, role_id: int) -> Optional[Role]:
        return db.query(Role).filter(Role.id == role_id).first()

    def get_role_by_name(self, db: Session, name: str) -> Optional[Role]:
        return db.query(Role).filter(Role.name == name).first()

    def get_all_roles(self, db: Session) -> List[Role]:
        return db.query(Role).filter(Role.is_active == True).all()

    def update_role(self, db: Session, role_id: int, role_data: RoleUpdate) -> Optional[Role]:
        role = self.get_role_by_id(db, role_id)
        if not role:
            return None
        
        update_data = role_data.model_dump(exclude_unset=True, exclude={'permission_ids'})
        for field, value in update_data.items():
            setattr(role, field, value)
        
        # Actualizar permisos si se proporcionan
        if role_data.permission_ids is not None:
            permissions = db.query(Permission).filter(
                Permission.id.in_(role_data.permission_ids)
            ).all()
            role.permissions = permissions
        
        db.commit()
        db.refresh(role)
        return role

    def delete_role(self, db: Session, role_id: int) -> bool:
        role = self.get_role_by_id(db, role_id)
        if not role:
            return False
        
        role.is_active = False
        db.commit()
        return True

    # Verificación de permisos
    def user_has_permission(self, db: Session, user_role: str, permission_name: str) -> bool:
        # Si es admin, tiene todos los permisos
        if user_role == "admin":
            return True
        
        # Buscar el rol y verificar si tiene el permiso
        role = self.get_role_by_name(db, user_role)
        if not role:
            return False
        
        return any(perm.name == permission_name for perm in role.permissions if perm.is_active)

    def get_user_permissions(self, db: Session, user_role: str) -> List[Permission]:
        if user_role == "admin":
            return self.get_all_permissions(db)
        
        role = self.get_role_by_name(db, user_role)
        if not role:
            return []
        
        return [perm for perm in role.permissions if perm.is_active]

    def get_user_modules_access(self, db: Session, user_role: str) -> List[str]:
        permissions = self.get_user_permissions(db, user_role)
        modules = set(perm.module for perm in permissions)
        return list(modules)

    # Inicialización de permisos por defecto
    def initialize_default_permissions(self, db: Session):
        """Inicializa los permisos por defecto del sistema"""
        default_permissions = [
            # Módulo de Ventas
            {"name": "ventas_read", "description": "Ver ventas", "module": "ventas", "action": "read"},
            {"name": "ventas_write", "description": "Crear/Editar ventas", "module": "ventas", "action": "write"},
            {"name": "ventas_delete", "description": "Eliminar ventas", "module": "ventas", "action": "delete"},
            
            # Módulo de Inventario
            {"name": "inventario_read", "description": "Ver inventario", "module": "inventario", "action": "read"},
            {"name": "inventario_write", "description": "Gestionar inventario", "module": "inventario", "action": "write"},
            {"name": "inventario_delete", "description": "Eliminar productos", "module": "inventario", "action": "delete"},
            
            # Módulo de Clientes
            {"name": "clientes_read", "description": "Ver clientes", "module": "clientes", "action": "read"},
            {"name": "clientes_write", "description": "Crear/Editar clientes", "module": "clientes", "action": "write"},
            {"name": "clientes_delete", "description": "Eliminar clientes", "module": "clientes", "action": "delete"},
            
            # Módulo de Productos
            {"name": "productos_read", "description": "Ver productos", "module": "productos", "action": "read"},
            {"name": "productos_write", "description": "Crear/Editar productos", "module": "productos", "action": "write"},
            {"name": "productos_delete", "description": "Eliminar productos", "module": "productos", "action": "delete"},
            
            # Módulo de Dashboard
            {"name": "dashboard_read", "description": "Ver dashboard", "module": "dashboard", "action": "read"},
            
            # Módulo de Usuarios
            {"name": "usuarios_read", "description": "Ver usuarios", "module": "usuarios", "action": "read"},
            {"name": "usuarios_write", "description": "Crear/Editar usuarios", "module": "usuarios", "action": "write"},
            {"name": "usuarios_delete", "description": "Eliminar usuarios", "module": "usuarios", "action": "delete"},
        ]
        
        for perm_data in default_permissions:
            existing = db.query(Permission).filter(Permission.name == perm_data["name"]).first()
            if not existing:
                permission = Permission(**perm_data)
                db.add(permission)
        
        db.commit()

    def initialize_default_roles(self, db: Session):
        """Inicializa los roles por defecto del sistema"""
        # Rol de Administrador (todos los permisos)
        admin_role = self.get_role_by_name(db, "admin")
        if not admin_role:
            all_permissions = self.get_all_permissions(db)
            admin_role = Role(
                name="admin",
                description="Administrador con acceso completo al sistema",
                permissions=all_permissions
            )
            db.add(admin_role)
        
        # Rol de Vendedor (ventas, clientes, productos, dashboard)
        vendedor_role = self.get_role_by_name(db, "vendedor")
        if not vendedor_role:
            vendedor_permissions = db.query(Permission).filter(
                Permission.module.in_(["ventas", "clientes", "productos", "dashboard"])
            ).all()
            vendedor_role = Role(
                name="vendedor",
                description="Vendedor con acceso a ventas, clientes y productos",
                permissions=vendedor_permissions
            )
            db.add(vendedor_role)
        
        # Rol de Consulta (solo lectura)
        consulta_role = self.get_role_by_name(db, "consulta")
        if not consulta_role:
            consulta_permissions = db.query(Permission).filter(
                Permission.action == "read"
            ).all()
            consulta_role = Role(
                name="consulta",
                description="Usuario con acceso de solo lectura",
                permissions=consulta_permissions
            )
            db.add(consulta_role)
        
        db.commit()

# Instancia global del servicio
permiso_service = PermissionService()




