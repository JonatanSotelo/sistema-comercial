# Sprint: Reservas + Notificaciones + Remitos/Etiquetas

## 🎯 **Estado: Parcialmente Implementado**

### ✅ **Completado (Objetivo A - Reservas de Stock)**

## 1. Modelo y Migración de Reservas

### Tabla `stock_reservations`
```sql
CREATE TABLE stock_reservations (
    id SERIAL PRIMARY KEY,
    pedido_id INTEGER NOT NULL REFERENCES pedidos(id) ON DELETE CASCADE,
    pedido_item_id INTEGER NOT NULL REFERENCES pedido_items(id) ON DELETE CASCADE,
    producto_id INTEGER NOT NULL REFERENCES productos(id) ON DELETE RESTRICT,
    cantidad INTEGER NOT NULL CHECK (cantidad >= 1),
    estado VARCHAR NOT NULL DEFAULT 'RESERVADA',  -- RESERVADA, CANCELADA, CONSUMIDA
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Índices Implementados:
- ✅ `ix_stock_reservations_producto_estado` - Para consultas de disponibilidad
- ✅ `ix_stock_reservations_pedido_item_active` - Único parcial (WHERE estado='RESERVADA')
- ✅ Índices individuales en todas las FKs

### Modelo SQLAlchemy
- **Archivo**: `backend/app/models/stock_reservation_model.py`
- **Enum**: `EstadoReserva` (RESERVADA, CANCELADA, CONSUMIDA)
- **Relaciones**: pedido, pedido_item, producto

### Migración Alembic
- **Archivo**: `backend/migrations/versions/b2c3d4e5f6g7_add_stock_reservations.py`
- **Revision**: b2c3d4e5f6g7
- **Down revision**: a1b2c3d4e5f6 (pedidos)

## 2. Servicio de Reservas

### Archivo: `backend/app/services/stock_reservations_service.py`

### Funciones Implementadas:

**`get_disponible_producto(db, producto_id)`**
- Calcula: `Disponible = stock - SUM(reservas RESERVADA)`
- Retorna stock disponible para venta

**`ensure_reservas_for_pedido(db, pedido_id, user, request)`**
- Crea o ajusta reservas para todos los items del pedido
- Solo válido en estados EN_PREPARACION o LISTO
- Usa `SELECT ... FOR UPDATE` para locks
- Valida que disponible >= 0
- Auditoría: CREATE con detalles de creadas/ajustadas

**`release_reservas_for_pedido(db, pedido_id, user, request)`**
- Marca todas las reservas activas como CANCELADA
- Usado cuando se cancela el pedido
- Auditoría: UPDATE con action=CANCEL

**`consume_reservas_for_pedido(db, pedido_id, user, request)`**
- Marca reservas como CONSUMIDA
- Descuenta stock real de productos (con lock)
- Transaccional con la creación de Venta
- Revalida stock antes de consumir
- Auditoría: UPDATE con action=CONSUME y deltas de stock

## 3. Hooks en Cambios de Estado

### Integración en `pedidos_service.py`

**NUEVO → EN_PREPARACION:**
```python
ensure_reservas_for_pedido(db, pedido_id, user, request)
# Crea reservas para todos los items
# Falla si no hay disponible suficiente (409)
```

**EN_PREPARACION → LISTO:**
```python
ensure_reservas_for_pedido(db, pedido_id, user, request)
# Revalida y ajusta reservas si los items cambiaron
```

**Cualquier → CANCELADO:**
```python
release_reservas_for_pedido(db, pedido_id, user, request)
# Libera reservas (no falla el cambio de estado)
```

**LISTO → FACTURADO (en facturar_pedido):**
```python
consume_reservas_for_pedido(db, pedido_id, user, request)
# Consume reservas y descuenta stock
# Crea Venta SIN volver a ajustar stock
```

## 4. Cambios en Facturación

### Modificación Crítica
La función `facturar_pedido()` ahora:
1. ✅ Consume reservas (que descuentan stock con lock)
2. ✅ Crea Venta **manualmente** (no usa `crear_venta()`)
3. ✅ **NO ajusta stock** (ya lo hizo el consumo de reservas)
4. ✅ Auditoría de venta con `origen=pedido`

**Antes:**
```python
crear_venta(db, venta_data)  # Ajustaba stock automáticamente
```

**Ahora:**
```python
consume_reservas_for_pedido()  # Ajusta stock aquí
# Crear venta manualmente sin adjust_stock
Venta(...) + VentaItem(...) 
```

---

## 📋 **Pendiente de Implementación**

### 🔄 **UI para Mostrar Disponible (Parcial)**
- ⏳ Endpoint `GET /productos/{id}/disponible`
- ⏳ Modificar lookups para incluir campo `disponible`
- ⏳ Actualizar formularios para mostrar "Disponible: X"
- ⏳ Badge en tabla de pedidos: "RESERVA OK" / "RESERVA INSUFICIENTE"

### 🔔 **Objetivo B - Notificaciones (Pendiente)**

#### Settings (.env)
```env
NOTIFY_ON_READY=true
NOTIFY_WHATS_ENDPOINT=https://bot.ejemplo.com/webhook/order-ready
NOTIFY_WHATS_TOKEN=tu-token-secreto

# Opcional - Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu@email.com
SMTP_PASS=tu-password
SMTP_FROM=noreply@tuempresa.com
```

#### Servicio de Notificaciones
- ⏳ `backend/app/services/notifications_service.py`
- ⏳ Función `notify_order_ready(pedido_id)`
- ⏳ POST a NOTIFY_WHATS_ENDPOINT con retry (3 intentos, backoff)
- ⏳ Envío de email opcional (SMTP)
- ⏳ Auditoría en table_name="notificaciones"
- ⏳ No bloqueante (BackgroundTasks)

#### Hook en Estado LISTO
```python
# En change_estado()
if nuevo_estado == EstadoPedido.LISTO and settings.NOTIFY_ON_READY:
    background_tasks.add_task(notify_order_ready, db, pedido_id)
