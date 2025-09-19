# backend/app/schemas/permiso_schema.py
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class PermissionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    module: str = Field(..., min_length=1, max_length=50)
    action: str = Field(..., min_length=1, max_length=50)

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    module: Optional[str] = Field(None, min_length=1, max_length=50)
    action: Optional[str] = Field(None, min_length=1, max_length=50)
    is_active: Optional[bool] = None

class PermissionOut(PermissionBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class RoleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=255)

class RoleCreate(RoleBase):
    permission_ids: List[int] = Field(default_factory=list)

class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=255)
    permission_ids: Optional[List[int]] = None
    is_active: Optional[bool] = None

class RoleOut(RoleBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    permissions: List[PermissionOut] = []

    class Config:
        from_attributes = True

class UserPermissionsOut(BaseModel):
    user_id: int
    username: str
    role: str
    permissions: List[PermissionOut]
    modules_access: List[str]  # Lista de módulos a los que tiene acceso

    class Config:
        from_attributes = True

