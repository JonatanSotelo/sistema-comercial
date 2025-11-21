from typing import List, Optional, Tuple, Dict, Any
from io import BytesIO
from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from openpyxl import Workbook

from app.db.database import get_db
from app.models.proveedor_model import Proveedor
from app.schemas.proveedor_schema import ProveedorOut, ProveedorCreate, ProveedorUpdate
from app.core.deps import require_user, require_admin
from app.services.import_export_service import (
    parse_import_file, normalize_proveedor_row
)

router = APIRouter(prefix="/proveedores", tags=["proveedores"])

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
            (Proveedor.nombre.ilike(like))
            | (Proveedor.email.ilike(like))
            | (Proveedor.telefono.ilike(like))
            | (Proveedor.cuit.ilike(like))
            | (Proveedor.direccion.ilike(like))
        )
    return queryset

def apply_sort(queryset, sort: Optional[str]):
    if not sort:
        return queryset.order_by(asc(Proveedor.nombre), asc(Proveedor.id))
    order_clauses = []
    for token in [t.strip() for t in sort.split(",") if t.strip()]:
        if token.startswith("-"):
            col = token[1:]; direction = desc
        else:
            col = token; direction = asc
        if col == "nombre":
            order_clauses.append(direction(Proveedor.nombre))
        elif col == "email":
            order_clauses.append(direction(Proveedor.email))
        elif col == "id":
            order_clauses.append(direction(Proveedor.id))
        elif col == "telefono":
            order_clauses.append(direction(Proveedor.telefono))
        elif col == "cuit":
            order_clauses.append(direction(Proveedor.cuit))
        elif col == "direccion":
            order_clauses.append(direction(Proveedor.direccion))
    if not order_clauses:
        order_clauses = [asc(Proveedor.nombre), asc(Proveedor.id)]
    return queryset.order_by(*order_clauses)

# --------- CRUD ----------
@router.get("", response_model=List[ProveedorOut])
def list_proveedores(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=200),
    search: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _auth=Depends(require_user),
):
    page, size, offset = parse_pagination(page, per_page)
    queryset = db.query(Proveedor)
    queryset = apply_search(queryset, search)
    queryset = apply_sort(queryset, sort)
    return queryset.offset(offset).limit(size).all()

@router.post("", response_model=ProveedorOut, status_code=201)
def create_proveedor(
    payload: ProveedorCreate,
    db: Session = Depends(get_db),
    _auth=Depends(require_admin),
):
    obj = Proveedor(**payload.model_dump(exclude_unset=True))
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.get("/{proveedor_id}", response_model=ProveedorOut)
def get_proveedor(
    proveedor_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(require_user),
):
    obj = db.get(Proveedor, proveedor_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return obj

@router.put("/{proveedor_id}", response_model=ProveedorOut)
def update_proveedor(
    proveedor_id: int,
    payload: ProveedorUpdate,
    db: Session = Depends(get_db),
    _auth=Depends(require_admin),
):
    obj = db.get(Proveedor, proveedor_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.delete("/{proveedor_id}", status_code=204)
def delete_proveedor(
    proveedor_id: int,
    db: Session = Depends(get_db),
    _auth=Depends(require_admin),
):
    obj = db.get(Proveedor, proveedor_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    db.delete(obj)
    db.commit()
    return

# --------- Listado + paginación ----------
@router.get("", response_model=dict)
def list_proveedores(
    search: Optional[str] = Query(None, description="Busca por nombre/email (ilike)"),
    sort: Optional[str] = Query("nombre,-id", description="Campos separados por coma, '-' desc"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
    _auth=Depends(require_user),
):
    page, size, offset = parse_pagination(page, size)
    qs = db.query(Proveedor)
    qs = apply_search(qs, search)
    total = qs.count()
    qs = apply_sort(qs, sort)
    items = qs.offset(offset).limit(size).all()

    return {
        "items": [ProveedorOut.model_validate(i).model_dump() for i in items],
        "total": total,
        "page": page,
        "size": size,
    }

# --------- Export CSV/XLSX ----------
@router.get("/export")
def export_proveedores(
    format: str = Query("xlsx", regex="^(csv|xlsx)$"),
    search: Optional[str] = Query(None),
    sort: Optional[str] = Query("nombre,-id"),
    db: Session = Depends(get_db),
    _auth=Depends(require_user),
):
    qs = db.query(Proveedor)
    qs = apply_search(qs, search)
    qs = apply_sort(qs, sort)
    rows: List[Proveedor] = qs.all()

    headers = ["ID", "Nombre", "Email", "Teléfono", "CUIT", "Dirección"]
    data_rows = []
    for r in rows:
        data_rows.append([r.id, r.nombre, r.email or "", r.telefono or "", r.cuit or "", r.direccion or ""])

    if format == "csv":
        from io import StringIO
        import csv as csv_module
        output = StringIO()
        writer = csv_module.writer(output)
        writer.writerow(headers)
        writer.writerows(data_rows)
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue().encode("utf-8-sig")]),
            media_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="proveedores.csv"'},
        )
    else:  # xlsx
        wb = Workbook()
        ws = wb.active
        ws.title = "Proveedores"
        ws.append(headers)
        for row in data_rows:
            ws.append(row)
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": 'attachment; filename="proveedores.xlsx"'},
        )

# --------- Import CSV/XLSX ----------
@router.post("/import")
async def importar(
    file: UploadFile = File(...),
    dry_run: bool = Query(True, description="Si true, solo muestra preview sin ejecutar"),
    db: Session = Depends(get_db),
    _auth=Depends(require_admin),
):
    """Importa proveedores desde CSV o XLSX con dry_run para preview"""
    try:
        file_content = await file.read()
        headers, rows = parse_import_file(file_content, file.filename or "")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al parsear archivo: {e}")
    
    insertados = 0
    actualizados = 0
    errores: List[Dict[str, Any]] = []
    sample_rows: List[Dict[str, Any]] = []
    
    for idx, row in enumerate(rows, start=2):
        try:
            normalized = normalize_proveedor_row(row)
            
            # Validar nombre requerido
            if not normalized.get("nombre"):
                errores.append({
                    "fila": idx,
                    "error": "Nombre es requerido",
                    "datos": row,
                })
                continue
            
            # Upsert por CUIT si viene, sino por nombre
            cuit = normalized.get("cuit")
            nombre = normalized["nombre"]
            
            existing = None
            if cuit:
                existing = db.query(Proveedor).filter(Proveedor.cuit == cuit).first()
            else:
                existing = db.query(Proveedor).filter(Proveedor.nombre == nombre).first()
            
            if existing:
                # Update
                if dry_run:
                    actualizados += 1
                else:
                    for k, v in normalized.items():
                        if k != "nombre":  # No actualizar nombre si es la clave
                            setattr(existing, k, v)
                    db.add(existing)
                    actualizados += 1
            else:
                # Insert
                if dry_run:
                    insertados += 1
                else:
                    proveedor_data = ProveedorCreate(**normalized)
                    obj = Proveedor(**proveedor_data.model_dump(exclude_none=True))
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
        "errores": errores[:10],
        "sample_rows": sample_rows,
    }
