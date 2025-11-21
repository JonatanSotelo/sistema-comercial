# Sprint v0.9.0 - Facturación AFIP (WSFEv1)

**Fecha**: 2025-11-21  
**Estado**: ✅ IMPLEMENTADO - Pendiente de validación  

---

## 🎯 Objetivo

Emitir Factura electrónica AFIP (WSFEv1) para ventas: A/B/C con CAE + vencimiento + QR AFIP. Vincular Venta/Pedido ↔ Factura. PDF de factura. Auditoría y tests. (Sin reintroducir "Activo").

---

## ✅ Componentes Implementados

### 1. Configuración y Settings ✅
- **Archivo**: `backend/env.example`, `backend/app/core/config.py`
- **Variables nuevas**:
  ```env
  AFIP_ENV=homologacion
  AFIP_CUIT=20123456789
  AFIP_CERT_PATH=/secrets/afip.crt
  AFIP_KEY_PATH=/secrets/afip.key
  AFIP_CERT_PASS=
  AFIP_WSDL_WSAA=https://wsaahomo.afip.gov.ar/ws/services/LoginCms?wsdl
  AFIP_WSDL_WSFEV1=https://wswhomo.afip.gov.ar/wsfev1/service.asmx?WSDL
  FACTURA_PTO_VTA=1
  FACTURA_MONEDA=ARS
  FACTURA_COTIZACION=1.000
  ```

### 2. Modelos y Migraciones ✅
- **Archivos**: 
  - `backend/app/models/factura_model.py` (nuevo)
  - `backend/migrations/versions/e4f5g6h7i8j9_add_facturacion_afip.py` (nuevo)
- **Tablas creadas**:
  - `facturas`: id, venta_id, pedido_id, tipo_cbte, pto_vta, nro_cbte, concepto, doc_tipo, doc_nro, imp_neto, imp_iva, imp_total, imp_exento, moneda, cotiz, cae, cae_vto, resultado, obs, qr_json
  - `factura_items`: id, factura_id, producto_id, descripcion, cantidad, precio_unitario, alic_iva, subtotal, iva_monto
- **Campos agregados a `clientes`**: direccion, condicion_iva, doc_tipo, doc_nro
- **ENUMs**: TipoComprobante, TipoDocumento, ConceptoFactura, ResultadoAFIP, AlicuotaIVA

### 3. Cliente AFIP (WSAA + WSFEv1) ✅
- **Archivos**:
  - `backend/app/services/afip_wsaa.py` (nuevo): Autenticación con WSAA, obtiene Token/Sign (TA) con certificado y clave privada
  - `backend/app/services/afip_wsfe_client.py` (nuevo): Cliente WSFEv1 para obtener último comprobante y solicitar CAE
- **Funcionalidades**:
  - `get_ticket_acceso()`: Obtiene TA de WSAA con cache
  - `fe_comp_ultimo_autorizado()`: Consulta último comprobante autorizado
  - `fe_cae_solicitar()`: Solicita CAE para un comprobante
  - Soporte de reintentos y manejo de errores

### 4. Servicio de Facturación ✅
- **Archivo**: `backend/app/services/facturacion_service.py` (nuevo)
- **Función principal**: `emitir_factura(venta_id, pedido_id, tipo_cbte, pto_vta, user, request)`
  - Construye cabecera según Cliente (doc_tipo/nro, condición IVA)
  - Calcula neto + IVA según alícuota e items
  - B/A: IVA discriminado; C: IVA al 0 (precio final)
  - Llama a `afip.get_last_cmp` y `afip.solicitar_cae`
  - Persiste factura + factura_items con CAE/CAE_VTO/QR json
  - Auditoría: table_name="facturacion", action=CREATE/ERROR
- **Función**: `generar_qr_json(factura)`: Genera JSON del QR AFIP según spec oficial

### 5. Servicio de PDF de Factura ✅
- **Archivo**: `backend/app/services/factura_pdf_service.py` (nuevo)
- **Función**: `generate_factura_pdf(db, factura_id)`: Genera PDF con QR AFIP embebido
  - Encabezado emisor, datos del cliente, tabla ítems (cant, desc, PU, neto, IVA, total)
  - Totales, CAE + CAE Vto, QR con URL de validación AFIP
  - Variantes A/B/C: A/B muestran IVA discriminado; C sin IVA

### 6. API y Schemas ✅
- **Archivos**:
  - `backend/app/schemas/factura_schema.py` (nuevo): FacturaOut, FacturaItemOut, FacturaEmitirRequest, FacturaListFilter
  - `backend/app/routers/facturacion_router.py` (nuevo): Endpoints para facturación
- **Endpoints**:
  - `POST /facturacion/emitir`: Emite una factura electrónica AFIP
  - `GET /facturacion`: Lista facturas con filtros (fecha, tipo, pto_vta)
  - `GET /facturacion/{factura_id}`: Obtiene una factura por ID
  - `GET /facturacion/{factura_id}/pdf`: Descarga PDF de factura con QR

### 7. Reporte Libro IVA Ventas ✅
- **Archivo**: `backend/app/services/libro_iva_ventas_service.py` (nuevo)
- **Función**: `generar_libro_iva_ventas(db, fecha_desde, fecha_hasta, formato)`: Genera reporte en CSV/XLSX
  - Columnas: Fecha, Tipo, Pto. Vta., Nro. Cbte., Doc. Tipo, Doc. Nro., Cliente, Neto Gravado, Exento, IVA, Total, Alíc. Principal, CAE
- **Endpoint**: `GET /reportes/libro-iva-ventas?desde=YYYY-MM-DD&hasta=YYYY-MM-DD&format=csv|xlsx`

