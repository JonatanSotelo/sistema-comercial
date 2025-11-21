# Release v0.5.0 - Integración WhatsApp → Venta (MVP) + Auditoría + Reportes + Import/Export + Backups

## Highlights

### 🛒 Ventas/Compras con Stock Transaccional
- Validación de stock antes de crear ventas/compras
- Error 409 si no hay stock suficiente
- Ajuste automático de stock al confirmar ventas/compras

### 📋 Auditoría Completa
- UI en `/app/auditoria` con filtros avanzados
- Logs de todas las operaciones (CREATE, UPDATE, DELETE, ADJUST)
- Auditoría de integraciones y ajustes de stock
- Filtros por tabla, usuario, fecha, acción

### 📊 Reportes Financieros
- Reportes de ventas/compras por día/cliente/proveedor/producto
- Exportación a CSV/XLSX
- Historial de reportes generados
- Endpoint `/reportes-financieros/ultimo` para obtener el último reporte

### 📥 Import/Export CSV/XLSX
- **Export**: Clientes, Proveedores, Productos (CSV/XLSX)
- **Import**: Con preview (dry_run) antes de confirmar
- Validaciones y manejo de errores
- Upsert inteligente (actualiza si existe, crea si no)

### 💾 Backups Automáticos
- Crear backups manuales desde `/app/backups`
- Job diario automático a las 02:30 (configurable)
- Listar y descargar backups
- Archivos comprimidos (.sql.gz) en `./backups/`

### 📱 Integración WhatsApp → Venta (MVP)
- Endpoint `POST /integrations/whatsapp/orders`
- **Cotización** (`confirm=false`): No toca stock, solo calcula total
- **Venta confirmada** (`confirm=true`): Crea venta y descuenta stock
- Resolución de productos por:
  - `product_id`: Directo
  - `codigo`: Búsqueda por código
  - `query`: Búsqueda por nombre (fuzzy match)
- Resolución de clientes por teléfono
- Autenticación por header `X-Integration-Token`
- UI de monitoreo en `/app/integraciones/whatsapp`

## Breaking Changes / Notas Importantes

### ⚠️ Variables de Entorno Requeridas
- **NUEVO**: `WHATS_ORDERS_TOKEN`: Token secreto para autenticación de integración WhatsApp
  - Agregar a `backend/.env` (NO commitear tokens)
  - Ejemplo en `backend/env.example`

### 🔧 Dependencias
- **PostgreSQL Client**: Si falta `pg_dump`, instalar cliente Postgres en imagen backend:
  ```dockerfile
  RUN apt-get update && apt-get install -y postgresql-client
  ```
  O usar el contenedor de Postgres para ejecutar `pg_dump`

### 📝 Migraciones
- Enum `auditaction` actualizado con valor `ADJUST` para ajustes de stock
- Ejecutar: `alembic upgrade head`

## Mejoras Técnicas

- Tests automatizados para integración WhatsApp (6 tests)
- Mejora en manejo de errores y validaciones
- UI mejorada con HTMX para mejor UX
- Documentación actualizada

## Post-Tag Checklist

- [x] `backend/env.example` actualizado con `WHATS_ORDERS_TOKEN`
- [ ] Verificar en logs del backend: job `daily_backup` registrado (02:30 -03:00)
- [ ] Confirmar que `./backups/` del host recibe archivos nuevos
- [ ] Verificar UI: `/app/integraciones/whatsapp`, `/app/auditoria`, `/app/reportes`
- [ ] Sin campos "Activo" en formularios/tablas (CARRERA)

## Próximos Pasos

1. **Deploy dev** en DO App Platform (backend + Postgres gestionado o container)
2. **Bot WhatsApp**: Apuntar webhook a micro-backend y usar endpoint del Sistema
   - Token → `X-Integration-Token`
   - Flujo: mensaje → parse → `POST /integrations/whatsapp/orders`

## Archivos Principales Modificados

- `backend/app/routers/integrations_whatsapp_router.py` - Nueva integración
- `backend/app/services/integrations/whatsapp_orders_service.py` - Lógica de negocio
- `backend/app/routers/audit_log_router.py` - Auditoría
- `backend/app/routers/reportes_router.py` - Reportes
- `backend/app/routers/backup_router.py` - Backups
- `backend/app/services/import_export_service.py` - Import/Export
- `backend/tests/test_integrations_whatsapp.py` - Tests

## Contribuidores

- Desarrollo y QA completado
- Tests automatizados: ✅ 6/6 pasando
- QA E2E: ✅ Completada

---

**Tag**: `v0.5.0`  
**Fecha**: 2025-11-14  
**Estado**: ✅ Listo para producción


