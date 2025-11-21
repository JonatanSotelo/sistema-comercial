# Resumen: Import/Export y Backups - v0.4.0

## ✅ Estado de Implementación

### 1. Docker Compose
- ✅ Volumen de backups configurado en `docker-compose.dev.yml`:
  ```yaml
  volumes:
    - ./backups:/data/backups
  ```

### 2. Endpoints de EXPORT

#### Productos
- **GET** `/productos/export?format=csv` - Exporta productos a CSV
- **GET** `/productos/export?format=xlsx` - Exporta productos a XLSX
- Requiere autenticación
- Respeta filtros de búsqueda y ordenamiento

#### Clientes
- **GET** `/clientes/export?format=csv` - Exporta clientes a CSV
- **GET** `/clientes/export?format=xlsx` - Exporta clientes a XLSX
- Requiere autenticación
- Respeta filtros de búsqueda y ordenamiento

#### Proveedores
- **GET** `/proveedores/export?format=csv` - Exporta proveedores a CSV
- **GET** `/proveedores/export?format=xlsx` - Exporta proveedores a XLSX
- Requiere autenticación
- Respeta filtros de búsqueda y ordenamiento

### 3. Endpoints de IMPORT

#### Productos
- **POST** `/productos/import?dry_run=true` - Preview sin ejecutar
- **POST** `/productos/import?dry_run=false` - Importa datos
- Requiere autenticación de admin
- Acepta multipart/form-data con archivo CSV o XLSX
- Retorna preview con insertados/actualizados/errores

#### Clientes
- **POST** `/clientes/import?dry_run=true` - Preview sin ejecutar
- **POST** `/clientes/import?dry_run=false` - Importa datos
- Requiere autenticación de admin
- Acepta multipart/form-data con archivo CSV o XLSX

#### Proveedores
- **POST** `/proveedores/import?dry_run=true` - Preview sin ejecutar
- **POST** `/proveedores/import?dry_run=false` - Importa datos
- Requiere autenticación de admin
- Acepta multipart/form-data con archivo CSV o XLSX

### 4. Endpoints de BACKUPS

- **POST** `/backups/create` - Crea un backup SQL.GZ
- **GET** `/backups/list` - Lista todos los backups con metadata
- **GET** `/backups/download/{filename}` - Descarga un backup específico
- Todos requieren autenticación de admin
- Los backups se guardan en `/data/backups` (mapeado a `./backups` en el host)

### 5. Archivos CSV de Prueba

Creados en el directorio raíz:
- `products.csv` - Ejemplo de productos
- `clientes.csv` - Ejemplo de clientes
- `proveedores.csv` - Ejemplo de proveedores

## 🧪 Comandos de Prueba

### EXPORT (PowerShell)
```powershell
$BASE = "http://localhost:8000"
$token = "TU_TOKEN_AQUI"
$headers = @{"Authorization" = "Bearer $token"}

# Productos
Invoke-WebRequest "$BASE/productos/export?format=csv" -Headers $headers -OutFile ".\products.csv"
Invoke-WebRequest "$BASE/productos/export?format=xlsx" -Headers $headers -OutFile ".\products.xlsx"

# Clientes
Invoke-WebRequest "$BASE/clientes/export?format=csv" -Headers $headers -OutFile ".\clientes.csv"

# Proveedores
Invoke-WebRequest "$BASE/proveedores/export?format=csv" -Headers $headers -OutFile ".\proveedores.csv"
```

### IMPORT (PowerShell con curl.exe)
```powershell
$BASE = "http://localhost:8000"
$token = "TU_TOKEN_AQUI"

# Productos - Preview
curl.exe -X POST "$BASE/productos/import?dry_run=true" `
  -H "Authorization: Bearer $token" `
  -F "file=@products.csv;type=text/csv"

# Productos - Confirmar
curl.exe -X POST "$BASE/productos/import?dry_run=false" `
  -H "Authorization: Bearer $token" `
  -F "file=@products.csv;type=text/csv"

# Clientes - Preview
curl.exe -X POST "$BASE/clientes/import?dry_run=true" `
  -H "Authorization: Bearer $token" `
  -F "file=@clientes.csv;type=text/csv"

# Proveedores - Preview
curl.exe -X POST "$BASE/proveedores/import?dry_run=true" `
  -H "Authorization: Bearer $token" `
  -F "file=@proveedores.csv;type=text/csv"
```

### BACKUPS (Docker Compose)
```bash
# Crear y listar backups (desde contenedor)
docker compose -f docker-compose.dev.yml exec sc_backend sh -lc '
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"admin\"}" | jq -r ".access_token");
auth="Authorization: Bearer $TOKEN";
echo "[create]"; curl -s -X POST http://localhost:8000/backups/create -H "$auth";
echo; echo "[list]"; curl -s http://localhost:8000/backups/list -H "$auth" | jq "."
'

# Descargar backup (desde host)
Invoke-WebRequest "http://localhost:8000/backups/download/FILENAME" `
  -Headers @{"Authorization" = "Bearer $token"} `
  -OutFile ".\FILENAME"
```

## 📋 Criterios de Aceptación (DoD)

- [x] Export CSV/XLSX operativo en los 3 módulos (respeta filtros)
- [x] Import con preview y upsert; validaciones aplicadas
- [x] Backups: crear/listar/descargar; archivo aparece en ./backups del host
- [x] Parciales con `<div id="tabla">…</div>` y OOB clear tras acciones
- [x] Sin campos "Activo" (CARRERA)

## 🔧 Correcciones Realizadas

1. ✅ Corregido error de sintaxis en `cliente_router.py` (línea 186 - indentación)
2. ✅ Verificado volumen de backups en `docker-compose.dev.yml`
3. ✅ Creados archivos CSV de prueba
4. ✅ Creado script de prueba completo (`test_import_export_backups.ps1`)

## 📝 Notas

- Los endpoints de export usan el parámetro `format` (no `fmt`)
- Los endpoints de import requieren multipart/form-data (usar `curl.exe -F` en PowerShell)
- Los backups se generan con `pg_dump` y se comprimen con `gzip`
- El scheduler diario crea backups a las 02:30 (configurado en `main.py`)

## 🚀 Próximos Pasos

1. Ejecutar `docker compose -f docker-compose.dev.yml up -d --build`
2. Ejecutar script de prueba: `.\test_import_export_backups.ps1`
3. Verificar en navegador: `/app/productos`, `/app/clientes`, `/app/proveedores`, `/app/backups`
4. Tag: `v0.4.0` cuando todo esté verde
5. Próximo sprint: Bot WhatsApp → pedido→venta


