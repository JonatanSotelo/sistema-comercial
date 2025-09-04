# app/routers/backup_router.py
from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse

from app.services.backup_service import create_backup_zip, last_backup_file

router = APIRouter(prefix="/backup", tags=["Backup"])

@router.post("/run", summary="Ejecutar backup ahora")
def run_backup():
    path = create_backup_zip()
    return {"ok": True, "file": path}

@router.get("/download", summary="Descargar último backup")
def download_last():
    path = last_backup_file()
    if not path:
        return JSONResponse({"error": "No hay backups aún"}, status_code=404)
    filename = path.split("/")[-1]
    return FileResponse(path, media_type="application/zip", filename=filename)

@router.get("/last", summary="Info del último backup")
def info_last():
    path = last_backup_file()
    if not path:
        return {"exists": False}
    return {"exists": True, "file": path}
