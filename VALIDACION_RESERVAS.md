# ✅ VALIDACIÓN DE RESERVAS - LISTA PARA QA

## 🎯 Objetivo
Implementar y validar el sistema de **soft stock reservations** para el módulo de Pedidos.

## 📋 Implementación Completada

### 1. ✅ Modelo y Migración
- **Archivo**: `backend/app/models/stock_reservation_model.py`
- **Tabla**: `stock_reservations`
- **Campos**: `id`, `pedido_id`, `pedido_item_id`, `producto_id`, `cantidad`, `estado` (RESERVADA, CANCELADA, CONSUMIDA), `created_at`, `updated_at`
- **Migración**: `backend/migrations/versions/b2c3d4e5f6g7_add_stock_reservations.py`
- **Índices**: 
  - `(producto_id, estado)` para consultas rápidas
  - Constraint único en `pedido_item_id`

### 2. ✅ Servicio de Reservas
- **Archivo**: `backend/app/services/stock_reservations_service.py`
- **Funciones principales**:
  - `ensure_reservas_for_pedido(pedido_id)`: Crea/ajusta reservas con row locking (`with_for_update()`)
  - `release_reservas_for_pedido(pedido_id)`: Cancela reservas activas
  - `consume_reservas_for_pedido(pedido_id)`: Marca como CONSUMIDA y descuenta stock
  - `get_disponible_producto(producto_id)`: Calcula disponible = stock - reservas_activas
  - `get_disponible_for_productos(producto_ids)`: Calcula disponible para múltiples productos (batch)

### 3. ✅ Hooks en Flujo de Pedidos
- **Archivo**: `backend/app/services/pedidos_service.py`
- **Transiciones que crean/ajustan reservas**:
  - `NUEVO → EN_PREPARACION`: Crea reservas
  - `EN_PREPARACION → LISTO`: Revalida reservas
  - `CUALQUIER_ESTADO → CANCELADO`: Libera reservas
- **Facturación**:
  - `facturar_pedido()`: Consume reservas y descuenta stock en la misma transacción

### 4. ✅ Actualización de Pedidos con Reservas
- **Lógica**: Al editar un pedido en `EN_PREPARACION`, se reajustan las reservas automáticamente
- **Validación**: No permite pasar a `EN_PREPARACION` si no hay disponible suficiente (409/400)

### 5. ✅ API y UI - Mostrar Disponible
- **Schema**: `backend/app/schemas/producto_schema.py` - Campo `disponible` agregado a `ProductoOut`
- **Router**: `backend/app/routers/producto_router.py` - Todos los endpoints de productos ahora calculan y devuelven `disponible`
- **Template**: `backend/app/templates/pedidos/_lookup_producto.html` - Muestra "Disponible: X" en verde/rojo según stock

### 6. ✅ Tests
- **Archivo**: `backend/tests/test_reservas.py`
- **Tests incluidos**:
  - `test_reserva_al_preparar`: Verifica que se crean reservas al pasar a EN_PREPARACION
  - `test_reserva_ajuste_cantidad`: Verifica que se ajustan reservas al editar pedido
  - `test_cancelacion_libera`: Verifica que se liberan reservas al cancelar
  - `test_facturar_consumo`: Verifica que se consumen reservas y se descuenta stock al facturar
  - `test_reserva_concurrencia`: Verifica que dos pedidos no pueden reservar más del disponible

### 7. ✅ Smoke Tests
- **Archivo**: `scripts/smoke.sh`
- **Tests de reservas agregados**:
  - `[R1]` Lookup de producto devuelve "Disponible"
  - `[R2]` API de productos incluye campo `disponible`
  - `[R3-R4]` Crear producto con stock limitado y pedidos
  - `[R5]` Pasar pedido 1 a EN_PREPARACION (crea reservas)
  - `[R6-R7]` Intentar pasar pedido 2 a EN_PREPARACION (debe fallar por falta de disponible)
  - `[R8]` Cancelar pedido 1 (libera reservas)
  - `[R9]` Ahora pedido 2 puede pasar a EN_PREPARACION

### 8. ✅ Auditoría
- **Eventos registrados**: CREATE, ADJUST, CANCEL, CONSUME
- **Tabla**: `reservas`
- **Detalles**: Incluyen `pedido_id`, `producto_id`, `cantidad` afectada

## 🚀 Comandos QA Express

### 1. Reconstruir y Migrar
```bash
docker compose -f docker-compose.dev.yml up -d --build
docker compose -f docker-compose.dev.yml exec sc_backend bash -lc "alembic upgrade head && alembic current"
```

### 2. Tests de Reservas
```bash
docker compose -f docker-compose.dev.yml exec sc_backend pytest backend/tests/test_reservas.py -q
```

### 3. Smoke Tests (incluye reservas)
```bash
./scripts/smoke.sh
```

### 4. Smoke Manual (Reservas Específicas)

#### Obtener Token
```bash
ADM=$(docker compose -f docker-compose.dev.yml exec -T sc_backend sh -lc \
"curl -s -X POST http://localhost:8000/auth/login -H 'Content-Type: application/json' \
-d '{\"username\":\"admin\",\"password\":\"admin\"}' | jq -r '.access_token // .token // .access'")

auth="Authorization: Bearer $ADM"
```

#### Crear Producto con Stock Limitado
```bash
PRODUCTO_ID=$(docker compose -f docker-compose.dev.yml exec -T sc_backend sh -lc \
"curl -s -X POST http://localhost:8000/productos -H \"$auth\" -H 'Content-Type: application/json' \
 -d '{\"nombre\":\"Producto Test Reservas\",\"codigo\":\"PTR001\",\"categoria\":\"TEST\",\"precio\":100.0,\"costo\":50.0,\"stock\":5}' | jq -r '.id'")

echo "Producto ID: $PRODUCTO_ID"
```

