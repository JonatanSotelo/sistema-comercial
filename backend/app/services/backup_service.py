# app/services/backup_service.py
import csv
import io
import os
import zipfile
from datetime import datetime, timezone
from typing import Iterable, Optional

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.db.database import SessionLocal, engine

BACKUP_DIR = settings.BACKUP_DIR
os.makedirs(BACKUP_DIR, exist_ok=True)

TABLES = [
    "users", "clientes", "proveedores", "productos",
    "stock", "compras", "ventas", "auditoria"
]

def _fetch_all_as_dicts(db: Session, table: str) -> tuple[list[str], list[dict]]:
    cols = [c["column_name"] for c in db.execute(text(
        "SELECT column_name FROM information_schema.columns WHERE table_name=:t ORDER BY ordinal_position"
    ), {"t": table}).mappings().all()]
    if not cols:
        return [], []
    rows = db.execute(text(f"SELECT * FROM {table}")).mappings().all()
    return cols, [dict(r) for r in rows]

def _write_csv(cols: list[str], rows: Iterable[dict]) -> bytes:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(cols)
    for r in rows:
        w.writerow([r.get(c) for c in cols])
    return buf.getvalue().encode("utf-8")

def create_backup_zip() -> str:
    """
    Crea un ZIP en BACKUP_DIR exportando tablas existentes.
    Auto-gestiona la sesión para poder usarse desde el scheduler.
    """
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    zip_path = os.path.join(BACKUP_DIR, f"backup-{ts}.zip")

    inspector = inspect(engine)
    existing = set(inspector.get_table_names())

    with SessionLocal() as db, zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for t in TABLES:
            if t in existing:
                cols, rows = _fetch_all_as_dicts(db, t)
                if cols:
                    zf.writestr(f"{t}.csv", _write_csv(cols, rows))

    return zip_path

def last_backup_file() -> Optional[str]:
    if not os.path.isdir(BACKUP_DIR):
        return None
    files = [f for f in os.listdir(BACKUP_DIR) if f.endswith(".zip")]
    if not files:
        return None
    files.sort(reverse=True)
    return os.path.join(BACKUP_DIR, files[0])
