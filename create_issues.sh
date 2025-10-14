#!/usr/bin/env bash
# Crea issues en GitHub usando gh CLI.
# Uso: export REPO=usuario/sistema-comercial && bash create_issues.sh
set -euo pipefail
REPO="${REPO:-}"
if [[ -z "$REPO" ]]; then echo "Definí REPO=owner/repo"; exit 1; fi
MILESTONE_V21="v2.1"
MILESTONE_V22="v2.2"
MILESTONE_V23="v2.3"
# Crear milestones si no existen
gh api repos/$REPO/milestones -q ".[]|.title" | grep -qx "$MILESTONE_V21" || gh api repos/$REPO/milestones -f title="$MILESTONE_V21" -f state=open >/dev/null
gh api repos/$REPO/milestones -q ".[]|.title" | grep -qx "$MILESTONE_V22" || gh api repos/$REPO/milestones -f title="$MILESTONE_V22" -f state=open >/dev/null
gh api repos/$REPO/milestones -q ".[]|.title" | grep -qx "$MILESTONE_V23" || gh api repos/$REPO/milestones -f title="$MILESTONE_V23" -f state=open >/dev/null

# v2.1 Issues
gh issue create -R "$REPO" -t "Migraciones de datos: estados y numeradores" -b "Agregar columnas `status` y `numero` en purchases/ventas/entregas. Definir enums y transiciones válidas.
**Criterios de aceptación**
- Estados normalizados
- Numeradores por documento
- Tests de transición (happy/error)" -m "$MILESTONE_V21" -l 'backend' -l 'migracion' -l 'estado' -l 'alta-prioridad'
gh issue create -R "$REPO" -t "Kardex: tabla inventory_moves + políticas" -b "Crear `inventory_moves` (IN/OUT) con referencias a documento origen y usuario. Definir política (reserva vs salida).
**Criterios**
- Movimientos en compras/recepciones/ventas/ajustes
- Auditoría visible
- Endpoint de historial por producto" -m "$MILESTONE_V21" -l 'backend' -l 'inventario' -l 'auditoria'
gh issue create -R "$REPO" -t "Depósitos/Ubicaciones + JSONB custom" -b "Tablas `depositos`, `ubicaciones` y `extra JSONB` en `stock_items`. UI para ver/editar claves configuradas.
**Criterios**
- CRUD depósitos/ubicaciones
- Consulta de stock por ubicación
- Soporte de campos personalizados" -m "$MILESTONE_V21" -l 'backend' -l 'frontend' -l 'inventario'
gh issue create -R "$REPO" -t "Adjuntos unificados (attachments)" -b "Tabla `attachments` + endpoints (subir, listar, borrar) y UI en compras/ventas/entregas.
**Criterios**
- Subir PDF/JPG/PNG
- Vista de adjuntos por documento
- Registro en auditoría" -m "$MILESTONE_V21" -l 'backend' -l 'frontend' -l 'archivos' -l 'auditoria'
gh issue create -R "$REPO" -t "Deliveries: creación, asignación y cierre" -b "Tabla `deliveries` + endpoints crear/asignar/cerrar. Adjuntar remito firmado al cerrar.
**Criterios**
- Estados Pendiente/Asignado/En tránsito/Entregado/Fallido
- Remito de entrega PDF
- Movimientos de stock coherentes" -m "$MILESTONE_V21" -l 'backend' -l 'frontend' -l 'logistica'
gh issue create -R "$REPO" -t "Productos: barcode + búsqueda por código" -b "Agregar `barcode` en productos y endpoints de búsqueda por código; input con autofocus para lectores.
**Criterios**
- Escaneo funciona como teclado
- Búsqueda por `barcode` o `sku`
- Filtro en ventas/stock" -m "$MILESTONE_V21" -l 'backend' -l 'frontend' -l 'ux'
gh issue create -R "$REPO" -t "Compras: aprobar y recepcionar (IN)" -b "Endpoints de aprobar/recepcionar; recepción parcial/total genera IN en kardex y actualiza `costo_ultimo`.
**Criterios**
- Recepción parcial
- Actualiza costo
- PDF/adjuntos visibles" -m "$MILESTONE_V21" -l 'backend' -l 'frontend' -l 'compras'
gh issue create -R "$REPO" -t "Ventas: facturar/remitir (OUT) + cliente genérico" -b "Endpoints de facturar/remitir; permitir cliente “Mostrador”. OUT en kardex según política.
**Criterios**
- Cliente genérico
- Remito/Factura interno
- Stock coherente" -m "$MILESTONE_V21" -l 'backend' -l 'frontend' -l 'ventas'
gh issue create -R "$REPO" -t "Dashboard: KPIs operativos" -b "Cards: ventas día/mes, top 5 productos, pendientes de entrega, compras abiertas, quiebres de stock.
**Criterios**
- API /dashboard/*
- Auto-refresh
- Export CSV" -m "$MILESTONE_V21" -l 'backend' -l 'frontend' -l 'dashboard'
gh issue create -R "$REPO" -t "Usuarios y roles: UI mínima" -b "UI para CRUD de usuarios y asignación de roles (ventas, compras, logística, contable, supervisor).
**Criterios**
- Ingreso/edición/activación
- Guardas en backend existentes
- Auditoría" -m "$MILESTONE_V21" -l 'frontend' -l 'seguridad' -l 'usuarios'
gh issue create -R "$REPO" -t "Reportes básicos (ventas/compras por fecha)" -b "Listado + filtros + export XLSX/PDF (simple). Dejar ganchos para rentabilidad.
**Criterios**
- Fecha desde/hasta
- Export XLSX/PDF
- Paginación" -m "$MILESTONE_V21" -l 'frontend' -l 'reportes'

# v2.2 Issues
gh issue create -R "$REPO" -t "Permisos granulares y guards en UI" -b "Aplicar permisos por rol a cada acción sensible (aprobar, recepcionar, facturar, cerrar entrega).
**Criterios**
- Protect en rutas
- Ocultar botones sin permiso
- Tests de autorización" -m "$MILESTONE_V22" -l 'frontend' -l 'seguridad' -l 'backend'
gh issue create -R "$REPO" -t "Auditoría: vista administrativa" -b "Pantalla para consultar `audit_log` (filtros: usuario, módulo, fecha) y export CSV.
**Criterios**
- Tabla con filtros
- Export CSV
- Link al registro origen" -m "$MILESTONE_V22" -l 'frontend' -l 'auditoria'
gh issue create -R "$REPO" -t "Precios y descuentos" -b "Soportar descuentos por línea y por documento; vista de listas de precios (si aplica).
**Criterios**
- Cálculo total coherente
- Mostrar en PDFs
- Validaciones UI" -m "$MILESTONE_V22" -l 'frontend' -l 'backend' -l 'ventas'
gh issue create -R "$REPO" -t "Notificaciones (operativas)" -b "Notificar a logística/ventas ante eventos: nueva entrega, entrega fallida, stock bajo (mock + webhook).
**Criterios**
- Servicio de eventos
- Webhook configurable
- Log de envíos" -m "$MILESTONE_V22" -l 'backend' -l 'infra' -l 'notificaciones'
gh issue create -R "$REPO" -t "Ruteo/Tracking v1 (mínimo viable)" -b "Microservicio de ruteo (mock/OSRM dev), PWA logística con lista de paradas, tracking público por token.
**Criterios**
- Plan de ruta simple
- Streaming posición 15–30s
- Marcar entregado/fallido + firma/foto" -m "$MILESTONE_V22" -l 'backend' -l 'frontend' -l 'mobile' -l 'logistica'
gh issue create -R "$REPO" -t "Etiquetas y códigos de barras (impresión)" -b "Generar/descargar etiquetas Code128/EAN para productos/ubicaciones.
**Criterios**
- PDF/PNG por lote
- Tamaños comunes
- Guardado de plantillas" -m "$MILESTONE_V22" -l 'frontend' -l 'backend' -l 'inventario'
gh issue create -R "$REPO" -t "CxC/CxP avanzado (parcialidades)" -b "Pagos parciales, notas de crédito/débito y cálculo de saldo por documento.
**Criterios**
- Registro de parcialidades
- Aplicación de notas
- Reporte de saldos" -m "$MILESTONE_V22" -l 'backend' -l 'frontend' -l 'finanzas'

# v2.3 Issues
gh issue create -R "$REPO" -t "Backups y restauración" -b "Backup programado de DB y adjuntos; botón de descarga y política de retención.
**Criterios**
- Cron en contenedor
- Retención configurables
- Restore documentado" -m "$MILESTONE_V23" -l 'infra' -l 'devops' -l 'seguridad'
gh issue create -R "$REPO" -t "Monitoring y métricas" -b "Health checks, logs estructurados y métricas básicas; alertas por umbrales.
**Criterios**
- /health extendido
- Panel básico
- Alertas" -m "$MILESTONE_V23" -l 'infra' -l 'monitoring' -l 'devops'
gh issue create -R "$REPO" -t "Integración AFIP e-Factura (A/B/C)" -b "Conexión a AFIP: puntos de venta, CAE, numeración fiscal; sandbox→prod.
**Criterios**
- Factura A/B/C con CAE
- Validaciones de condición IVA
- Logs de errores AFIP" -m "$MILESTONE_V23" -l 'backend' -l 'fiscal' -l 'integracion'
gh issue create -R "$REPO" -t "Ruteo/Tracking v2 (multi-vehículo)" -b "Optimización multi-vehículo y ventanas horarias; priorización por SLAs.
**Criterios**
- Asignación por capacidad
- Respeto de ventanas
- KPIs de cumplimiento" -m "$MILESTONE_V23" -l 'backend' -l 'frontend' -l 'mobile' -l 'logistica'
gh issue create -R "$REPO" -t "BI/Reportes avanzados" -b "Cubos y tableros avanzados (rentabilidad, cohortes de clientes, rotación de stock).
**Criterios**
- 3 dashboards
- Export masivo
- Jobs programados" -m "$MILESTONE_V23" -l 'frontend' -l 'backend' -l 'bi'