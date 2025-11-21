# app/routers/backup_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse, JSONResponse

from app.services.backup_service import create_backup_sql_gz, list_backups, get_backup_path
from app.core.deps import require_admin

router = APIRouter(prefix="/backups", tags=["Backups"])

@router.get("/list", summary="Listar backups")
def listar(_auth=Depends(require_admin)):
    """Lista todos los backups con metadata"""
    backups = list_backups()
    return {"items": backups, "total": len(backups)}

@router.post("/create", summary="Crear backup ahora")
def crear(_auth=Depends(require_admin)):
    """Crea un backup SQL.GZ usando pg_dump"""
    try:
        result = create_backup_sql_gz()
        return {
            "ok": True,
            "filename": result["filename"],
            "size": result["size"],
            "created_at": result["created_at"],
            "checksum": result["checksum"],
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear backup: {str(e)}"
        )

@router.get("/download/{filename}", summary="Descargar backup por nombre")
def descargar(filename: str, _auth=Depends(require_admin)):
    """Descarga un backup específico"""
    filepath = get_backup_path(filename)
    if not filepath:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Backup no encontrado"
        )
    
    media_type = "application/gzip" if filename.endswith(".gz") else "application/zip"
    return FileResponse(filepath, media_type=media_type, filename=filename)

# Compatibilidad con endpoints antiguos
@router.post("/run", summary="Ejecutar backup ahora (legacy)")
def run_backup(_auth=Depends(require_admin)):
    """Endpoint legacy que crea backup y devuelve path"""
    result = crear(_auth=_auth)
    return {"ok": True, "file": result["filename"]}

@router.get("/download", summary="Descargar último backup (legacy)")
def download_last(_auth=Depends(require_admin)):
    """Endpoint legacy que descarga el último backup"""
    backups = list_backups()
    if not backups:
        return JSONResponse({"error": "No hay backups aún"}, status_code=404)
    filename = backups[0]["filename"]
    return descargar(filename, _auth=_auth)
