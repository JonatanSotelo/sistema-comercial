# 📊 FINAL STATUS - Sistema Comercial HTMX v0.9.x

**Fecha:** 2025-11-22  
**Branch Principal:** `main` (HTMX-first)  
**Última Versión Estable:** v0.9.1

---

## ✅ RESUMEN EJECUTIVO

| Ítem | Estado | Notas |
|------|--------|-------|
| Branch default | 🟡 PENDIENTE | Cambiar a `main` en GitHub Settings |
| Modelos & Imports | ⏳ EN VERIFICACIÓN | - |
| Migraciones Alembic | ⏳ EN VERIFICACIÓN | - |
| Requirements.txt | ⏳ EN VERIFICACIÓN | - |
| Docker Compose | ⏳ EN VERIFICACIÓN | - |
| Smoke Tests | ⏳ EN VERIFICACIÓN | - |
| CARRERA (sin "Activo") | ⏳ EN VERIFICACIÓN | - |

---

## 📋 1. AUDITORÍA DE BRANCHES

### Branch Default Remoto
```bash
# Ejecutar: git remote show origin | grep "HEAD branch"
```
**Resultado:** ⏳ PENDIENTE

**Acción requerida:** Cambiar default branch a `main` en:
- https://github.com/JonatanSotelo/sistema-comercial/settings/branches

### Tags Existentes
```bash
# Ejecutar: git tag -l
```
**Tags detectados:**
- `v0.9.1` - Cobros & Caja + IVA Compras (actual)
- `v0.9.0` - Facturación Electrónica AFIP
- `v0.8.0` - Notificaciones + Remito + Etiqueta
- `v0.7.5` - Reservas de Stock
- `v0.5.0` - Core + Proveedores

### Branches Locales y Remotas
```bash
# Ejecutar: git branch -vv
```
**Branches vivas:**
- `main` (HTMX, nueva línea principal) ✅
- `react-legacy` (backup histórico, no tocar) ✅
- `feat/ventas-stock-ui` (base de v0.9.1, puede archivarse)
- `chore/repo-cleanup-htmx-main` (trabajo temporal, borrar después del merge)

---

## 🗂️ 2. MODELOS Y BASE DE DATOS

### Modelos Detectados en `app/models/`
⏳ Verificando...

**Esperados:**
- [ ] `producto_model.py` → Producto
- [ ] `cliente_model.py` → Cliente
- [ ] `proveedor_model.py` → Proveedor
- [ ] `venta_model.py` → Venta, VentaItem
- [ ] `pedido_model.py` → Pedido, PedidoItem ⚠️ (ModuleNotFoundError reportado)
- [ ] `stock_reservation_model.py` → StockReservation
- [ ] `cobro_model.py` → Cobro
- [ ] `factura_model.py` → Factura, FacturaItem
- [ ] `purchase_invoice_model.py` → PurchaseInvoice
- [ ] `auditoria.py` → AuditLog

### Importación en `app/db/base.py`
⏳ Verificando...

### Routers Registrados

#### API (`app/routers/__init__.py`)
⏳ Verificando...

**Esperados:**
- ventas, compras, productos, clientes, proveedores
- pedidos, cobros, iva_compras, facturacion
- reportes, audit_logs, backups
- integrations_whatsapp

#### UI (`app/web/router.py`)
⏳ Verificando...

**Esperados:**
- auth, dashboard
- clientes, proveedores, productos
- ventas, compras, pedidos
- cobros, iva_compras, facturacion
- reportes, audit, backups
- integrations/whatsapp

---

## 📦 3. DEPENDENCIAS

### Requirements.txt
⏳ Verificando...

**Críticas esperadas:**
- [ ] fastapi, uvicorn[standard]
- [ ] sqlalchemy, alembic, psycopg2-binary
- [ ] httpx (notificaciones v0.8.0)
- [ ] reportlab (PDFs)
- [ ] qrcode[pil], Pillow (etiquetas con QR)
- [ ] zeep, cryptography (AFIP WSFEv1)
- [ ] openpyxl (export XLSX)
- [ ] python-jose[cryptography], passlib[bcrypt]
- [ ] python-multipart
- [ ] pydantic>=2.0

---

## 🐳 4. DOCKER COMPOSE

### Servicios Activos
⏳ Verificando `docker-compose.dev.yml`...

**Esperados:**
- [ ] sc_postgres (appdb, appuser)
- [ ] sc_redis
- [ ] sc_backend (puerto 8000)
- [ ] sc_pgadmin (puerto 5050)

