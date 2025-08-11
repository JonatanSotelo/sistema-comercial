from __future__ import annotations
import os
from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool
from dotenv import load_dotenv

# Cargar .env para obtener DATABASE_URL
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Config de Alembic
config = context.config

# Setear la URL solo si la tenemos (sobrescribe alembic.ini)
if DATABASE_URL:
    # Acepta algo tipo: postgresql+psycopg2://user:pass@host:port/db
    config.set_main_option("sqlalchemy.url", DATABASE_URL)
else:
    # Evita seguir sin URL válida
    raise RuntimeError("DATABASE_URL no encontrada. Creá backend/.env con DATABASE_URL=...")

# Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Importá Base y TODOS tus modelos para autogenerate
from app.db.database import Base
from app.models.producto_model import Producto
from app.models.cliente_model import Cliente
from app.models.venta_model import Venta
from app.models.user_model import Usuario
from app.models.proveedor_model import Proveedor
from app.models.compra_model import Compra, CompraItem, StockMovimiento

target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    if not url:
        raise RuntimeError("sqlalchemy.url vacío en modo offline.")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    # ¡Importante!: usar el prefix correcto para config dict
    connectable = engine_from_config(
        config.get_section(config.config_ini_section) or {},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
