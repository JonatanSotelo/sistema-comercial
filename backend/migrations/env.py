import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# === Asegurar que /app (repo root) esté en sys.path ===
# migrations/env.py -> migrations/ .. -> /app
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# === Importar metadata de tus modelos ===
from app.db.database import Base
import app.db.base  # importa todos los modelos para que Alembic los registre

# This is the Alembic Config object, which provides access to the values within the .ini file.
config = context.config

# Logging (opcional, si tenés fileConfig en alembic.ini)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Permite override de la URL por variable de entorno (compose)
db_url = os.getenv("DATABASE_URL")
if db_url:
    config.set_main_option("sqlalchemy.url", db_url)

target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
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
