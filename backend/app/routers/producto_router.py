# app/routers/producto_router.py
from __future__ import annotations

from io import BytesIO
from typing import List, Sequence, Union

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_admin, common_params, CommonQueryParams
from app.db.database import get_db
from app.models.producto import Producto
from app.schemas.producto_schema import (
    ProductoCreate, ProductoUpdate, ProductoOut, ProductoPageOut
)

try:
    from openpyxl import Workbook
except ImportError:
    Workbook = None  # si falta openpyxl, lo informamos en el endpoint

router = APIRouter(prefix="/productos", tags=["Productos"])

# -------------------------
# Helpers de filtrado/orden
# -------------------------
def _build_search_filter(search: str | None):
    if not search:
        return None
    pattern = f"%{search.strip()}%"
    cols = []
    if hasattr(Producto, "nombre"):
        cols.append(Producto.nombre.ilike(pattern))
    if hasattr(Producto, "descripcion"):
        cols.append(Producto.descripcion.ilike(pattern))
    if hasattr(Producto, "sku"):
        # por si agregás sku más adelante (no rompe si no existe)
        cols.append(getattr(Producto, "sku").ilike(pattern))
    return or_(*cols) if cols else None

def _parse_sort(sort: str | None):
    allowed = {
        "id": getattr(Producto, "id", None),
        "nombre": getattr(Producto, "nombre", None),
        "precio": getattr(Producto, "precio", None),
        "descripcion": getattr(Producto, "descripcion", None),
        "sku": getattr(Producto, "sku", None),
    }
    allowed = {k: v for k, v in allowed.items() if v is not None}

    if not sort:
        return [Producto.id.asc()]
    order = []
    for raw in [p.strip() for p in sort.split(",") if p.strip()]:
        desc = raw.startswith("-")
        key = raw[1:] if desc else raw
        col = allowed.get(key)
        if not col:
            continue
        order.append(col.desc() if desc else col.asc())
    return order or [Producto.id.asc()]

# -------------------------
# Lectura (lista / paginado)
# -------------------------
@router.get("", response_model=Union[List[ProductoOut], ProductoPageOut],
            dependencies=[Depends(get_current_user)])
@router.get("/", response_model=Union[List[ProductoOut], ProductoPageOut],
            dependencies=[Depends(get_current_user)])
def listar(q: CommonQueryParams = Depends(common_params), db: Session = Depends(get_db)):
    """
    - Si NO se envían page/size/search/sort -> list[ProductoOut] (modo legacy)
    - Si se envía cualquiera -> ProductoPageOut (paginado)
    """
    filters = []
    sf = _build_search_filter(q.search)
    if sf is not None:
        filters.append(sf)

    order_by = _parse_sort(q.sort)
    base_stmt = select(Producto).where(*filters)

    legacy_mode = q.page is None and q.size is None and q.search is None and q.sort is None
    if legacy_mode:
        items: Sequence[Producto] = db.scalars(base_stmt.order_by(*order_by)).all()
        return [ProductoOut.model_validate(x) for x in items]

    page = q.page or 1
    size = q.size or 20
    total = db.scalar(select(func.count(Producto.id)).where(*filters)) or 0

    stmt = base_stmt.order_by(*order_by).offset((page - 1) * size).limit(size)
    items_page: Sequence[Producto] = db.scalars(stmt).all()

    return ProductoPageOut(
        items=[ProductoOut.model_validate(x) for x in items_page],
        total=total,
        page=page,
        size=size,
    )

# -------------------------
# Exportar a Excel
# -------------------------
@router.get("/export", dependencies=[Depends(get_current_user)])
def exportar_excel(q: CommonQueryParams = Depends(common_params), db: Session = Depends(get_db)):
    if Workbook is None:
        raise HTTPException(
            status_code=500,
            detail="Falta dependencia 'openpyxl'. Instalala en la imagen/entorno del backend."
        )

    # Reutilizamos filtros/orden
    filters = []
    sf = _build_search_filter(q.search)
    if sf is not None:
        filters.append(sf)
    order_by = _parse_sort(q.sort)

    items: Sequence[Producto] = db.scalars(
        select(Producto).where(*filters).order_by(*order_by)
    ).all()

    # Armar Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Productos"

    # Encabezados
    headers = ["ID", "Nombre", "Descripción", "Precio"]
    # si tu modelo tiene más campos, agregalos acá (sku, stock, activo, etc.)
    ws.append(headers)

    for p in items:
        ws.append([
            getattr(p, "id", None),
            getattr(p, "nombre", None),
            getattr(p, "descripcion", None),
            float(getattr(p, "precio", 0.0)) if getattr(p, "precio", None) is not None else None,
        ])

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)

    return Response(
        content=buf.read(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="productos.xlsx"'},
    )

# -------------------------
# Detalle
# -------------------------
@router.get("/{prod_id}", response_model=ProductoOut, dependencies=[Depends(get_current_user)])
def obtener(prod_id: int, db: Session = Depends(get_db)):
    obj = db.get(Producto, prod_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return ProductoOut.model_validate(obj)

# -------------------------
# Escritura (solo admin)
# -------------------------
@router.post("/", response_model=ProductoOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_admin)])
def crear(data: ProductoCreate, db: Session = Depends(get_db)):
    obj = Producto(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return ProductoOut.model_validate(obj)

@router.put("/{prod_id}", response_model=ProductoOut,
            dependencies=[Depends(require_admin)])
def actualizar(prod_id: int, data: ProductoUpdate, db: Session = Depends(get_db)):
    obj = db.get(Producto, prod_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return ProductoOut.model_validate(obj)

@router.delete("/{prod_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(require_admin)])
def eliminar(prod_id: int, db: Session = Depends(get_db)):
    obj = db.get(Producto, prod_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(obj)
    db.commit()
    return None
