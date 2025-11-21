# app/routers/producto_router.py
from __future__ import annotations

from io import BytesIO
from typing import List, Sequence, Union

from fastapi import APIRouter, Depends, HTTPException, status, Response, UploadFile, File, Query
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from app.core.deps import get_current_user, require_admin, common_params, CommonQueryParams
from app.db.database import get_db
from app.models.producto_model import Producto
from app.schemas.producto_schema import (
    ProductoCreate, ProductoUpdate, ProductoOut, ProductoPageOut
)
from app.services.import_export_service import (
    parse_import_file, normalize_producto_row
)
from app.services.stock_reservations_service import get_disponible_for_productos

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
    if hasattr(Producto, "codigo"):
        cols.append(Producto.codigo.ilike(pattern))
    if hasattr(Producto, "categoria"):
        cols.append(Producto.categoria.ilike(pattern))
    return or_(*cols) if cols else None

def _parse_sort(sort: str | None):
    allowed = {
        "id": getattr(Producto, "id", None),
        "nombre": getattr(Producto, "nombre", None),
        "precio": getattr(Producto, "precio", None),
        "costo": getattr(Producto, "costo", None),
        "stock": getattr(Producto, "stock", None),
        "categoria": getattr(Producto, "categoria", None),
        "codigo": getattr(Producto, "codigo", None),
        "descripcion": getattr(Producto, "descripcion", None),
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
        productos_out = [ProductoOut.model_validate(x) for x in items]
        
        # Agregar disponible a cada producto
        producto_ids = [p.id for p in productos_out]
        disponibles = get_disponible_for_productos(db, producto_ids)
        for p in productos_out:
            p.disponible = disponibles.get(p.id, float(p.stock))
        
        return productos_out

    page = q.page or 1
    size = q.size or 20
    total = db.scalar(select(func.count(Producto.id)).where(*filters)) or 0

    stmt = base_stmt.order_by(*order_by).offset((page - 1) * size).limit(size)
    items_page: Sequence[Producto] = db.scalars(stmt).all()
    productos_out = [ProductoOut.model_validate(x) for x in items_page]
    
    # Agregar disponible a cada producto
    producto_ids = [p.id for p in productos_out]
    disponibles = get_disponible_for_productos(db, producto_ids)
    for p in productos_out:
        p.disponible = disponibles.get(p.id, float(p.stock))

    return ProductoPageOut(
        items=productos_out,
        total=total,
        page=page,
        size=size,
    )

# -------------------------
# Exportar a CSV/XLSX
# -------------------------
@router.get("/export", dependencies=[Depends(get_current_user)])
def exportar(
    format: str = Query("xlsx", regex="^(csv|xlsx)$"),
    q: CommonQueryParams = Depends(common_params),
    db: Session = Depends(get_db),
):
    # Reutilizamos filtros/orden
    filters = []
    sf = _build_search_filter(q.search)
    if sf is not None:
        filters.append(sf)
    order_by = _parse_sort(q.sort)

    items: Sequence[Producto] = db.scalars(
        select(Producto).where(*filters).order_by(*order_by)
    ).all()

    # Encabezados (sin "Activo", con proveedor_id)
    headers = ["ID", "Nombre", "Precio", "Stock", "Proveedor_ID"]
    rows = []
    for p in items:
        rows.append([
            getattr(p, "id", None),
            getattr(p, "nombre", None),
            float(getattr(p, "precio", 0.0)) if getattr(p, "precio", None) is not None else None,
            float(getattr(p, "stock", 0.0)) if getattr(p, "stock", None) is not None else None,
            getattr(p, "proveedor_id", None),
        ])

    if format == "csv":
        from io import StringIO
        import csv
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        writer.writerows(rows)
        output.seek(0)
        return Response(
            content=output.getvalue().encode("utf-8-sig"),
            media_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="productos.csv"'},
        )
    else:  # xlsx
        if Workbook is None:
            raise HTTPException(
                status_code=500,
                detail="Falta dependencia 'openpyxl'. Instalala en la imagen/entorno del backend."
            )
        wb = Workbook()
        ws = wb.active
        ws.title = "Productos"
        ws.append(headers)
        for row in rows:
            ws.append(row)
        buf = BytesIO()
        wb.save(buf)
        buf.seek(0)
        return Response(
            content=buf.read(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": 'attachment; filename="productos.xlsx"'},
        )

# -------------------------
# Import CSV/XLSX
# -------------------------
@router.post("/import", dependencies=[Depends(require_admin)])
async def importar(
    file: UploadFile = File(...),
    dry_run: bool = Query(True, description="Si true, solo muestra preview sin ejecutar"),
    db: Session = Depends(get_db),
):
    """Importa productos desde CSV o XLSX con dry_run para preview"""
    try:
        file_content = await file.read()
        headers, rows = parse_import_file(file_content, file.filename or "")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al parsear archivo: {e}")
    
    insertados = 0
    actualizados = 0
    errores: List[Dict[str, Any]] = []
    sample_rows: List[Dict[str, Any]] = []
    
    for idx, row in enumerate(rows, start=2):  # Empezar en 2 (header es fila 1)
        try:
            normalized = normalize_producto_row(row)
            
            # Validar nombre requerido
            if not normalized.get("nombre"):
                errores.append({
                    "fila": idx,
                    "error": "Nombre es requerido",
                    "datos": row,
                })
                continue
            
            # Upsert por nombre (y opcionalmente proveedor_id)
            nombre = normalized["nombre"]
            proveedor_id = normalized.get("proveedor_id")
            
            existing = None
            if proveedor_id:
                existing = db.query(Producto).filter(
                    Producto.nombre == nombre,
                    Producto.proveedor_id == proveedor_id
                ).first()
            else:
                existing = db.query(Producto).filter(Producto.nombre == nombre).first()
            
            if existing:
                # Update
                if dry_run:
                    actualizados += 1
                else:
                    for k, v in normalized.items():
                        if k != "nombre":  # No actualizar nombre (es la clave)
                            setattr(existing, k, v)
                    db.add(existing)
                    actualizados += 1
            else:
                # Insert
                if dry_run:
                    insertados += 1
                else:
                    producto_data = ProductoCreate(**normalized)
                    obj = Producto(**producto_data.model_dump())
                    db.add(obj)
                    insertados += 1
            
            # Agregar a muestra (primeros 5)
            if len(sample_rows) < 5:
                sample_rows.append({
                    "fila": idx,
                    "accion": "actualizar" if existing else "insertar",
                    "datos": normalized,
                })
        
        except Exception as e:
            errores.append({
                "fila": idx,
                "error": str(e),
                "datos": row,
            })
    
    if not dry_run:
        db.commit()
    
    return {
        "insertados": insertados,
        "actualizados": actualizados,
        "errores": errores[:10],  # Limitar a 10 errores
        "sample_rows": sample_rows,
    }

# -------------------------
# Detalle
# -------------------------
@router.get("/{prod_id}", response_model=ProductoOut, dependencies=[Depends(get_current_user)])
def obtener(prod_id: int, db: Session = Depends(get_db)):
    obj = db.get(Producto, prod_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    producto_out = ProductoOut.model_validate(obj)
    
    # Agregar disponible
    from app.services.stock_reservations_service import get_disponible_for_producto
    producto_out.disponible = get_disponible_for_producto(db, prod_id)
    
    return producto_out

# -------------------------
# Escritura (solo admin)
# -------------------------
@router.post("", response_model=ProductoOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_admin)])
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
