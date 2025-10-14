# Backlog de Issues — Alineación Backend vs Frontend ( 2025-10-14 )

> Extracto del análisis de Cursor:

# 🔍 ANÁLISIS: Backend vs Frontend Web ## Gap Analysis - Funcionalidades Pendientes **Fecha**: Octubre 13, 2025 **Versión**: 2.0.0 **Estado**: MVP Completado - Planificación v2.1+ --- ## 📊 RESUMEN EJECUTIVO ### ✅ IMPLEMENTADO EN FRONTEND (MVP v2.0) - **5 módulos core**: Productos, Clientes, Proveedores, Ventas, Compras - **CRUD completo** en todos los módulos - **Autenticación** básica (login/logout) - **Control de stock** automático - **Exportación** a XLSX ### ❌ PENDIENTE EN FRONTEND - **14 módulos avanzados** del backend sin interfaz web - **Dashboard** con métricas - **Administración** de usuarios y permisos - **Reportes** financieros - **Monitoreo** y auditoría ### 📈 Progreso ``` Backend API: 22 routers (100%) Frontend Web: 6 routers (27%) Pendiente: 16 módulos (73%) ``` --- ## 🗂️ COMPARATIVA DETALLADA ### ✅ MÓDULOS IMPLEMENTADOS (Frontend Web) | # | Módulo | Backend | Frontend | Endpoints | Completitud | |---|--------|---------|----------|-----------|-------------| | 1 | **Autenticación** | `auth_router.py` | `auth.py` | Login, Logout, Me | ✅ 100% | | 2 | **Productos** | `producto_router.py` | `productos.py` | CRUD + Export + Toggle | ✅ 100% | | 3 | **Clientes** | `cliente_router.py` | `clientes.py` | CRUD + Export | ✅ 100% | | 4 | **Proveedores** | `proveedor_router.py` | `proveedores.py` | CRUD + Export | ✅ 100% | | 5 | **Ventas** | `venta_router.py` | `ventas.py` | Create + List + Detail + Complete | ✅ 90% | | 6 | **Compras** | `compra_router.py` | `compras.py` | Create + List + Detail + Complete | ✅ 90% | **Total MVP**: 6 módulos completados ✅ --- ### ❌ MÓDULOS PENDIENTES (Sin Frontend Web) #### 🎯 PRIORIDAD ALTA (v2.1) | # | Módulo | Backend Router | Complejidad | Impacto | Endpoints Disponibles | |---|--------|----------------|-------------|---------|----------------------| | 1 | **Dashboard** | `dashboard_router.py` | 🟢 Media | ⭐⭐⭐⭐⭐ | GET /dashboard/stats, /dashboard/metrics | | 2 | **Usuarios** | `user_router.py` | 🟡 Media | ⭐⭐⭐⭐⭐ | CRUD users, roles, activate/deactivate | | 3 | **Inventario** | `inventario_router.py` | 🟡 Media | ⭐⭐⭐⭐ | Movimientos stock, ajustes, historial | | 4 | **Reportes** | `reporte_financiero_router.py` | 🔴 Alta | ⭐⭐⭐⭐ | Ventas, compras, rentabilidad, gráficos | **Estimación**: 40-60 horas de desarrollo --- #### 🎯 PRIORIDAD MEDIA (v2.2) | # | Módulo | Backend Router | Complejidad | Impacto | Endpoints Disponibles | |---|--------|----------------|-------------|---------|----------------------| | 5 | **Permisos/Roles** | `permiso_router.py` | 🟡 Media | ⭐⭐⭐⭐ | CRUD roles, assign permissions | | 6 | **Descuentos** | `descuento_router.py` |...

## Releases y módulos

### v2.1 — Núcleo Operativo (evitar refactors)

**Issue:** Migraciones de datos: estados y numeradores

Agregar columnas `status` y `numero` en purchases/ventas/entregas. Definir enums y transiciones válidas.
**Criterios de aceptación**
- Estados normalizados
- Numeradores por documento
- Tests de transición (happy/error)

**Labels:** `backend`, `migracion`, `estado`, `alta-prioridad`

---

**Issue:** Kardex: tabla inventory_moves + políticas

Crear `inventory_moves` (IN/OUT) con referencias a documento origen y usuario. Definir política (reserva vs salida).
**Criterios**
- Movimientos en compras/recepciones/ventas/ajustes
- Auditoría visible
- Endpoint de historial por producto

**Labels:** `backend`, `inventario`, `auditoria`

---

**Issue:** Depósitos/Ubicaciones + JSONB custom

Tablas `depositos`, `ubicaciones` y `extra JSONB` en `stock_items`. UI para ver/editar claves configuradas.
**Criterios**
- CRUD depósitos/ubicaciones
- Consulta de stock por ubicación
- Soporte de campos personalizados

**Labels:** `backend`, `frontend`, `inventario`

---

**Issue:** Adjuntos unificados (attachments)

Tabla `attachments` + endpoints (subir, listar, borrar) y UI en compras/ventas/entregas.
**Criterios**
- Subir PDF/JPG/PNG
- Vista de adjuntos por documento
- Registro en auditoría

**Labels:** `backend`, `frontend`, `archivos`, `auditoria`

---

**Issue:** Deliveries: creación, asignación y cierre

Tabla `deliveries` + endpoints crear/asignar/cerrar. Adjuntar remito firmado al cerrar.
**Criterios**
- Estados Pendiente/Asignado/En tránsito/Entregado/Fallido
- Remito de entrega PDF
- Movimientos de stock coherentes

**Labels:** `backend`, `frontend`, `logistica`

---

**Issue:** Productos: barcode + búsqueda por código

