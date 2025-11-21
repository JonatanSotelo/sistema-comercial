# Integración WhatsApp → Venta / Pedido (MVP)

## Descripción

Endpoint de integración para que el Bot WhatsApp cree Ventas, Pedidos (o valide presupuestos) en el backend del Sistema Comercial.

## Configuración

### Variables de Entorno

Agregar en `backend/.env`:

```env
WHATS_ORDERS_TOKEN=tu-token-secreto-para-integracion-whatsapp
WHATS_DEFAULT_PRICE_SOURCE=name  # name|producto|lista
WHATS_FUZZY_MATCH=true
WHATS_CREATE_ORDERS=false  # true=crea Pedidos en lugar de Ventas por defecto
```

## Endpoint

### POST /integrations/whatsapp/orders

**Autenticación:** Header `X-Integration-Token: {WHATS_ORDERS_TOKEN}`

**Body (estructurado - preferido):**

```json
{
  "phone": "54911XXXXXXXX",
  "customer_name": "Juan Perez",   // opcional
  "confirm": true,                 // true=crea venta/pedido, false=simula
  "as_order": true,                // true=crea Pedido, false=crea Venta
  "external_ref": "whatsapp_msg_123",  // opcional: ID mensaje/hilo del bot
  "items": [
    {"product_id": 1, "cantidad": 2, "precio_unitario": 150000},
    {"codigo": "BAT12V", "cantidad": 1},
    {"query": "bateria 12v 65ah", "cantidad": 1}
  ]
}
```

**Nota:** Si `WHATS_CREATE_ORDERS=true` en `.env`, se fuerza `as_order=true` automáticamente.

**Respuestas:**

- `confirm=false` (cotización):
```json
{
  "type": "quote",
  "cliente_id": 1,
  "items": [...],
  "total": 150000.0,
  "stock_check": "ok"
}
```

- `confirm=true` + `as_order=false` (venta creada):
```json
{
  "type": "sale",
  "venta_id": 123,
  "cliente_id": 1,
  "items": [...],
  "total": 150000.0
}
```

- `confirm=true` + `as_order=true` (pedido creado):
```json
{
  "type": "order",
  "pedido_id": 45,
  "cliente_id": 1,
  "items": [...],
  "total": 150000.0,
  "estado": "NUEVO"
}
```

- Error (stock insuficiente):
```json
{
  "detail": {
    "errors": ["Item 1 (Producto X): Stock insuficiente (disponible: 2, solicitado: 5)"],
    "resolved_items": [...],
    "total": 0.0
  }
}
```

## Flujo de Resolución

### Cliente

1. Buscar por `phone` (normalizado a dígitos) en tabla `clientes`
2. Si no existe y viene `customer_name` → crear cliente mínimo
3. Si no existe y no viene nombre → 400 (solicitar `customer_name`)

### Productos

Resolución en este orden:

1. **product_id** directo
2. **codigo** (si existe campo `codigo` en productos)
3. **query** → búsqueda ILIKE por nombre (si `WHATS_FUZZY_MATCH=true`)
   - Si 0 hallazgos → error del ítem
   - Si >1 hallazgo → 400 con sugerencias

### Precios

- Usar `precio_unitario` de ítem si viene
- Si no, usar `producto.precio`

### Stock

- Validación de stock (como en ventas): si falta → 409 con detalle por ítem
- `confirm=false` → no tocar stock (solo cotización)
- `confirm=true` + `as_order=false` → crear Venta y ajustar stock
- `confirm=true` + `as_order=true` → crear Pedido SIN ajustar stock (se factura después)

## Auditoría

Todos los eventos se registran en `auditoria` con:
- `table_name="integraciones"`
- `action="CREATE"`
- `username="whatsapp_bot"`
- `details` con payload sanitizado (sin token), resultado y IP

## UI Monitor

**GET /app/integraciones/whatsapp**

Vista que lista los últimos 100 eventos de integración desde la tabla de auditoría, con filtros:
- Fecha desde/hasta
- Teléfono
- Estado (cotización/venta/error)

## Tests

Ejecutar tests:

```bash
pytest backend/tests/test_integrations_whatsapp.py -v
```

Tests incluidos:
- `test_whats_orders_structured_ok_crea_venta` - Cliente no existe → se crea → venta ok → stock baja → auditoría
- `test_whats_orders_quote_only` - confirm=false → no altera stock
- `test_whats_orders_ambiguous` - query devuelve múltiples productos → 400 con sugerencias
- `test_whats_orders_stock_409` - stock insuficiente
- `test_whats_orders_auth_401` - token inválido
- `test_whats_orders_by_codigo` - resolver producto por código

## Ejemplos de Uso

### Cotización (sin crear venta)

```bash
curl -X POST "http://localhost:8000/integrations/whatsapp/orders" \
  -H "X-Integration-Token: tu-token" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "5491100000000",
    "customer_name": "Cliente Test",
    "confirm": false,
    "items": [
      {"query": "bateria 12v", "cantidad": 1}
    ]
  }'
```

### Crear Venta

```bash
curl -X POST "http://localhost:8000/integrations/whatsapp/orders" \
  -H "X-Integration-Token: tu-token" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "5491100000000",
    "customer_name": "Cliente Test",
    "confirm": true,
    "as_order": false,
    "items": [
      {"product_id": 1, "cantidad": 2}
    ]
  }'
```

### Crear Pedido (sin ajustar stock)

```bash
curl -X POST "http://localhost:8000/integrations/whatsapp/orders" \
  -H "X-Integration-Token: tu-token" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "5491100000000",
    "customer_name": "Cliente Test",
    "confirm": true,
    "as_order": true,
    "external_ref": "whatsapp_msg_12345",
    "items": [
      {"product_id": 1, "cantidad": 2}
    ]
  }'
```

