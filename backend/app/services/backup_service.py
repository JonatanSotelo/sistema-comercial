# app/services/backup_service.py
import os
import subprocess
import gzip
import hashlib
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from pathlib import Path

from app.core.settings import settings
from app.db.database import engine

# BACKUP_DIR puede venir de env o defaults
BACKUP_DIR = os.environ.get("BACKUP_DIR", settings.BACKUP_DIR if hasattr(settings, "BACKUP_DIR") else "/data/backups")
os.makedirs(BACKUP_DIR, exist_ok=True)


def _parse_db_url(db_url: str) -> Dict[str, str]:
    """Parsea DATABASE_URL para obtener componentes"""
    # postgresql+psycopg2://user:pass@host:port/db
    if "+" in db_url:
        db_url = db_url.split("+")[-1]
    # postgresql://user:pass@host:port/db
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "")
    else:
        raise ValueError("Solo soportamos PostgreSQL")
    
    # user:pass@host:port/db
    if "@" not in db_url:
        raise ValueError("URL inválida")
    
    auth, rest = db_url.split("@", 1)
    if ":" in auth:
        user, password = auth.split(":", 1)
    else:
        user, password = auth, ""
    
    if "/" in rest:
        host_port, dbname = rest.rsplit("/", 1)
    else:
        host_port, dbname = rest, "postgres"
    
    if ":" in host_port:
        host, port = host_port.split(":", 1)
    else:
        host, port = host_port, "5432"
    
    return {
        "host": host,
        "port": port,
        "dbname": dbname,
        "user": user,
        "password": password,
    }


def create_backup_sql_gz() -> Dict[str, Any]:
    """
    Crea un backup SQL comprimido con gzip usando pg_dump.
    Devuelve metadata: filename, size, created_at, checksum sha256.
    """
    db_url = os.environ.get("DATABASE_URL", settings.DATABASE_URL)
    db_params = _parse_db_url(db_url)
    
    # Timestamp para nombre de archivo
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"backup_{ts}.sql.gz"
    filepath = os.path.join(BACKUP_DIR, filename)
    
    # Ejecutar pg_dump
    env = os.environ.copy()
    if db_params["password"]:
        env["PGPASSWORD"] = db_params["password"]
    
    cmd = [
        "pg_dump",
        "-h", db_params["host"],
        "-p", db_params["port"],
        "-U", db_params["user"],
        "-d", db_params["dbname"],
        "--no-owner",
        "--no-acl",
        "--clean",
        "--if-exists",
    ]
    
    try:
        # Ejecutar pg_dump y comprimir con gzip
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )
        
        # Comprimir con gzip
        with open(filepath, "wb") as f:
            gzip_file = gzip.open(f, "wb")
            for chunk in process.stdout:
                gzip_file.write(chunk)
            gzip_file.close()
        
        process.wait()
        
        if process.returncode != 0:
            stderr = process.stderr.read().decode("utf-8", errors="ignore")
            os.remove(filepath)
            raise RuntimeError(f"pg_dump falló: {stderr}")
        
        # Calcular metadata
        size = os.path.getsize(filepath)
        created_at = datetime.now(timezone.utc)
        
        # Calcular checksum sha256
        with open(filepath, "rb") as f:
            sha256 = hashlib.sha256(f.read()).hexdigest()
        
        return {
            "filename": filename,
            "size": size,
            "created_at": created_at.isoformat(),
            "checksum": sha256,
        }
    
    except FileNotFoundError:
        raise RuntimeError("pg_dump no encontrado. Instalá postgresql-client en el contenedor.")
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        raise RuntimeError(f"Error al crear backup: {e}")


def list_backups() -> List[Dict[str, Any]]:
    """
    Lista archivos de backup con metadata.
    """
    if not os.path.isdir(BACKUP_DIR):
        return []
    
    backups = []
    for filename in os.listdir(BACKUP_DIR):
        if filename.startswith("backup_") and filename.endswith(".sql.gz"):
            filepath = os.path.join(BACKUP_DIR, filename)
            try:
                stat = os.stat(filepath)
                size = stat.st_size
                created_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
                
                # Calcular checksum
                with open(filepath, "rb") as f:
                    sha256 = hashlib.sha256(f.read()).hexdigest()
                
                backups.append({
                    "filename": filename,
                    "size": size,
                    "created_at": created_at.isoformat(),
                    "checksum": sha256,
                })
            except Exception:
                continue
    
    # Ordenar por fecha descendente
    backups.sort(key=lambda x: x["created_at"], reverse=True)
    return backups


def get_backup_path(filename: str) -> Optional[str]:
    """Obtiene path de backup validando que exista y esté en BACKUP_DIR"""
    if not filename or ".." in filename or "/" in filename or "\\" in filename:
        return None
    filepath = os.path.join(BACKUP_DIR, filename)
    if not os.path.exists(filepath) or not filepath.startswith(BACKUP_DIR):
        return None
    return filepath


# Compatibilidad con código existente (usar ZIP como fallback si pg_dump falla)
def create_backup_zip() -> str:
    """
    Fallback: crea ZIP si pg_dump no está disponible.
    Auto-gestiona la sesión para poder usarse desde el scheduler.
    """
    try:
        result = create_backup_sql_gz()
        return os.path.join(BACKUP_DIR, result["filename"])
    except Exception as e:
        # Fallback a ZIP si pg_dump falla
        import zipfile
        from sqlalchemy import inspect, text
        from sqlalchemy.orm import Session
        from app.db.database import SessionLocal
        
        print(f"[backup] pg_dump falló, usando ZIP fallback: {e}")
        
        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        zip_path = os.path.join(BACKUP_DIR, f"backup-{ts}.zip")
        
        TABLES = [
            "users", "clientes", "proveedores", "productos",
            "stock_movimientos", "compras", "compra_items", "ventas", "venta_items", "audit_logs"
        ]
        
        inspector = inspect(engine)
        existing = set(inspector.get_table_names())
        
        with SessionLocal() as db, zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for t in TABLES:
                if t in existing:
                    try:
                        cols = [c["column_name"] for c in db.execute(text(
                            "SELECT column_name FROM information_schema.columns WHERE table_name=:t ORDER BY ordinal_position"
                        ), {"t": t}).mappings().all()]
                        if cols:
                            rows = db.execute(text(f"SELECT * FROM {t}")).mappings().all()
                            import csv, io
                            buf = io.StringIO()
                            w = csv.writer(buf)
                            w.writerow(cols)
                            for r in rows:
                                w.writerow([r.get(c) for c in cols])
                            zf.writestr(f"{t}.csv", buf.getvalue().encode("utf-8"))
                    except Exception:
                        continue
        
        return zip_path


def last_backup_file() -> Optional[str]:
    """Obtiene el último backup (SQL.GZ o ZIP)"""
    if not os.path.isdir(BACKUP_DIR):
        return None
    files = [f for f in os.listdir(BACKUP_DIR) if f.endswith((".sql.gz", ".zip")) and f.startswith("backup_")]
    if not files:
        return None
    files.sort(reverse=True)
    return os.path.join(BACKUP_DIR, files[0])
