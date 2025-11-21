# smoke_v0_9_1.ps1
# Quick smoke for Cobros + Recibo PDF + IVA Compras
# Usage (PowerShell):  .\smoke_v0_9_1.ps1

$ErrorActionPreference = "Stop"
$BASE = "http://localhost:8000"

Write-Host "== 0) Login admin ==" -ForegroundColor Cyan
$TOKEN = $null
try {
  $resp = Invoke-RestMethod "$BASE/auth/login" -Method POST `
    -ContentType "application/json" -Body '{"username":"admin","password":"admin123"}'
  $TOKEN = $resp.access_token
} catch { }
if (-not $TOKEN) {
  $resp = Invoke-RestMethod "$BASE/auth/oauth2/token" -Method POST `
    -ContentType "application/x-www-form-urlencoded" -Body "username=admin&password=admin123&grant_type=password"
  $TOKEN = $resp.access_token
}
if (-not $TOKEN) { throw "No pude obtener token. Verifica credenciales admin/admin123." }
$H = @{ "Authorization" = "Bearer $TOKEN"; "Content-Type" = "application/json" }
Write-Host "OK token" -ForegroundColor Green

function Ensure-Cliente {
  $cl = Invoke-RestMethod "$BASE/clientes?page=1&size=1" -Headers $H
  if ($cl.items.Count -gt 0) { return $cl.items[0].id }
  $nuevo = Invoke-RestMethod "$BASE/clientes" -Headers $H -Method POST `
    -Body (@{ nombre="Cliente QA"; telefono="5491100000000"; email="qa@nexouno.com" } | ConvertTo-Json)
  return $nuevo.id
}

function Ensure-Proveedor {
  $pr = Invoke-RestMethod "$BASE/proveedores?page=1&size=1" -Headers $H
  if ($pr.items.Count -gt 0) { return $pr.items[0].id }
  $nuevo = Invoke-RestMethod "$BASE/proveedores" -Headers $H -Method POST `
    -Body (@{ nombre="Proveedor QA"; telefono="1144444444"; email="prov@nexouno.com"; cuit="20123456789" } | ConvertTo-Json)
  return $nuevo.id
}

function Ensure-Producto {
  $p = Invoke-RestMethod "$BASE/productos?page=1&size=1" -Headers $H
  if ($p.items.Count -gt 0) { return $p.items[0].id }
  $provId = Ensure-Proveedor
  $nuevo = Invoke-RestMethod "$BASE/productos" -Headers $H -Method POST `
    -Body (@{ nombre="Bateria QA 12V"; precio=150000; stock=5; proveedor_id=$provId; codigo="BAT-QA" } | ConvertTo-Json)
  return $nuevo.id
}

function Ensure-Venta {
  $v = Invoke-RestMethod "$BASE/ventas?page=1&size=1" -Headers $H
  if ($v.items.Count -gt 0) { return $v.items[0].id }
  $cli = Ensure-Cliente
  $prod = Ensure-Producto
  $venta = Invoke-RestMethod "$BASE/ventas" -Headers $H -Method POST `
    -Body (@{ cliente_id=$cli; items=@(@{ producto_id=$prod; cantidad=1; precio_unitario=150000 }) } | ConvertTo-Json)
  return $venta.id
}

Write-Host "== 1) Ensure data (cliente, proveedor, producto, venta) ==" -ForegroundColor Cyan
$ventaId = Ensure-Venta
Write-Host "Venta ID: $ventaId" -ForegroundColor Green

Write-Host "== 2) Crear cobro ==" -ForegroundColor Cyan
$cobro = Invoke-RestMethod "$BASE/cobros" -Headers $H -Method POST `
  -Body (@{ venta_id=$ventaId; medio="EFECTIVO"; importe=1000; referencia="QA"; observaciones="smoke" } | ConvertTo-Json)
$cobroId = $cobro.id
Write-Host "Cobro ID: $cobroId" -ForegroundColor Green

Write-Host "== 3) Recibo PDF ==" -ForegroundColor Cyan
Invoke-WebRequest "$BASE/cobros/$cobroId/pdf" -Headers @{ "Authorization" = "Bearer $TOKEN" } -OutFile "recibo_$cobroId.pdf" -UseBasicParsing
Write-Host "PDF generado: recibo_$cobroId.pdf" -ForegroundColor Green

Write-Host "== 4) Saldo venta ==" -ForegroundColor Cyan
$saldo = Invoke-RestMethod "$BASE/cobros/venta/$ventaId/saldo" -Headers $H
$saldo | Format-Table | Out-String | Write-Host

Write-Host "== 5) IVA Compras: crear + export ==" -ForegroundColor Cyan
$compra = Invoke-RestMethod "$BASE/iva-compras" -Headers $H -Method POST `
  -Body (@{
    proveedor_nombre="Proveedor QA";
    fecha="2025-01-15"; tipo_cbte=6; pto_vta=1; nro_cbte=1234;
    doc_tipo=80; doc_nro="20123456789"; imp_neto=1000; imp_iva=210; imp_exento=0; imp_total=1210;
    alicuota_principal=21; moneda="ARS"; cotiz=1.0
  } | ConvertTo-Json)
Invoke-WebRequest "$BASE/iva-compras/export?desde=2025-01-01&hasta=2025-12-31&format=csv" `
  -Headers @{ "Authorization" = "Bearer $TOKEN" } -OutFile "iva_compras.csv" -UseBasicParsing
Write-Host "CSV generado: iva_compras.csv" -ForegroundColor Green

Write-Host "== SMOKE OK ==" -ForegroundColor Green
