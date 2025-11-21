# Check Foreign Keys to users table
# Usage: .\scripts\check_db_fks.ps1

Param(
    [string]$ComposeFile = "docker-compose.dev.yml",
    [string]$User = "appuser",
    [string]$Database = "appdb"
)

Write-Host "`n=== Checking Foreign Keys to users table ===" -ForegroundColor Cyan

# Verificar que el contenedor esté corriendo
$running = docker ps --filter "name=sc_postgres" --format "{{.Names}}"
if (-not $running) {
    Write-Host "ERROR: Container sc_postgres is not running" -ForegroundColor Red
    Write-Host "Run: docker compose -f $ComposeFile up -d" -ForegroundColor Yellow
    exit 1
}

# Verificar que el archivo SQL existe
$sqlFile = "scripts/sql/check_fks_users.sql"
if (-not (Test-Path $sqlFile)) {
    Write-Host "ERROR: $sqlFile not found" -ForegroundColor Red
    exit 1
}

# Ejecutar el check (con pager deshabilitado)
$cmd = "docker compose -f $ComposeFile exec -T sc_postgres psql -U $User -d $Database -P pager=off -f /app/$sqlFile"

try {
    Write-Host "Running: $cmd" -ForegroundColor Gray
    Invoke-Expression $cmd
    
    Write-Host "`n=== Check completed ===" -ForegroundColor Green
    Write-Host "If you see FKs pointing to 'usuarios', run the fix migration:" -ForegroundColor Yellow
    Write-Host "  docker compose -f $ComposeFile exec -T sc_backend alembic upgrade head" -ForegroundColor Yellow
}
catch {
    Write-Host "`nERROR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