## Seguridad

- Autenticación por token compartido (`X-Integration-Token`)
- Rate limiting recomendado (30 req/min por IP/phone)
- Sanitización de payload en auditoría (no guardar token)
- Validación de cantidad >= 1 y precios >= 0

## Comportamiento por Defecto con Pedidos

### Variable WHATS_CREATE_ORDERS

Si `WHATS_CREATE_ORDERS=true` en `.env`:
- **Todos** los requests con `confirm=true` crearán **Pedidos** automáticamente
- El parámetro `as_order` se fuerza a `true`
- El stock NO se ajusta (se factura después desde `/app/pedidos`)

### Flujo Recomendado

**Opción A: Pedidos (recomendado para WhatsApp):**
1. Bot recibe mensaje → Cotiza con `confirm=false` → Responde al cliente
2. Cliente confirma → Bot envía `confirm=true, as_order=true`
3. Se crea Pedido en estado NUEVO (sin tocar stock)
4. Personal de preparación:
   - Ve pedido en `/app/pedidos`
   - Cambia a EN_PREPARACION → LISTO
   - Click en "Facturar" → Crea Venta + Ajusta stock

**Opción B: Ventas directas (compatibilidad):**
1. Bot recibe mensaje con `confirm=true, as_order=false`
2. Se crea Venta inmediatamente (ajusta stock)
3. No pasa por preparación

### Referencia Externa

El campo `external_ref` permite rastrear el mensaje/hilo de WhatsApp:
- Almacenar ID del mensaje o conversación
- Buscar pedido por `external_ref` si el cliente vuelve a preguntar
- Útil para bots que mantienen contexto

## UI de Preparación

Los pedidos creados desde WhatsApp aparecen en `/app/pedidos` con:
- **Origen:** Badge "WHATSAPP"
- **Teléfono:** Visible en el detalle
- **External Ref:** Para tracking
- **Botones de impresión:** Packing slip HTML/PDF cuando está EN_PREPARACION o LISTO
- **Acciones masivas:** Cambiar estado de múltiples pedidos a la vez

## Notificaciones Automáticas (v0.8.0+)

### Configuración

Agregar en `backend/.env`:

```env
# Habilitar/deshabilitar notificaciones automáticas
NOTIFY_ON_READY=true

# URL del webhook del bot WhatsApp (micro-servicio)
NOTIFY_WHATS_ENDPOINT=https://tu-bot.com/webhook/order-ready

# Token de autenticación para el webhook
NOTIFY_WHATS_TOKEN=tu-token-secreto-notificaciones

# SMTP (Opcional - email de respaldo)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASS=tu-app-password
SMTP_FROM=noreply@sistema-comercial.com
```

### Cuándo se Dispara

Cuando un pedido cambia a estado **LISTO** y `NOTIFY_ON_READY=true`, el sistema envía automáticamente:
1. Notificación WhatsApp al teléfono del cliente (si está configurado)
2. Email opcional (si SMTP está configurado)

### Payload Enviado al Bot

```json
{
  "phone": "5491100000000",
  "customer_name": "Juan Pérez",
  "order_id": 123,
  "items": [
    {
      "producto": "Batería 12V 65Ah",
      "cantidad": 2,
      "precio": 15000.0
    }
  ],
  "total": 30000.0,
  "external_ref": "whatsapp_msg_456",
  "message": "¡Tu pedido #123 está listo para retirar! Total: $30000.00"
}
```

### Headers del Request

```
POST https://tu-bot.com/webhook/order-ready
Authorization: Bearer {NOTIFY_WHATS_TOKEN}
Content-Type: application/json
```

### Comportamiento

- **No bloqueante**: Se ejecuta en background (FastAPI BackgroundTasks)
- **Reintentos**: 3 intentos con backoff exponencial (0.5s, 1s, 2s)
- **Timeout**: 5 segundos por intento
- **Fallo**: Si no puede enviar, registra error en auditoría pero NO falla el cambio de estado del pedido
- **Auditoría**: Todos los intentos se registran en `table_name="notificaciones"`

### Ejemplo de Auditoría

```json
{
  "table_name": "notificaciones",
  "action": "CREATE",
  "record_id": "123",
  "details": {
    "type": "order_ready",
    "success": true,
    "phone": "5491100000000",
    "items_count": 2
  }
}
```

### Troubleshooting

**Notificación no enviada:**
1. Verificar que `NOTIFY_ON_READY=true` en `.env`
2. Verificar que el pedido tiene `telefono` o el cliente tiene `telefono`
3. Revisar logs del backend: `docker compose logs sc_backend | grep notif`
4. Revisar auditoría: `/app/auditoria?q=notificaciones`
5. Verificar que el webhook del bot responde correctamente

**Ver historial de notificaciones:**
```bash
# API
GET /app/auditoria?q=notificaciones

# SQL directo
SELECT * FROM auditoria 
WHERE table_name = 'notificaciones' 
ORDER BY created_at DESC LIMIT 20;
```

## Notas

- El campo `codigo` ya existe en el modelo `Producto` (no requiere migración)
- Sin campo "Activo" en formularios/tablas (CARRERA)
- Los parciales de tabla están envueltos en `<div id="tabla">…</div>` y usan HTMX
- **v0.7.5+**: Los pedidos reservan stock automáticamente al pasar a EN_PREPARACION
- **v0.8.0+**: Notificaciones automáticas cuando el pedido está LISTO