Agregar `barcode` en productos y endpoints de búsqueda por código; input con autofocus para lectores.
**Criterios**
- Escaneo funciona como teclado
- Búsqueda por `barcode` o `sku`
- Filtro en ventas/stock

**Labels:** `backend`, `frontend`, `ux`

---

**Issue:** Compras: aprobar y recepcionar (IN)

Endpoints de aprobar/recepcionar; recepción parcial/total genera IN en kardex y actualiza `costo_ultimo`.
**Criterios**
- Recepción parcial
- Actualiza costo
- PDF/adjuntos visibles

**Labels:** `backend`, `frontend`, `compras`

---

**Issue:** Ventas: facturar/remitir (OUT) + cliente genérico

Endpoints de facturar/remitir; permitir cliente “Mostrador”. OUT en kardex según política.
**Criterios**
- Cliente genérico
- Remito/Factura interno
- Stock coherente

**Labels:** `backend`, `frontend`, `ventas`

---

**Issue:** Dashboard: KPIs operativos

Cards: ventas día/mes, top 5 productos, pendientes de entrega, compras abiertas, quiebres de stock.
**Criterios**
- API /dashboard/*
- Auto-refresh
- Export CSV

**Labels:** `backend`, `frontend`, `dashboard`

---

**Issue:** Usuarios y roles: UI mínima

UI para CRUD de usuarios y asignación de roles (ventas, compras, logística, contable, supervisor).
**Criterios**
- Ingreso/edición/activación
- Guardas en backend existentes
- Auditoría

**Labels:** `frontend`, `seguridad`, `usuarios`

---

**Issue:** Reportes básicos (ventas/compras por fecha)

Listado + filtros + export XLSX/PDF (simple). Dejar ganchos para rentabilidad.
**Criterios**
- Fecha desde/hasta
- Export XLSX/PDF
- Paginación

**Labels:** `frontend`, `reportes`

---

### v2.2 — Seguridad y Entregas Inteligentes

**Issue:** Permisos granulares y guards en UI

Aplicar permisos por rol a cada acción sensible (aprobar, recepcionar, facturar, cerrar entrega).
**Criterios**
- Protect en rutas
- Ocultar botones sin permiso
- Tests de autorización

**Labels:** `frontend`, `seguridad`, `backend`

---

**Issue:** Auditoría: vista administrativa

Pantalla para consultar `audit_log` (filtros: usuario, módulo, fecha) y export CSV.
**Criterios**
- Tabla con filtros
- Export CSV
- Link al registro origen

**Labels:** `frontend`, `auditoria`

---

**Issue:** Precios y descuentos

Soportar descuentos por línea y por documento; vista de listas de precios (si aplica).
**Criterios**
- Cálculo total coherente
- Mostrar en PDFs
- Validaciones UI

**Labels:** `frontend`, `backend`, `ventas`

---

**Issue:** Notificaciones (operativas)

Notificar a logística/ventas ante eventos: nueva entrega, entrega fallida, stock bajo (mock + webhook).
**Criterios**
- Servicio de eventos
- Webhook configurable
- Log de envíos

**Labels:** `backend`, `infra`, `notificaciones`

---

**Issue:** Ruteo/Tracking v1 (mínimo viable)

Microservicio de ruteo (mock/OSRM dev), PWA logística con lista de paradas, tracking público por token.
**Criterios**
- Plan de ruta simple
- Streaming posición 15–30s
- Marcar entregado/fallido + firma/foto

**Labels:** `backend`, `frontend`, `mobile`, `logistica`

---

**Issue:** Etiquetas y códigos de barras (impresión)

Generar/descargar etiquetas Code128/EAN para productos/ubicaciones.
**Criterios**
- PDF/PNG por lote
- Tamaños comunes
- Guardado de plantillas

**Labels:** `frontend`, `backend`, `inventario`

---

**Issue:** CxC/CxP avanzado (parcialidades)

Pagos parciales, notas de crédito/débito y cálculo de saldo por documento.
**Criterios**
- Registro de parcialidades
- Aplicación de notas
- Reporte de saldos

**Labels:** `backend`, `frontend`, `finanzas`

---

### v2.3 — Confiabilidad y Fiscal

**Issue:** Backups y restauración

Backup programado de DB y adjuntos; botón de descarga y política de retención.
**Criterios**
- Cron en contenedor
- Retención configurables
- Restore documentado

**Labels:** `infra`, `devops`, `seguridad`

---

**Issue:** Monitoring y métricas

Health checks, logs estructurados y métricas básicas; alertas por umbrales.
**Criterios**
- /health extendido
- Panel básico
- Alertas

**Labels:** `infra`, `monitoring`, `devops`

---

**Issue:** Integración AFIP e-Factura (A/B/C)

Conexión a AFIP: puntos de venta, CAE, numeración fiscal; sandbox→prod.
**Criterios**
- Factura A/B/C con CAE
- Validaciones de condición IVA
- Logs de errores AFIP

**Labels:** `backend`, `fiscal`, `integracion`

---

**Issue:** Ruteo/Tracking v2 (multi-vehículo)

Optimización multi-vehículo y ventanas horarias; priorización por SLAs.
**Criterios**
- Asignación por capacidad
- Respeto de ventanas
- KPIs de cumplimiento

**Labels:** `backend`, `frontend`, `mobile`, `logistica`

---

**Issue:** BI/Reportes avanzados

Cubos y tableros avanzados (rentabilidad, cohortes de clientes, rotación de stock).
**Criterios**
- 3 dashboards
- Export masivo
- Jobs programados

**Labels:** `frontend`, `backend`, `bi`

---
