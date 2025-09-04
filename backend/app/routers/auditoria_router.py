# app/routers/auditoria_router.py
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.database import get_db

router = APIRouter(prefix="/auditoria", tags=["Auditoría"])

# Tabla minimal si no existe:
#   id bigserial pk
#   ts timestamptz
#   actor text
#   accion text
#   detalle jsonb

DDL_CREATE = text("""
CREATE TABLE IF NOT EXISTS auditoria (
    id BIGSERIAL PRIMARY KEY,
    ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actor TEXT,
    accion TEXT NOT NULL,
    detalle JSONB
);
""")

class AuditIn(BaseModel):
    accion: str
    actor: Optional[str] = None
    detalle: Optional[Any] = None

@router.on_event("startup")
def ensure_table():
    # Nota: en routers, este evento corre cuando el router se monta.
    # Si preferís centralizar, podés moverlo a main.py
    from app.db.database import engine
    with engine.begin() as conn:
        conn.execute(DDL_CREATE)

@router.post("", summary="Registrar evento de auditoría")
def add_event(data: AuditIn, db: Session = Depends(get_db)):
    q = text("INSERT INTO auditoria (actor, accion, detalle) VALUES (:actor, :accion, CAST(:detalle AS JSONB)) RETURNING id, ts;")
    row = db.execute(q, {
        "actor": data.actor,
        "accion": data.accion,
        "detalle": None if data.detalle is None else str(data.detalle).replace("'", '"')
    }).first()
    db.commit()
    return {"id": row.id, "ts": row.ts, "actor": data.actor, "accion": data.accion}

@router.get("", summary="Listar eventos", description="Paginado simple por offset/limit, ordenado por más recientes")
def list_events(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    rows = db.execute(
        text("SELECT id, ts, actor, accion, detalle FROM auditoria ORDER BY ts DESC, id DESC OFFSET :o LIMIT :l"),
        {"o": offset, "l": limit}
    ).mappings().all()
    return {"items": [dict(r) for r in rows], "offset": offset, "limit": limit}

@router.get("/{event_id}", summary="Obtener evento por id")
def get_event(event_id: int, db: Session = Depends(get_db)):
    row = db.execute(
        text("SELECT id, ts, actor, accion, detalle FROM auditoria WHERE id=:id"),
        {"id": event_id}
    ).mappings().first()
    if not row:
        raise HTTPException(404, "No encontrado")
    return dict(row)

@router.delete("/{event_id}", summary="Borrar evento por id")
def delete_event(event_id: int, db: Session = Depends(get_db)):
    res = db.execute(text("DELETE FROM auditoria WHERE id=:id"), {"id": event_id})
    db.commit()
    if res.rowcount == 0:
        raise HTTPException(404, "No encontrado")
    return {"ok": True, "deleted_id": event_id, "ts": datetime.utcnow().isoformat() + "Z"}