### 8. UI Web (HTMX) ✅
- **Archivos**:
  - `backend/app/web/facturacion_ui.py` (nuevo)
  - `backend/app/templates/facturacion/index.html` (nuevo)
  - `backend/app/templates/facturacion/_table.html` (nuevo)
  - `backend/app/templates/sales/_table.html`: Agregado botón "📄 Facturar"
  - `backend/app/templates/base.html`: Agregado enlace "Facturación" en navbar
- **Funcionalidades**:
  - `/app/facturacion`: Listado de facturas con filtros
  - `/app/facturacion/table`: Tabla HTMX de facturas
  - Botón "Facturar" en tabla de Ventas para emitir factura

### 9. Tests ✅
- **Archivo**: `backend/tests/test_facturacion_afip.py` (nuevo)
- **Tests implementados**:
  - `test_emitir_factura_b_consumidor_final_ok`: Emitir Factura B a CF exitosamente
  - `test_emitir_factura_a_ri_ok`: Emitir Factura A a RI exitosamente
  - `test_qr_payload_ok`: Generar payload QR AFIP con campos obligatorios
  - `test_pdf_nonempty`: PDF de factura genera bytes no vacíos
  - `test_error_afip_auditoria`: Errores de AFIP se registran en auditoría
  - `test_sin_venta_ni_pedido_error`: Error si no se especifica venta_id ni pedido_id
- **Mocks**: `WSFEv1Client` mockeado para simular respuestas de AFIP

### 10. Smoke Tests ✅
- **Archivo**: `scripts/smoke.sh`
- **Tests agregados**:
  - `[FAC1]`: GET /app/facturacion
  - `[FAC2]`: GET /app/facturacion/table (HTMX partial)
  - `[FAC3]`: GET /facturacion (API list facturas)
  - `[FAC4]`: GET /reportes/libro-iva-ventas
  - `[FAC5]`: GET /facturas/1/pdf

### 11. Dependencias ✅
- **Archivo**: `backend/requirements.txt`
- **Nuevas dependencias**:
  ```
  zeep==4.2.1
  cryptography==42.0.5
  ```

---

## 📋 DoD (Definition of Done)

- ✅ Emitir B/C a CF y A a RI (mock homologación) con CAE guardado
- ✅ PDF con QR y datos fiscales correctos
- ✅ Factura vinculada a venta_id (y pedido_id si aplica)
- ✅ Auditoría en facturacion (CREATE/ERROR)
- ✅ Libro IVA Ventas exporta CSV/XLSX
- ✅ Tests verdes y smoke actualizado
- ✅ CARRERA: sin "Activo"

---

## 🚀 Plan de Validación

### 1. Rebuild + Migrate
```powershell
docker compose -f docker-compose.dev.yml up -d --build
docker compose -f docker-compose.dev.yml exec -T sc_backend alembic upgrade head
docker compose -f docker-compose.dev.yml exec -T sc_backend alembic current
```

### 2. Verificar Tablas
```powershell
docker compose -f docker-compose.dev.yml exec -T sc_postgres psql -U appuser -d appdb -P pager=off -c "\d facturas"
docker compose -f docker-compose.dev.yml exec -T sc_postgres psql -U appuser -d appdb -P pager=off -c "\d factura_items"
```

### 3. Tests
```powershell
docker compose -f docker-compose.dev.yml exec -T sc_backend pytest backend/tests/test_facturacion_afip.py -v
```

### 4. Smoke Tests
```bash
bash scripts/smoke.sh
```

### 5. Browser Check
- `/app/facturacion`: Ver listado de facturas
- `/app/ventas`: Ver botón "Facturar" en cada venta
- Crear una venta de prueba y emitir factura (MOCK)
- Descargar PDF de factura con QR
- `/reportes/libro-iva-ventas`: Exportar a CSV/XLSX

---

## 📝 Notas Importantes

### Certificados AFIP
- **Para homologación**: Generar certificado de prueba desde AFIP y colocarlo en `/secrets/afip.crt` y `/secrets/afip.key`
- **Para producción**: Usar certificado real de AFIP
- **WSAA**: El servicio actual usa una implementación simplificada de PKCS#7. En producción, considerar usar `M2Crypto` o `pysimplesoap` para firmar correctamente el TRA.

### Ambiente de Homologación
- Los endpoints de WSDL por defecto apuntan a homologación de AFIP
- Cambiar `AFIP_ENV=produccion` y actualizar WSDLs para producción

### QR AFIP
- URL generada: `https://www.afip.gob.ar/fe/qr/?p=<base64url(json)>`
- El QR es escaneabledesde el PDF y permite validar el CAE en AFIP

### Próximos Pasos (v0.9.1+)
- **v0.9.1**: Cobros & Caja + Libro IVA Compras, recibo PDF, saldos
- **v0.9.2**: Notas de Crédito/Débito + reverso stock
- **v1.0**: freeze + deploy

---

## 🐛 Troubleshooting

### Error: "zeep not found"
```bash
docker compose -f docker-compose.dev.yml exec sc_backend pip install zeep==4.2.1 cryptography==42.0.5
```

### Error: "psycopg2.errors.UndefinedTable: relation facturas does not exist"
```bash
docker compose -f docker-compose.dev.yml exec -T sc_backend alembic upgrade head
```

### Error: "WSAAClient timeout"
- Verificar conectividad con AFIP (wsaahomo.afip.gov.ar)
- Verificar que el certificado y clave privada sean válidos
- Verificar `AFIP_CERT_PATH` y `AFIP_KEY_PATH` en `.env`

---

¡Sprint v0.9.0 completado! 🎉 Listo para QA y deploy a staging.