```

### 📄 **Objetivo C - Remitos y Etiquetas (Pendiente)**

#### Remito de Venta
- ⏳ `GET /ventas/{id}/remito` (HTML imprimible)
- ⏳ `GET /ventas/{id}/remito.pdf` (ReportLab)
- ⏳ Contenido: cliente, fecha, items, totales, firma

#### Etiqueta de Pedido con QR
- ⏳ `GET /pedidos/{id}/label.pdf`
- ⏳ QR Code con: `{pedido_id, cliente, total}`
- ⏳ Dependencias: `qrcode[pil]`, `Pillow`
- ⏳ Generado con ReportLab

---

## 🧪 **Tests Pendientes**

### Tests de Reservas
```python
def test_reserva_al_preparar()
def test_reserva_ajuste_cantidad()
def test_cancelacion_libera()
def test_facturar_consumo()
def test_reserva_concurrencia()  # Lock concurrency
```

### Tests de Notificaciones
```python
def test_notificacion_whatsapp_ok()
def test_notificacion_retry_on_error()
def test_notificacion_auditoria()
```

### Tests de Remitos
```python
def test_remito_venta_html()
def test_remito_venta_pdf()
def test_etiqueta_pedido_qr()
```

---

## 📦 **Dependencias**

### Ya en requirements.txt:
```
reportlab==4.0.7
httpx==0.28.1
```

### Agregadas:
```
qrcode[pil]==7.4.2
Pillow>=10.0
```

---

## 🚀 **Comandos de Deploy**

```bash
# 1. Rebuild con nuevas dependencias
docker compose -f docker-compose.dev.yml up -d --build

# 2. Aplicar migración de reservas
docker compose -f docker-compose.dev.yml exec sc_backend bash -lc "alembic upgrade head"

# 3. Verificar
docker compose -f docker-compose.dev.yml exec sc_backend bash -lc "alembic current"

# 4. Smoke test
bash scripts/smoke.sh
```

---

## ✅ **DoD del Sprint Actual**

### Completado:
- ✅ Modelo y migración de stock_reservations
- ✅ Servicio de reservas con ensure/release/consume
- ✅ Hooks en cambios de estado (NUEVO→EN_PREP→LISTO→FACTURADO, CANCELADO)
- ✅ Locks y transacciones para evitar condiciones de carrera
- ✅ Auditoría completa de reservas
- ✅ Modificación de facturación para consumir reservas

### Pendiente:
- ⏳ UI para mostrar disponible
- ⏳ Endpoint de disponible por producto
- ⏳ Servicio de notificaciones (WhatsApp + Email)
- ⏳ Hook de notificación en LISTO
- ⏳ Remito de venta (HTML + PDF)
- ⏳ Etiqueta de pedido con QR
- ⏳ Tests completos (11 tests nuevos)
- ⏳ Smoke tests actualizados

---

## 🎯 **Impacto del Sprint**

### Funcionalidad de Reservas (Implementada):
1. **Evita sobreventa**: Múltiples pedidos no pueden reservar más que el disponible
2. **Stock soft**: No se descuenta hasta facturar
3. **Transaccional**: Consumo de reservas + creación de venta es atómico
4. **Auditoría completa**: Todos los movimientos de reservas quedan registrados
5. **Locks**: Previene condiciones de carrera con `SELECT FOR UPDATE`

### Flujo Completo:
```
1. Crear Pedido (NUEVO) → Stock no se toca
2. Cambiar a EN_PREPARACION → Crear RESERVAS (valida disponible)
3. Pedidos concurrentes → Si no hay disponible → Error 409
4. Cambiar a LISTO → Revalidar reservas
5. Facturar → Consumir reservas (descuenta stock real) + Crear venta
6. Cancelar en cualquier momento → Liberar reservas
```

---

## 📝 **Notas Importantes**

### ⚠️ **Breaking Change**
La función `facturar_pedido()` ya NO usa `crear_venta()` del servicio de ventas, porque esa función ajusta el stock automáticamente. Ahora:
- Las reservas ajustan el stock al consumirse
- La venta se crea manualmente sin tocar stock
- Esto evita doble descuento de stock

### 🔒 **Concurrencia**
El sistema usa locks a nivel de producto (`with_for_update()`) para garantizar que:
- Dos pedidos no puedan reservar el mismo stock simultáneamente
- El disponible se calcula de forma atómica
- No hay condiciones de carrera

### 📊 **Disponible vs Stock**
- **Stock**: Cantidad física en inventario
- **Disponible**: `Stock - SUM(reservas RESERVADA)`
- **Reservado**: SUM(reservas RESERVADA) del producto

---

## 🎊 **Versión Sugerida**

**v0.8.0** - Reservas de Stock (cuando se complete todo el sprint)

**Contenido:**
- Soft reservations (no descontar hasta facturar)
- Notificaciones WhatsApp/Email en LISTO
- Remitos de venta
- Etiquetas de pedido con QR
- Tests completos de concurrencia

---

## 🚦 **Siguiente Paso**

Para completar el sprint, falta implementar:
1. UI de disponible (30% del trabajo pendiente)
2. Notificaciones (40% del trabajo pendiente)
3. Remitos/Etiquetas (20% del trabajo pendiente)
4. Tests (10% del trabajo pendiente)

**Progreso actual: ~35% del sprint completado** (la parte más crítica: reservas)

---

**¿Continuar con la implementación completa o hacer QA de las reservas primero?**

