# v0.7.5 — Reservas + FK Fix

## ✨ Nuevas Funcionalidades

### Soft Stock Reservations
- **NUEVO → EN_PREPARACION**: Crea reservas automáticas por cada item del pedido
- **FACTURAR**: Consume reservas y descuenta stock en transacción atómica
- **CANCELAR**: Libera reservas (marca como CANCELADA)
- **Edición de pedidos**: Reajusta reservas automáticamente si el pedido está EN_PREPARACION

### UI - Stock Disponible
- **Lookups de productos**: Muestra "Disponible: X" en verde (si > 0) o rojo (si = 0)
- **Cálculo**: `Disponible = stock - sum(reservas RESERVADA)`
- **API**: Campo `disponible` en todos los endpoints de productos

### Auditoría de Reservas
- **Eventos**: CREATE, ADJUST, CANCEL, CONSUME
- **Tabla**: `reservas`
- **Detalles**: `pedido_id`, `producto_id`, `cantidad` afectada

## 🔧 Fixes

### Foreign Keys a `users`
- **Fix robusto**: Migración `fix_users_fks` que asegura que todas las FKs apunten a `users(id)` (no `usuarios`)
- **Tablas corregidas**: `audit_logs`, `pedidos`, y otras 24 tablas
- **Validado**: 26 FKs correctas, 0 FKs obsoletas

## 📚 Documentación y Herramientas

### Scripts de Chequeo
- **`scripts/sql/check_fks_users.sql`**: Diagnóstico SQL de FKs a users
- **`scripts/check_db_fks.ps1`**: Script PowerShell para Windows
- **`scripts/check_db_fks.sh`**: Script Bash para Linux/Mac

### Documentación
- **`docs/DEV_DATABASE_CHECKS.md`**: Guía completa de checks de DB, troubleshooting y convenciones
- **Anti-pager**: Todos los comandos `psql` usan `-P pager=off` para evitar bloqueos de terminal

## 🗄️ Base de Datos

### Nuevas Tablas
- **`stock_reservations`**: Gestión de reservas de stock
  - Campos: `id`, `pedido_id`, `pedido_item_id`, `producto_id`, `cantidad`, `estado`, timestamps
  - Índices optimizados: `(producto_id, estado)`, constraint único en `pedido_item_id`

### Migraciones
- `a1b2c3d4e5f6_add_pedidos_module.py` - Pedidos y items (corregida FK a `users`)
- `b2c3d4e5f6g7_add_stock_reservations.py` - Tabla de reservas
- `c1d2e3f4g5h6_fix_users_fks.py` - Fix automático de FKs obsoletas

## 🧪 Tests

### Nuevos Tests
- `test_reserva_al_preparar`: Verifica creación de reservas
- `test_reserva_ajuste_cantidad`: Verifica ajuste al editar
- `test_cancelacion_libera`: Verifica liberación al cancelar
- `test_facturar_consumo`: Verifica consumo y descuento de stock
- `test_reserva_concurrencia`: Verifica que no se puede reservar más del disponible

### Smoke Tests
- **[R1-R9]**: Tests completos de flujo de reservas
- Validación de lookup con disponible
- Test de concurrencia (409/400 cuando no hay stock)

## 🔒 Seguridad y Calidad

### Row Locking
- `SELECT ... FOR UPDATE` en operaciones críticas de reservas
- Previene race conditions en actualizaciones concurrentes

### Validaciones
- No permite pasar a EN_PREPARACION si no hay disponible suficiente
- Valida stock antes de consumir reservas
- Transacciones atómicas para garantizar consistencia

## 📋 Convenciones Mantenidas

- ✅ No reintroduce campo "Activo"
- ✅ Mantiene HTMX + OOB swap
- ✅ Auditoría completa en todas las operaciones
- ✅ CARRERA: código limpio y consistente

## 🚀 Deploy

```bash
# 1. Rebuild containers
docker compose -f docker-compose.dev.yml up -d --build

# 2. Run migrations
docker compose -f docker-compose.dev.yml exec -T sc_backend alembic upgrade head

# 3. Verify FK health
./scripts/check_db_fks.ps1  # Windows
bash scripts/check_db_fks.sh  # Linux/Mac

# 4. Smoke tests
./scripts/smoke.sh
```

## 📊 Estadísticas

- **Archivos nuevos**: 7
- **Archivos modificados**: 12
- **Tests nuevos**: 5
- **Migraciones**: 3
- **Scripts de utilidad**: 3
- **Documentación**: 2

---

**Fecha de Release:** 2025-11-21  
**Autor:** Sistema Comercial Team  
**Próximo Sprint:** v0.8.0 - Notificaciones + Remito + Etiqueta

