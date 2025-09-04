from typing import List, Optional, Tuple
from io import BytesIO
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from openpyxl import Workbook

from app.db.database import get_db
from app.models.cliente_model import Cliente
from app.schemas.cliente_schema import ClienteOut, ClienteCreate, ClienteUpdate
from app.core.deps import require_user, require_admin

router = APIRouter(prefix="/clientes", tags=["clientes"])

# --------- Helpers ----------
def parse_pagination(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
) -> Tuple[int, int, int]:
    page = page or 1
    size = size or 20
    offset = (page - 1) * size
    return page, size, offset

def apply_search(queryset, search: Optional[str]):
    if search:
        like = f"%{search}%"
        queryset = queryset.filter(
            (Cliente.nombre.ilike(like)) | (Cliente.email.ilike(like))
        )
    return queryset

def apply_sort(queryset, sort: Optional[str]):
    if not sort:
        return queryset.order_by(asc(Cliente.nombre), asc(Cliente.id))
    order_clauses = []
    for token in [t.strip() for t in sort.split(",") if t.strip()]:
        if token.startswith("-"):
            col = token[1:]; direction = desc
        else:
            col = token; direction = asc
        if col == "nombre":
            order_clauses.append(direction(Cliente.nombre))
        elif col == "email":
            order_clauses.append(direction(Cliente.email))
        elif col == "id":
            order_clauses.append(direction(Cliente.id))
    if not order_clauses:
        order_clauses = [asc(Cliente.nombre), asc(Cliente.id)]
    return queryset.order_by(*order_clauses)

# --------- CRUD ----------
@router.post("", response_model=ClienteOut, status_code=201)
def create_cliente(
    payload: ClienteCreate,
    db: Session = Depends(get_db),
    _auth=Depends(require_admin),
):
    obj = Cliente(**payload.model_dump(exclude_unset=True))
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/{cliente_id}", response_model=ClienteOut)
def get_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(require_user),
):
    obj = db.get(Cliente, cliente_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return obj

@router.put("/{cliente_id}", response_model=ClienteOut)
def update_cliente(
    cliente_id: int,
    payload: ClienteUpdate,
    db: Session = Depends(get_db),
    _auth=Depends(require_admin),
):
    obj = db.get(Cliente, cliente_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{cliente_id}", status_code=204)
def delete_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(require_admin),
):
    obj = db.get(Cliente, cliente_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    db.delete(obj)
    db.commit()
    return

# --------- Listado + paginación ----------
@router.get("", response_model=dict)
def list_clientes(
    search: Optional[str] = Query(None, description="Busca por nombre/email (ilike)"),
    sort: Optional[str] = Query("nombre,-id", description="Campos separados por coma, '-' desc"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
    _auth=Depends(require_user),
):
    page, size, offset = parse_pagination(page, size)
    qs = db.query(Cliente)
    qs = apply_search(qs, search)
    total = qs.count()
    qs = apply_sort(qs, sort)
    items = qs.offset(offset).limit(size).all()

    return {
        "items": [ClienteOut.model_validate(i).model_dump() for i in items],
        "total": total,
        "page": page,
        "size": size,
    }

# --------- Export Excel ----------
@router.get("/export")
def export_clientes(
    search: Optional[str] = Query(None),
    sort: Optional[str] = Query("nombre,-id"),
    db: Session = Depends(get_db),
    _auth=Depends(require_user),
):
    qs = db.query(Cliente)
    qs = apply_search(qs, search)
    qs = apply_sort(qs, sort)
    rows: List[Cliente] = qs.all()

    wb = Workbook()
    ws = wb.active
    ws.title = "Clientes"
    ws.append(["ID", "Nombre", "Email", "Telefono"])

    for r in rows:
        ws.append([r.id, r.nombre, r.email or "", r.telefono or ""])

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    filename = "clientes.xlsx"

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
