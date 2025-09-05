"""add_notificaciones_manual

Revision ID: e8e18a9dcd38
Revises: c544a0180d0b
Create Date: 2025-09-05 18:30:47.812846

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e8e18a9dcd38'
down_revision: Union[str, Sequence[str], None] = 'c544a0180d0b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Crear enum para tipos de notificación
    op.execute("CREATE TYPE tiponotificacion AS ENUM ('stock_bajo', 'venta_importante', 'sistema', 'mantenimiento', 'error', 'info', 'warning')")
    
    # Crear enum para estados de notificación
    op.execute("CREATE TYPE estadonotificacion AS ENUM ('pendiente', 'enviada', 'leida', 'archivada')")
    
    # Crear tabla notificaciones
    op.create_table('notificaciones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('titulo', sa.String(length=255), nullable=False),
        sa.Column('mensaje', sa.Text(), nullable=False),
        sa.Column('tipo', sa.Enum('stock_bajo', 'venta_importante', 'sistema', 'mantenimiento', 'error', 'info', 'warning', name='tiponotificacion'), nullable=False),
        sa.Column('estado', sa.Enum('pendiente', 'enviada', 'leida', 'archivada', name='estadonotificacion'), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=True),
        sa.Column('entidad_tipo', sa.String(length=50), nullable=True),
        sa.Column('entidad_id', sa.Integer(), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False),
        sa.Column('fecha_envio', sa.DateTime(), nullable=True),
        sa.Column('fecha_lectura', sa.DateTime(), nullable=True),
        sa.Column('es_urgente', sa.Boolean(), nullable=False),
        sa.Column('requiere_accion', sa.Boolean(), nullable=False),
        sa.Column('datos_adicionales', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Crear índices para notificaciones
    op.create_index('ix_notificaciones_id', 'notificaciones', ['id'], unique=False)
    op.create_index('ix_notificaciones_titulo', 'notificaciones', ['titulo'], unique=False)
    op.create_index('ix_notificaciones_tipo', 'notificaciones', ['tipo'], unique=False)
    op.create_index('ix_notificaciones_estado', 'notificaciones', ['estado'], unique=False)
    op.create_index('ix_notificaciones_usuario_id', 'notificaciones', ['usuario_id'], unique=False)
    op.create_index('ix_notificaciones_fecha_creacion', 'notificaciones', ['fecha_creacion'], unique=False)
    op.create_index('ix_notificaciones_es_urgente', 'notificaciones', ['es_urgente'], unique=False)
    
    # Crear tabla notificaciones_usuarios
    op.create_table('notificaciones_usuarios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('notificacion_id', sa.Integer(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=False),
        sa.Column('estado', sa.Enum('pendiente', 'enviada', 'leida', 'archivada', name='estadonotificacion'), nullable=False),
        sa.Column('fecha_lectura', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Crear índices para notificaciones_usuarios
    op.create_index('ix_notificaciones_usuarios_id', 'notificaciones_usuarios', ['id'], unique=False)
    op.create_index('ix_notificaciones_usuarios_notificacion_id', 'notificaciones_usuarios', ['notificacion_id'], unique=False)
    op.create_index('ix_notificaciones_usuarios_usuario_id', 'notificaciones_usuarios', ['usuario_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Eliminar tablas
    op.drop_table('notificaciones_usuarios')
    op.drop_table('notificaciones')
    
    # Eliminar enums
    op.execute("DROP TYPE estadonotificacion")
    op.execute("DROP TYPE tiponotificacion")
