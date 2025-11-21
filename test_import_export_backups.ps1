# Script de prueba para Import/Export y Backups
# Uso: .\test_import_export_backups.ps1

$BASE = "http://localhost:8000"
$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PRUEBA DE IMPORT/EXPORT Y BACKUPS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar que el servidor esté corriendo
Write-Host "[1/6] Verificando servidor..." -ForegroundColor Yellow
try {
    $health = Invoke-WebRequest -Uri "$BASE/health" -UseBasicParsing -TimeoutSec 2
    if ($health.StatusCode -eq 200) {
        Write-Host "✅ Servidor disponible" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Servidor responde con código: $($health.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Error: No se puede conectar al servidor" -ForegroundColor Red
    Write-Host "   Asegúrate de que el servidor esté corriendo en $BASE" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 2. Obtener token de autenticación
Write-Host "[2/6] Obteniendo token de autenticación..." -ForegroundColor Yellow
try {
    $loginBody = @{
        username = "admin"
        password = "admin"
    } | ConvertTo-Json
    
    $loginResponse = Invoke-RestMethod -Uri "$BASE/auth/login" -Method POST -Body $loginBody -ContentType "application/json"
    $token = $loginResponse.access_token
    if (-not $token) {
        $token = $loginResponse.token
    }
    if (-not $token) {
        Write-Host "❌ No se pudo obtener el token" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Token obtenido" -ForegroundColor Green
} catch {
    Write-Host "❌ Error al obtener token: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

$headers = @{
    "Authorization" = "Bearer $token"
}

# 3. Probar EXPORT
Write-Host "[3/6] Probando EXPORT (CSV/XLSX)..." -ForegroundColor Yellow

# Exportar productos
Write-Host "  - Exportando productos (CSV)..." -ForegroundColor Gray
try {
    Invoke-WebRequest -Uri "$BASE/productos/export?format=csv" -Headers $headers -OutFile ".\products_export.csv" -UseBasicParsing
    Write-Host "    ✅ products_export.csv creado" -ForegroundColor Green
} catch {
    Write-Host "    ❌ Error: $_" -ForegroundColor Red
}

Write-Host "  - Exportando productos (XLSX)..." -ForegroundColor Gray
try {
    Invoke-WebRequest -Uri "$BASE/productos/export?format=xlsx" -Headers $headers -OutFile ".\products_export.xlsx" -UseBasicParsing
    Write-Host "    ✅ products_export.xlsx creado" -ForegroundColor Green
} catch {
    Write-Host "    ❌ Error: $_" -ForegroundColor Red
}

# Exportar clientes
Write-Host "  - Exportando clientes (CSV)..." -ForegroundColor Gray
try {
    Invoke-WebRequest -Uri "$BASE/clientes/export?format=csv" -Headers $headers -OutFile ".\clientes_export.csv" -UseBasicParsing
    Write-Host "    ✅ clientes_export.csv creado" -ForegroundColor Green
} catch {
    Write-Host "    ❌ Error: $_" -ForegroundColor Red
}

# Exportar proveedores
Write-Host "  - Exportando proveedores (CSV)..." -ForegroundColor Gray
try {
    Invoke-WebRequest -Uri "$BASE/proveedores/export?format=csv" -Headers $headers -OutFile ".\proveedores_export.csv" -UseBasicParsing
    Write-Host "    ✅ proveedores_export.csv creado" -ForegroundColor Green
} catch {
    Write-Host "    ❌ Error: $_" -ForegroundColor Red
}
Write-Host ""

# 4. Probar IMPORT (dry_run primero)
Write-Host "[4/6] Probando IMPORT (dry_run)..." -ForegroundColor Yellow

# Importar productos (dry_run)
Write-Host "  - Importando productos (dry_run)..." -ForegroundColor Gray
try {
    $productosDryRun = curl.exe -s -X POST "$BASE/productos/import?dry_run=true" `
        -H "Authorization: Bearer $token" `
        -F "file=@products.csv;type=text/csv"
    Write-Host "    ✅ Preview productos:" -ForegroundColor Green
    Write-Host $productosDryRun -ForegroundColor Gray
} catch {
    Write-Host "    ❌ Error: $_" -ForegroundColor Red
}

# Importar clientes (dry_run)
Write-Host "  - Importando clientes (dry_run)..." -ForegroundColor Gray
try {
    $clientesDryRun = curl.exe -s -X POST "$BASE/clientes/import?dry_run=true" `
        -H "Authorization: Bearer $token" `
        -F "file=@clientes.csv;type=text/csv"
    Write-Host "    ✅ Preview clientes:" -ForegroundColor Green
    Write-Host $clientesDryRun -ForegroundColor Gray
} catch {
    Write-Host "    ❌ Error: $_" -ForegroundColor Red
}

# Importar proveedores (dry_run)
Write-Host "  - Importando proveedores (dry_run)..." -ForegroundColor Gray
try {
    $proveedoresDryRun = curl.exe -s -X POST "$BASE/proveedores/import?dry_run=true" `
        -H "Authorization: Bearer $token" `
        -F "file=@proveedores.csv;type=text/csv"
    Write-Host "    ✅ Preview proveedores:" -ForegroundColor Green
    Write-Host $proveedoresDryRun -ForegroundColor Gray
} catch {
    Write-Host "    ❌ Error: $_" -ForegroundColor Red
}
Write-Host ""

# 5. Probar BACKUPS
Write-Host "[5/6] Probando BACKUPS..." -ForegroundColor Yellow

# Crear backup
Write-Host "  - Creando backup..." -ForegroundColor Gray
try {
    $backupCreate = Invoke-RestMethod -Uri "$BASE/backups/create" -Method POST -Headers $headers
    Write-Host "    ✅ Backup creado: $($backupCreate.filename)" -ForegroundColor Green
    Write-Host "       Tamaño: $($backupCreate.size) bytes" -ForegroundColor Gray
} catch {
    Write-Host "    ❌ Error al crear backup: $_" -ForegroundColor Red
}

# Listar backups
Write-Host "  - Listando backups..." -ForegroundColor Gray
try {
    $backupsList = Invoke-RestMethod -Uri "$BASE/backups/list" -Headers $headers
    Write-Host "    ✅ Total de backups: $($backupsList.total)" -ForegroundColor Green
    if ($backupsList.items.Count -gt 0) {
        $ultimoBackup = $backupsList.items[0]
        Write-Host "       Último: $($ultimoBackup.filename)" -ForegroundColor Gray
        
        # Descargar último backup
        Write-Host "  - Descargando último backup..." -ForegroundColor Gray
        try {
            $backupFilename = $ultimoBackup.filename
            Invoke-WebRequest -Uri "$BASE/backups/download/$backupFilename" -Headers $headers -OutFile ".\$backupFilename" -UseBasicParsing
            Write-Host "    ✅ Backup descargado: $backupFilename" -ForegroundColor Green
        } catch {
            Write-Host "    ❌ Error al descargar backup: $_" -ForegroundColor Red
        }
    }
} catch {
    Write-Host "    ❌ Error al listar backups: $_" -ForegroundColor Red
}
Write-Host ""

# 6. Resumen
Write-Host "[6/6] Resumen" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ Pruebas completadas" -ForegroundColor Green
Write-Host ""
Write-Host "Archivos generados:" -ForegroundColor Cyan
Get-ChildItem -Filter "*_export.*" | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor Gray }
Get-ChildItem -Filter "backup_*.sql.gz" | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor Gray }
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan


