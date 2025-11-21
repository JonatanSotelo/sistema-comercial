# Smoke Test v0.9.1 - Cobros & Caja + IVA Compras
# PowerShell version

$BASE = "http://localhost:8000"
$ErrorActionPreference = "Stop"

Write-Host "`n🚀 SMOKE TEST v0.9.1 - Cobros & Caja" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

# 1. Login y obtener token
Write-Host "`n[1] Login..." -ForegroundColor Yellow
try {
    $loginBody = @{
        username = "admin"
        password = "admin"
    } | ConvertTo-Json

    $loginResponse = Invoke-RestMethod -Uri "$BASE/auth/login" -Method Post -Body $loginBody -ContentType "application/json"
    $TOKEN = $loginResponse.access_token
    
    if (-not $TOKEN) {
        $TOKEN = $loginResponse.token
    }
    
    if (-not $TOKEN) {
        throw "No se pudo obtener token"
    }
    
    Write-Host "✅ Token obtenido: $($TOKEN.Substring(0,20))..." -ForegroundColor Green
} catch {
    Write-Host "❌ Error en login: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $TOKEN"
    "Content-Type" = "application/json"
}

# 2. Crear/obtener cliente
Write-Host "`n[2] Verificando cliente..." -ForegroundColor Yellow
try {
    $clientes = Invoke-RestMethod -Uri "$BASE/clientes?size=1" -Headers $headers
    
    if ($clientes.items -and $clientes.items.Count -gt 0) {
        $clienteId = $clientes.items[0].id
        Write-Host "✅ Usando cliente existente ID: $clienteId" -ForegroundColor Green
    } else {
        # Crear cliente nuevo
        $nuevoCliente = @{
            nombre = "Cliente Test Cobros"
            email = "test@cobros.com"
            telefono = "1234567890"
        } | ConvertTo-Json
        
        $cliente = Invoke-RestMethod -Uri "$BASE/clientes" -Method Post -Body $nuevoCliente -Headers $headers
        $clienteId = $cliente.id
        Write-Host "✅ Cliente creado ID: $clienteId" -ForegroundColor Green
    }
} catch {
    Write-Host "[WARN] Error con clientes: $($_.Exception.Message)" -ForegroundColor Yellow
    $clienteId = 1
}

# 3. Crear/obtener producto
Write-Host "`n[3] Verificando producto..." -ForegroundColor Yellow
try {
    $productos = Invoke-RestMethod -Uri "$BASE/productos?size=1" -Headers $headers
    
    if ($productos.items -and $productos.items.Count -gt 0) {
        $productoId = $productos.items[0].id
        Write-Host "✅ Usando producto existente ID: $productoId" -ForegroundColor Green
    } else {
        # Crear producto nuevo
        $nuevoProducto = @{
            nombre = "Producto Test Cobros"
            codigo = "TESTCOB001"
            precio = 100.0
            costo = 50.0
            stock = 100
        } | ConvertTo-Json
        
        $producto = Invoke-RestMethod -Uri "$BASE/productos" -Method Post -Body $nuevoProducto -Headers $headers
        $productoId = $producto.id
        Write-Host "✅ Producto creado ID: $productoId" -ForegroundColor Green
    }
} catch {
    Write-Host "[WARN] Error con productos: $($_.Exception.Message)" -ForegroundColor Yellow
    $productoId = 1
}

# 4. Crear venta
Write-Host "`n[4] Creando venta..." -ForegroundColor Yellow
try {
    $nuevaVenta = @{
        cliente_id = $clienteId
        items = @(
            @{
                producto_id = $productoId
                cantidad = 2
                precio_unitario = 100.0
            }
        )
        total = 200.0
    } | ConvertTo-Json -Depth 5

    $venta = Invoke-RestMethod -Uri "$BASE/ventas" -Method Post -Body $nuevaVenta -Headers $headers
    $ventaId = $venta.id
    Write-Host "✅ Venta creada ID: $ventaId, Total: $($venta.total)" -ForegroundColor Green
} catch {
    Write-Host "❌ Error creando venta: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host $_.Exception.Response.StatusCode
    exit 1
}

