"""fix_users_fks

Revision ID: c1d2e3f4g5h6
Revises: 00f14465c7ef
Create Date: 2025-11-21 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'c1d2e3f4g5h6'
down_revision = '00f14465c7ef'
branch_labels = None
depends_on = None


def ensure_fk_users(conn, src_table: str, src_column: str, ondelete: str = "SET NULL"):
    """
    Asegura que una FK apunte correctamente a users(id)
    Elimina cualquier FK existente y crea una nueva correcta
    """
    # Buscar constraint existente
    sql_find = sa.text("""
        SELECT conname
        FROM pg_constraint c
        JOIN pg_class r ON r.oid = c.conrelid
        JOIN pg_attribute a ON a.attrelid = r.oid AND a.attnum = ANY(c.conkey)
        WHERE c.contype='f' 
          AND r.relname=:src_table 
          AND a.attname=:src_col
          AND r.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname='public')
    """)
    
    rows = conn.execute(sql_find, {"src_table": src_table, "src_col": src_column}).fetchall()
    
    # Eliminar constraints existentes
    for (conname,) in rows:
        try:
            conn.execute(sa.text(f'ALTER TABLE "{src_table}" DROP CONSTRAINT IF EXISTS "{conname}"'))
            print(f"  Dropped constraint {conname} from {src_table}.{src_column}")
        except Exception as e:
            print(f"  Warning: Could not drop {conname}: {e}")
    
    # Crear FK correcta
    fk_name = f"fk_{src_table}_{src_column}__users_id"
    try:
        conn.execute(sa.text(
            f'ALTER TABLE "{src_table}" '
            f'ADD CONSTRAINT "{fk_name}" FOREIGN KEY ("{src_column}") '
            f'REFERENCES "users"("id") ON DELETE {ondelete}'
        ))
        print(f"  Created FK: {fk_name} ({src_table}.{src_column} -> users.id)")
    except Exception as e:
        print(f"  Warning: Could not create {fk_name}: {e}")


def upgrade() -> None:
    """
    Asegura que todas las FKs a usuarios apunten a 'users' (no 'usuarios')
    """
    conn = op.get_bind()
    
    print("Fixing Foreign Keys to users table...")
    
    # Lista de tablas/columnas que deben referenciar users(id)
    # Ajustar según el esquema real del proyecto
    fk_mappings = [
        ("audit_logs", "user_id", "SET NULL"),
        ("auditoria", "user_id", "SET NULL"),
        ("pedidos", "created_by", "SET NULL"),
        ("ventas", "user_id", "SET NULL"),
        ("compras", "user_id", "SET NULL"),
        ("stock_movimientos", "user_id", "SET NULL"),
        ("notificaciones", "user_id", "CASCADE"),
    ]
    
    for src_table, src_column, ondelete in fk_mappings:
        # Verificar si la tabla existe
        check_table = sa.text("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = :table_name
            )
        """)
        
        table_exists = conn.execute(check_table, {"table_name": src_table}).scalar()
        
        if table_exists:
            # Verificar si la columna existe
            check_column = sa.text("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                      AND table_name = :table_name 
                      AND column_name = :column_name
                )
            """)
            
            column_exists = conn.execute(check_column, {
                "table_name": src_table, 
                "column_name": src_column
            }).scalar()
            
            if column_exists:
                ensure_fk_users(conn, src_table, src_column, ondelete)
            else:
                print(f"  Skipped {src_table}.{src_column} (column not found)")
        else:
            print(f"  Skipped {src_table} (table not found)")
    
    print("Foreign Keys fixed successfully!")


def downgrade() -> None:
    """
    No downgrade - mantener FKs correctas
    """
    pass

