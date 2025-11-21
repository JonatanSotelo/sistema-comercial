from typing import List, Optional, Tuple, Dict, Any
from io import BytesIO
from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from openpyxl import Workbook

from app.db.database import get_db
from app.models.cliente_model import Cliente
from app.schemas.cliente_schema import ClienteOut, ClienteCreate, ClienteUpdate
from app.core.deps import require_user, require_admin
from app.services.import_export_service import (
    parse_import_file, normalize_cliente_row
)

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
            (Cliente.nombre.ilike(like))
            | (Cliente.email.ilike(like))
            | (Cliente.cuit.ilike(like))
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
        elif col == "cuit":
            order_clauses.append(direction(Cliente.cuit))
    if not order_clauses:
        order_clauses = [asc(Cliente.nombre), asc(Cliente.id)]
    return queryset.order_by(*order_clauses)

# --------- CRUD ----------
@router.get("", response_model=List[ClienteOut])
def list_clientes(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=200),
    search: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _auth=Depends(require_user),
):
    page, size, offset = parse_pagination(page, per_page)
    queryset = db.query(Cliente)
    queryset = apply_search(queryset, search)
    queryset = apply_sort(queryset, sort)
    return queryset.offset(offset).limit(size).all()

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

# --------- Export CSV/XLSX ----------
@router.get("/export")
def export_clientes(
    format: str = Query("xlsx", regex="^(csv|xlsx)$"),
    search: Optional[str] = Query(None),
    sort: Optional[str] = Query("nombre,-id"),
    db: Session = Depends(get_db),
    _auth=Depends(require_user),
):
    qs = db.query(Cliente)
    qs = apply_search(qs, search)
    qs = apply_sort(qs, sort)
    rows: List[Cliente] = qs.all()

    headers = ["ID", "Nombre", "Email", "Telefono", "CUIT"]
    data_rows = []
    for r in rows:
        data_rows.append([r.id, r.nombre, r.email or "", r.telefono or "", r.cuit or ""])

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
            headers={"Content-Disposition": 'attachment; filename="clientes.csv"'},
        )
    else:  # xlsx
        wb = Workbook()
        ws = wb.active
        ws.title = "Clientes"
        ws.append(headers)
        for row in data_rows:
            ws.append(row)
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": 'attachment; filename="clientes.xlsx"'},
        )

# --------- Import CSV/XLSX ----------
@router.post("/import")
async def importar(
    file: UploadFile = File(...),
    dry_run: bool = Query(True, description="Si true, solo muestra preview sin ejecutar"),
    db: Session = Depends(get_db),
    _auth=Depends(require_admin),
):
    """Importa clientes desde CSV o XLSX con dry_run para preview"""
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
            normalized = normalize_cliente_row(row)
            
            # Validar nombre requerido
            if not normalized.get("nombre"):
                errores.append({
                    "fila": idx,
                    "error": "Nombre es requerido",
                    "datos": row,
                })
                continue
            
            # Upsert por CUIT si viene, sino por nombre+email
            cuit = normalized.get("cuit")
            nombre = normalized["nombre"]
            email = normalized.get("email")
            
            existing = None
            if cuit:
                existing = db.query(Cliente).filter(Cliente.cuit == cuit).first()
            elif nombre and email:
                existing = db.query(Cliente).filter(
                    Cliente.nombre == nombre,
                    Cliente.email == email
                ).first()
            
            if existing:
                # Update
                if dry_run:
                    actualizados += 1
                else:
                    for k, v in normalized.items():
                        setattr(existing, k, v)
                    db.add(existing)
                    actualizados += 1
            else:
                # Insert
                if dry_run:
                    insertados += 1
                else:
                    cliente_data = ClienteCreate(**normalized)
                    obj = Cliente(**cliente_data.model_dump(exclude_none=True))
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


# --------- Saldo (v0.9.1) ----------
@router.get("/{cliente_id}/saldo", dependencies=[Depends(require_user)])
def obtener_saldo_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """
    Obtiene el saldo pendiente de un cliente.
    Saldo = Suma de saldos de todas las ventas del cliente.
    """
    from app.services.cobros_service import get_saldo_cliente
    
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    saldo = get_saldo_cliente(db, cliente_id)
    
    return {
        "cliente_id": cliente_id,
        "cliente_nombre": cliente.nombre,
        "saldo": saldo
    }