# 5. Crear cobro
Write-Host "`n[5] Creando cobro..." -ForegroundColor Yellow
try {
    $nuevoCobro = @{
        venta_id = $ventaId
        medio = "EFECTIVO"
        importe = 100.0
        referencia = "Smoke test v0.9.1"
        observaciones = "Test automatizado"
    } | ConvertTo-Json

    $cobro = Invoke-RestMethod -Uri "$BASE/cobros" -Method Post -Body $nuevoCobro -Headers $headers
    $cobroId = $cobro.id
    Write-Host "✅ Cobro creado ID: $cobroId, Importe: $($cobro.importe), Estado: $($cobro.estado)" -ForegroundColor Green
} catch {
    Write-Host "❌ Error creando cobro: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 6. Verificar saldo de venta
Write-Host "`n[6] Verificando saldo venta..." -ForegroundColor Yellow
try {
    $saldo = Invoke-RestMethod -Uri "$BASE/cobros/venta/$ventaId/saldo" -Headers $headers
    Write-Host "✅ Saldo venta: $($saldo.saldo) (esperado: 100.0)" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Error obteniendo saldo: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 7. Descargar PDF del recibo
Write-Host "`n[7] Descargando recibo PDF..." -ForegroundColor Yellow
try {
    $pdfPath = "recibo_$cobroId.pdf"
    Invoke-WebRequest -Uri "$BASE/cobros/$cobroId/pdf" -Headers $headers -OutFile $pdfPath -UseBasicParsing
    
    $fileInfo = Get-Item $pdfPath
    if ($fileInfo.Length -gt 1000) {
        Write-Host "✅ Recibo PDF descargado: $pdfPath ($($fileInfo.Length) bytes)" -ForegroundColor Green
    } else {
        Write-Host "[WARN] Recibo PDF muy pequeno: $($fileInfo.Length) bytes" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Error descargando PDF: $($_.Exception.Message)" -ForegroundColor Red
}

# 8. Test IVA Compras - Crear registro
Write-Host "`n[8] Test IVA Compras..." -ForegroundColor Yellow
try {
    $nuevoIVACompra = @{
        proveedor_nombre = "Proveedor Test"
        fecha = "2025-01-15"
        tipo_cbte = 6
        pto_vta = 1
        nro_cbte = 9999
        doc_tipo = 80
        doc_nro = "20123456789"
        imp_neto = 100.0
        imp_iva = 21.0
        imp_exento = 0.0
        imp_total = 121.0
        alicuota_principal = 21.0
        moneda = "ARS"
        cotiz = 1.0
    } | ConvertTo-Json

    $ivaCompra = Invoke-RestMethod -Uri "$BASE/iva-compras" -Method Post -Body $nuevoIVACompra -Headers $headers
    Write-Host "✅ IVA Compra creado ID: $($ivaCompra.id)" -ForegroundColor Green
    
    # Exportar CSV
    $csvPath = "iva_compras_test.csv"
    Invoke-WebRequest -Uri "$BASE/reportes/libro-iva-compras?desde=2025-01-01&hasta=2025-12-31&format=csv" -Headers $headers -OutFile $csvPath -UseBasicParsing
    Write-Host "✅ IVA Compras CSV exportado: $csvPath" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Error con IVA Compras: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 9. Test Cuentas Corrientes
Write-Host "`n[9] Test Cuentas Corrientes..." -ForegroundColor Yellow
try {
    $cuentas = Invoke-RestMethod -Uri "$BASE/reportes/cuentas-corrientes?cliente_id=$clienteId" -Headers $headers
    Write-Host "✅ Cuentas corrientes OK: $($cuentas.Count) movimientos" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Error con cuentas corrientes: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 10. Verificar UI endpoints
Write-Host "`n[10] Verificando UI endpoints..." -ForegroundColor Yellow
$uiEndpoints = @(
    "/app/cobros",
    "/app/iva-compras",
    "/app/clientes"
)

foreach ($endpoint in $uiEndpoints) {
    try {
        $response = Invoke-WebRequest -Uri "$BASE$endpoint" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✅ $endpoint OK" -ForegroundColor Green
        }
    } catch {
        Write-Host "  [WARN] $endpoint - $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

Write-Host "`n" + ("=" * 50) -ForegroundColor Cyan
Write-Host "✅ SMOKE TEST v0.9.1 COMPLETADO" -ForegroundColor Green
Write-Host "`nArchivos generados:" -ForegroundColor Cyan
Write-Host "  - recibo_$cobroId.pdf" -ForegroundColor White
Write-Host "  - iva_compras_test.csv" -ForegroundColor White
Write-Host "`nRevisa los PDFs con:" -ForegroundColor Cyan
Write-Host "  Get-Item .\recibo_*.pdf | Select-Object Name,Length" -ForegroundColor White