#### Crear Pedido 1 (3 unidades)
```bash
PEDIDO1_ID=$(docker compose -f docker-compose.dev.yml exec -T sc_backend sh -lc \
"curl -s -X POST http://localhost:8000/pedidos -H \"$auth\" -H 'Content-Type: application/json' \
 -d '{\"cliente_id\":null,\"items\":[{\"producto_id\":$PRODUCTO_ID,\"cantidad\":3,\"precio_unitario\":100.0}],\"nota\":\"P1\"}' | jq -r '.id'")

echo "Pedido 1 ID: $PEDIDO1_ID"
```

#### Pasar Pedido 1 a EN_PREPARACION (debe crear reservas)
```bash
docker compose -f docker-compose.dev.yml exec -T sc_backend sh -lc \
"curl -s -X POST http://localhost:8000/pedidos/$PEDIDO1_ID/estado -H \"$auth\" -H 'Content-Type: application/json' \
 -d '{\"estado\":\"EN_PREPARACION\"}' | jq '.estado'"
# Debe devolver: "EN_PREPARACION"
```

#### Verificar Disponible (debe ser 2 = 5 - 3)
```bash
docker compose -f docker-compose.dev.yml exec -T sc_backend sh -lc \
"curl -s http://localhost:8000/productos/$PRODUCTO_ID -H \"$auth\" | jq '.disponible'"
# Debe devolver: 2
```

#### Crear Pedido 2 (3 unidades)
```bash
PEDIDO2_ID=$(docker compose -f docker-compose.dev.yml exec -T sc_backend sh -lc \
"curl -s -X POST http://localhost:8000/pedidos -H \"$auth\" -H 'Content-Type: application/json' \
 -d '{\"cliente_id\":null,\"items\":[{\"producto_id\":$PRODUCTO_ID,\"cantidad\":3,\"precio_unitario\":100.0}],\"nota\":\"P2\"}' | jq -r '.id'")

echo "Pedido 2 ID: $PEDIDO2_ID"
```

#### Intentar Pasar Pedido 2 a EN_PREPARACION (debe fallar)
```bash
docker compose -f docker-compose.dev.yml exec -T sc_backend sh -lc \
"curl -i -s -X POST http://localhost:8000/pedidos/$PEDIDO2_ID/estado -H \"$auth\" -H 'Content-Type: application/json' \
 -d '{\"estado\":\"EN_PREPARACION\"}' | head -n 1"
# Debe devolver: HTTP/1.1 409 Conflict o 400 Bad Request
```

#### Cancelar Pedido 1 (libera reservas)
```bash
docker compose -f docker-compose.dev.yml exec -T sc_backend sh -lc \
"curl -s -X POST http://localhost:8000/pedidos/$PEDIDO1_ID/estado -H \"$auth\" -H 'Content-Type: application/json' \
 -d '{\"estado\":\"CANCELADO\"}' | jq '.estado'"
# Debe devolver: "CANCELADO"
```

#### Verificar Disponible Nuevamente (debe ser 5)
```bash
docker compose -f docker-compose.dev.yml exec -T sc_backend sh -lc \
"curl -s http://localhost:8000/productos/$PRODUCTO_ID -H \"$auth\" | jq '.disponible'"
# Debe devolver: 5
```

#### Ahora Pedido 2 puede pasar a EN_PREPARACION
```bash
docker compose -f docker-compose.dev.yml exec -T sc_backend sh -lc \
"curl -s -X POST http://localhost:8000/pedidos/$PEDIDO2_ID/estado -H \"$auth\" -H 'Content-Type: application/json' \
 -d '{\"estado\":\"EN_PREPARACION\"}' | jq '.estado'"
# Debe devolver: "EN_PREPARACION"
```

#### Ver Auditoría de Reservas
```bash
docker compose -f docker-compose.dev.yml exec -T sc_backend sh -lc \
"curl -s 'http://localhost:8000/app/auditoria?q=reservas' -H \"$auth\" | head -n 50"
```

## ✅ Resultado Esperado

### Tests Pytest
- ✅ 5/5 tests de reservas pasando

### Smoke Script
- ✅ [R1-R9] todos los tests de reservas pasando
- ✅ Lookup muestra "Disponible: X"
- ✅ API devuelve campo `disponible` en productos
- ✅ Concurrencia manejada correctamente (409/400 cuando no hay disponible)

### UI
- ✅ Lookup de productos muestra "Disponible" en verde (si > 0) o rojo (si = 0)
- ✅ Form de pedidos muestra stock y disponible

### Auditoría
- ✅ Eventos CREATE, ADJUST, CANCEL, CONSUME registrados en tabla `reservas`

## 🎯 Próximos Pasos (si RESERVAS OK)

1. **Tag v0.7.5**:
   ```bash
   git add .
   git commit -m "feat: soft stock reservations con hooks y auditoría"
   git tag -a v0.7.5 -m "Reservas de stock (soft reservations) con hooks y auditoría"
   git push origin v0.7.5
   ```

2. **Continuar con Sprint v0.8.0**:
   - Notificaciones WhatsApp/Email en LISTO
   - Remito de venta (HTML + PDF)
   - Etiqueta de pedido con QR

## 🐛 Si algo falla

Reportar:
- Status HTTP + mensaje de error
- Logs del backend: `docker compose -f docker-compose.dev.yml logs sc_backend | tail -50`
- Output de pytest: `docker compose -f docker-compose.dev.yml exec sc_backend pytest backend/tests/test_reservas.py -v`

---

**Fecha**: 2025-11-21  
**Versión**: v0.7.5 (Reservas)  
**Status**: ✅ LISTO PARA QA

