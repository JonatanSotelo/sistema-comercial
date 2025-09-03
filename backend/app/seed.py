# app/seed.py
from __future__ import annotations

import importlib
from typing import Any, Dict, List

from sqlalchemy.orm import Session

# ⚠️ Importá base ANTES que nada para registrar todos los modelos y relaciones
import app.db.base  # noqa: F401

from app.db.database import SessionLocal
from app.models.producto_model import Producto

# Datos base
SEED_PRODUCTS: List[Dict[str, Any]] = [
    {"nombre": "Batería UPS 12V 9Ah", "descripcion": "Batería sellada para UPS", "precio": 45.50},
    {"nombre": "Rack 19\" 12U", "descripcion": "Rack mural 12U", "precio": 210.00},
    {"nombre": "UPS Online 1kVA", "descripcion": "UPS doble conversión 1kVA", "precio": 520.00},
    {"nombre": "Cable PDU", "descripcion": "Cable para PDU de rack", "precio": 12.00},
    {"nombre": "Bandeja Rack", "descripcion": "Bandeja fija 19\"", "precio": 28.00},
]

SEED_CLIENTES: List[Dict[str, Any]] = [
    {"nombre": "Cliente Demo SA", "email": "demo@cliente.com", "telefono": "1111-1111"},
    {"nombre": "Juan Pérez", "email": "juan@example.com"},
]

SEED_PROVEEDORES: List[Dict[str, Any]] = [
    {"nombre": "Proveedor UPS SRL", "email": "ventas@proveedorups.com"},
    {"nombre": "Racks SRL", "email": "contacto@racks.com"},
]


def _safe_load_model(module_path: str, class_name: str):
    """Intenta importar un modelo. Devuelve None si no existe."""
    try:
        mod = importlib.import_module(module_path)
        return getattr(mod, class_name, None)
    except Exception:
        return None


def _insert_if_empty(db: Session, model, rows: List[Dict[str, Any]], label: str):
    count = db.query(model).count()
    if count == 0 and rows:
        for raw in rows:
            filtered = {k: v for k, v in raw.items() if hasattr(model, k)}
            db.add(model(**filtered))
        db.commit()
        print(f"[seed] Insertados {len(rows)} {label}")
    else:
        print(f"[seed] {label} ya tiene {count} registros, no se insertó nada.")


def run():
    db: Session = SessionLocal()
    try:
        _insert_if_empty(db, Producto, SEED_PRODUCTS, "productos")

        # Clientes (opcional; protegido por try/except por si faltan relaciones/tablas)
        try:
            Cliente = _safe_load_model("app.models.cliente_model", "Cliente") or \
                      _safe_load_model("app.models.cliente", "Cliente")
            if Cliente:
                _insert_if_empty(db, Cliente, SEED_CLIENTES, "clientes")
            else:
                print("[seed] Modelo Cliente no encontrado. Saltando.")
        except Exception as e:
            print(f"[seed] Saltando clientes por error de relaciones/mapeo: {e!r}")

        # Proveedores (opcional)
        try:
            Proveedor = _safe_load_model("app.models.proveedor_model", "Proveedor") or \
                        _safe_load_model("app.models.proveedor", "Proveedor")
            if Proveedor:
                _insert_if_empty(db, Proveedor, SEED_PROVEEDORES, "proveedores")
            else:
                print("[seed] Modelo Proveedor no encontrado. Saltando.")
        except Exception as e:
            print(f"[seed] Saltando proveedores por error de relaciones/mapeo: {e!r}")

        print("[seed] OK.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
