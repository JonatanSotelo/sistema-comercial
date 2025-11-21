# Test simple v0.9.1 - Cobros & Caja
$ErrorActionPreference = "Continue"
$BASE = "http://localhost:8000"

Write-Host ""
Write-Host "SMOKE TEST v0.9.1 - Cobros & Caja" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

# 1. Login
Write-Host ""
Write-Host "[1] Login..." -ForegroundColor Yellow
try {
    $body = '{"username":"admin","password":"admin123"}'
    $login = Invoke-RestMethod -Uri "$BASE/auth/login" -Method Post -Body $body -ContentType "application/json"
    $TOKEN = $login.access_token
    if (-not $TOKEN) { $TOKEN = $login.token }
    Write-Host "[OK] Token: $($TOKEN.Substring(0,15))..." -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Login failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

$h = @{ "Authorization" = "Bearer $TOKEN"; "Content-Type" = "application/json" }

# 2. Get cliente
Write-Host ""
Write-Host "[2] Cliente..." -ForegroundColor Yellow
try {
    $clientes = Invoke-RestMethod -Uri "$BASE/clientes?size=1" -Headers $h
    if ($clientes.items -and $clientes.items.Count -gt 0) {
        $cid = $clientes.items[0].id
    } else {
        $cid = 1
    }
    Write-Host "[OK] Cliente ID: $cid" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Using cliente_id=1" -ForegroundColor Yellow
    $cid = 1
}

# 3. Crear producto de prueba con stock
Write-Host ""
Write-Host "[3] Producto..." -ForegroundColor Yellow
try {
    $prodBody = @{
        nombre = "Test Cobros v091"
        codigo = "TESTCOB$(Get-Random -Maximum 9999)"
        categoria = "TEST"
        precio = 100.0
        costo = 50.0
        stock = 1000
        stock_minimo = 0
    } | ConvertTo-Json
    
    $prod = Invoke-RestMethod -Uri "$BASE/productos/" -Method Post -Body $prodBody -Headers $h -ContentType "application/json"
    $prodId = $prod.id
    Write-Host "[OK] Producto creado ID: $prodId (stock: 1000)" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Error creando producto, usando ID=1" -ForegroundColor Yellow
    $prodId = 1
}

# 4. Crear venta
Write-Host ""
Write-Host "[4] Crear venta..." -ForegroundColor Yellow
try {
    $ventaBody = @{
        cliente_id = $cid
        items = @(@{
            producto_id = $prodId
            cantidad = 2
            precio_unitario = 100.0
        })
        total = 200.0
    } | ConvertTo-Json -Depth 5

    $venta = Invoke-RestMethod -Uri "$BASE/ventas/" -Method Post -Body $ventaBody -Headers $h -ContentType "application/json"
    $vid = $venta.id
    Write-Host "[OK] Venta ID: $vid, Total: $($venta.total)" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Venta failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "  StatusCode: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
    Write-Host "  Body sent: $ventaBody" -ForegroundColor Yellow
    exit 1
}

# 5. Crear cobro
Write-Host ""
Write-Host "[5] Crear cobro..." -ForegroundColor Yellow
try {
    $cobroBody = @{
        venta_id = $vid
        medio = "EFECTIVO"
        importe = 100.0
        referencia = "Test smoke"
        observaciones = "Automatizado"
    } | ConvertTo-Json

    $cobro = Invoke-RestMethod -Uri "$BASE/cobros/" -Method Post -Body $cobroBody -Headers $h -ContentType "application/json"
    $cobid = $cobro.id
    Write-Host "[OK] Cobro ID: $cobid, Importe: $($cobro.importe)" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Cobro failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 6. Saldo
Write-Host ""
Write-Host "[6] Saldo venta..." -ForegroundColor Yellow
try {
    $saldo = Invoke-RestMethod -Uri "$BASE/cobros/venta/$vid/saldo" -Headers $h
    Write-Host "[OK] Saldo: $($saldo.saldo)" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Saldo failed" -ForegroundColor Yellow
}

# 7. PDF Recibo
Write-Host ""
Write-Host "[7] PDF Recibo..." -ForegroundColor Yellow
try {
    $pdfFile = "recibo_$cobid.pdf"
    Invoke-WebRequest -Uri "$BASE/cobros/$cobid/pdf" -Headers $h -OutFile $pdfFile -UseBasicParsing
    $size = (Get-Item $pdfFile).Length
    if ($size -gt 1000) {
        Write-Host "[OK] PDF: $pdfFile ($size bytes)" -ForegroundColor Green
    } else {
        Write-Host "[WARN] PDF small: $size bytes" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[ERROR] PDF failed: $($_.Exception.Message)" -ForegroundColor Red
}

# 8. IVA Compras
Write-Host ""
Write-Host "[8] IVA Compras..." -ForegroundColor Yellow
try {
    $ivaBody = @{
        proveedor_nombre = "Test Prov"
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

    $iva = Invoke-RestMethod -Uri "$BASE/iva-compras/" -Method Post -Body $ivaBody -Headers $h -ContentType "application/json"
    Write-Host "[OK] IVA Compra ID: $($iva.id)" -ForegroundColor Green
    
    $csvFile = "iva_compras.csv"
    Invoke-WebRequest -Uri "$BASE/reportes/libro-iva-compras?desde=2025-01-01&hasta=2025-12-31&format=csv" -Headers $h -OutFile $csvFile -UseBasicParsing
    Write-Host "[OK] CSV: $csvFile" -ForegroundColor Green
} catch {
    Write-Host "[WARN] IVA Compras: $($_.Exception.Message)" -ForegroundColor Yellow
}

# 9. UI endpoints
Write-Host ""
Write-Host "[9] UI endpoints..." -ForegroundColor Yellow
$endpoints = @("/app/cobros", "/app/iva-compras")
foreach ($ep in $endpoints) {
    try {
        $r = Invoke-WebRequest -Uri "$BASE$ep" -UseBasicParsing -TimeoutSec 3
        if ($r.StatusCode -eq 200) {
            Write-Host "[OK] $ep" -ForegroundColor Green
        }
    } catch {
        Write-Host "[WARN] $ep failed" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "SMOKE TEST COMPLETADO" -ForegroundColor Green
Write-Host ""
Write-Host "Archivos generados:" -ForegroundColor Cyan
Write-Host "  - recibo_$cobid.pdf"
Write-Host "  - iva_compras.csv"
Write-Host ""