### Volúmenes
- [ ] `./backups:/data/backups` (backups automáticos)
- [ ] `./backend:/app` (hot reload dev)

### Variables de Entorno Mínimas
- [ ] `DATABASE_URL` correcto (appuser, appdb)
- [ ] `SECRET_KEY` presente
- [ ] `BACKUP_DIR=/data/backups`

---

## 🗄️ 5. MIGRACIONES ALEMBIC

### Estado Actual
```bash
# Ejecutar: docker compose -f docker-compose.dev.yml exec sc_backend alembic current
```
**Head actual:** ⏳ PENDIENTE

### Últimas Migraciones Esperadas
- `f5g6h7i8j9k0_add_cobros_caja.py` (v0.9.1)
- `e4f5g6h7i8j9_add_facturacion_afip.py` (v0.9.0)
- `d3e4f5g6h7i8_add_venta_id_to_pedidos.py` (v0.8.0)
- `b2c3d4e5f6g7_add_stock_reservations.py` (v0.7.5)
- `a1b2c3d4e5f6_add_pedidos_module.py` (v0.7.0)

### Test de Imports
```bash
# Ejecutar script de verificación de imports
```
**Resultado:** ⏳ PENDIENTE

---

## 🧪 6. SMOKE TESTS

### Smoke Quick (bash)
```bash
# Ejecutar: bash smoke_quick.sh
```
**Resultado:** ⏳ PENDIENTE

### Checklist
- [ ] Login OAuth2 exitoso
- [ ] Ventas API responde
- [ ] Cobro creado OK
- [ ] PDF recibo generado (>1.5 KB)
- [ ] IVA Compras CSV generado (>200 bytes)
- [ ] Backups create/list OK

---

## 🎯 7. VERIFICACIONES ADICIONALES

### Reservas de Stock
- [ ] Lookup de productos muestra "Disponible: X"
- [ ] Crear pedido descuenta de disponible
- [ ] Facturar consume reservas

### Auditoría
- [ ] `/app/auditoria` carga (UI con sesión)
- [ ] API `/audit-logs` responde 200 con token

### Reportes
- [ ] `/app/reportes` carga
- [ ] Export CSV/XLSX funciona

### CARRERA (sin campo "Activo")
```bash
# Ejecutar: grep -r "is_active\|<th>Estado" app/templates/
```
**Resultado:** ⏳ PENDIENTE

**Criterio:** NO debe haber referencias a `is_active` ni columnas "Estado" tipo boolean en templates.

---

## 🔧 8. FIXES APLICADOS

### Commits de Corrección
⏳ Ninguno aún...

*Si se aplican fixes durante la auditoría, se documentarán aquí.*

---

## 📌 9. ACCIONES PENDIENTES

### Críticas (Antes de Release)
- [ ] Cambiar default branch a `main` en GitHub
- [ ] Ejecutar smoke tests completos
- [ ] Verificar que no hay referencias a campo "Activo"

### Recomendadas
- [ ] Renombrar `master` → `react-legacy`
- [ ] Borrar rama `chore/repo-cleanup-htmx-main` después del merge
- [ ] Archivar `feat/ventas-stock-ui` si ya no se usa

### Opcional
- [ ] Crear tag `v0.9.2` si hubo fixes de imports/deps

---

## 🏷️ 10. PROPUESTA DE TAG (Si aplica)

**Condición:** Si se aplicaron fixes de imports/modelos/deps.

```bash
git add .
git commit -m "release: v0.9.2 finalize HTMX main (imports/models/deps) + smoke quick"
git tag -a v0.9.2 -m "v0.9.2 - Finalize HTMX main: imports/models/deps fixes + smoke quick script"
git push origin main --tags
```

**Decisión:** ⏳ Evaluar después de auditoría completa

---

## 📝 NOTAS FINALES

### AFIP en Desarrollo
- ⚠️ WSFEv1 requiere certificados reales
- En dev: UI y rutas cargan, tests mockean correctamente
- No emitir facturas reales sin configuración de homologación

### Autenticación UI vs API
- UI (`/app/*`): Sesión con cookies (401 normal sin login)
- API: OAuth2 Bearer token (`/auth/oauth2/token`)

### React Legacy
- ✅ Preservado en rama `react-legacy`
- 🚫 No se mantiene activamente
- 📚 Solo referencia histórica

---

**Última Actualización:** ⏳ En progreso...  
**Auditor:** Cursor AI  
**Revisado por:** @JonatanSotelo

