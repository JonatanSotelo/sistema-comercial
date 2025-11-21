# Módulo de Pedidos - v0.8.0

## 🎯 Funcionalidades

### Estados y Flujo
```
NUEVO → EN_PREPARACION → LISTO → FACTURADO
  ↓          ↓            ↓
CANCELADO ← ← ← ← ← ← ← ←
```

### Características por Estado

#### NUEVO
- Pedido recién creado
- **Acciones**: Editar, Preparar, Cancelar

#### EN_PREPARACION
- **Reservas**: Se crean automáticamente al entrar a este estado
- **Disponible**: `stock - reservas_activas`
- **Validación**: No permite pasar si no hay stock disponible (409/400)
- **Acciones**:
  - 🏷️ **Etiqueta PDF**: Con QR code y datos del pedido
  - 🖨️ **Packing Slip**: HTML e PDF para preparación
  - Editar (reajusta reservas automáticamente)
  - Marcar como LISTO, Cancelar

#### LISTO
- Pedido preparado, listo para entregar
- **Notificación** (v0.8.0): Si `NOTIFY_ON_READY=true`, envía WhatsApp/Email automáticamente en background
- **Acciones**:
  - 🏷️ **Etiqueta PDF**: Para identificación y entrega
  - 🖨️ **Packing Slip**: Verificación final
  - Facturar, Cancelar

#### FACTURADO
- Pedido convertido en venta
- **Venta vinculada**: `pedido.venta_id` apunta a la venta generada
- **Stock**: Descontado al facturar (consumo de reservas)
- **Acciones**:
  - 🏷️ **Etiqueta PDF**: Registro histórico
  - 📄 **Remito PDF**: De la venta asociada (si `venta_id` existe)

#### CANCELADO
- Pedido cancelado
- **Reservas**: Se liberan automáticamente

## 📋 Gestión de Reservas (Soft Stock)

### Qué son las Reservas
Las reservas de stock permiten "apartar" productos sin descontar el stock real hasta la facturación. Esto previene sobreventa cuando hay múltiples pedidos concurrentes.

### Cálculo de Disponible
```python
disponible = productos.stock - SUM(reservas WHERE estado='RESERVADA')
```

### Flujo de Reservas

1. **NUEVO → EN_PREPARACION**
   - Crea reservas por cada item del pedido
   - Valida que hay disponible suficiente
   - Si falla: devuelve 409/400 con mensaje de error

2. **Edición en EN_PREPARACION**
   - Reajusta reservas automáticamente
   - Valida disponible con las nuevas cantidades

3. **CANCELACIÓN**
   - Marca reservas como `CANCELADA`
   - Libera el stock reservado

4. **FACTURACIÓN**
   - Marca reservas como `CONSUMIDA`
   - Descuenta stock real en la misma transacción
   - Crea la venta vinculada

### Concurrencia
- **Row Locking**: `SELECT ... FOR UPDATE` en operaciones críticas
- **Validación atómica**: Todas las operaciones en transacción
- **Test de concurrencia**: `test_reserva_concurrencia` valida comportamiento

## 🔔 Notificaciones Automáticas (v0.8.0)

### Configuración (.env)
```bash
# Habilitar/deshabilitar notificaciones
NOTIFY_ON_READY=true

# Endpoint del micro-servicio bot WhatsApp
NOTIFY_WHATS_ENDPOINT=https://tu-bot.com/webhook

# Token de autenticación para el webhook
NOTIFY_WHATS_TOKEN=tu-token-secreto

# SMTP (Opcional - email de respaldo)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASS=tu-app-password
SMTP_FROM=noreply@sistema-comercial.com
```

### Cuándo se Dispara
Al cambiar un pedido a estado **LISTO**, si `NOTIFY_ON_READY=true`.

### Payload Enviado
```json
{
  "phone": "5491100000000",
  "customer_name": "Juan Pérez",
  "order_id": 123,
  "items": [
    {"producto": "Batería 12V", "cantidad": 2, "precio": 150.0}
  ],
  "total": 300.0,
  "external_ref": "WA_MSG_123",
  "message": "¡Tu pedido #123 está listo para retirar! Total: $300.00"
}
```

### Comportamiento
- **No bloqueante**: Se ejecuta en `BackgroundTasks` de FastAPI
- **Reintentos**: 3 intentos con backoff exponencial (0.5s, 1s, 2s)
- **Timeout**: 5 segundos por intento
- **Auditoría**: Registra éxito/fallo en `table_name="notificaciones"`
- **Fallo**: Si no puede enviar, registra error pero NO falla el cambio de estado

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

## 📄 Documentos PDF

### Etiqueta con QR (Pedidos)
- **Endpoint**: `GET /pedidos/{id}/label.pdf`
- **Estados**: EN_PREPARACION, LISTO, FACTURADO
- **Contenido**:
  - QR code con datos del pedido (JSON)
  - Número de pedido
  - Cliente y teléfono
  - Cantidad de items
  - Total
  - Estado actual
- **Tamaño**: A6 (~105x148mm)
- **Uso**: Identificación rápida, seguimiento, entrega

### Packing Slip (Preparación)
- **Endpoints**: 
  - `GET /pedidos/{id}/packing` (HTML)
  - `GET /pedidos/{id}/packing.pdf` (PDF)
- **Estados**: EN_PREPARACION, LISTO
- **Contenido**: Lista detallada de productos para picking/empaque

### Remito (Ventas)
- **Endpoints**:
  - `GET /ventas/{id}/remito` (HTML)
  - `GET /ventas/{id}/remito.pdf` (PDF)
- **Acceso**: Desde pedidos FACTURADOS (si tiene `venta_id`)
- **Contenido**:
  - Datos del cliente
  - Items con cantidades y precios
  - Total
  - Espacio para firma y observaciones

## 🎨 UI - Botones por Estado

### EN_PREPARACION
- 🏷️ **Etiqueta** → `/pedidos/{id}/label.pdf`
- 🖨️ **Packing** → `/pedidos/{id}/packing`
- 📄 **PDF** → `/pedidos/{id}/packing.pdf`
- **Editar**, **Marcar LISTO**, **Cancelar**

### LISTO
- 🏷️ **Etiqueta** → `/pedidos/{id}/label.pdf`
- 🖨️ **Packing** → `/pedidos/{id}/packing`
- 📄 **PDF** → `/pedidos/{id}/packing.pdf`
- **Facturar**, **Cancelar**

### FACTURADO
- 🏷️ **Etiqueta** → `/pedidos/{id}/label.pdf`
- 📄 **Remito** → `/ventas/{venta_id}/remito.pdf` (si existe)

### Acciones Masivas
- Checkboxes por fila + "Seleccionar todo"
- Panel dinámico para cambio masivo de estado:
  - Marcar EN_PREPARACION
  - Marcar LISTO
  - Cancelar múltiples

## 🧪 Tests

### Cobertura
- **Reservas**: `backend/tests/test_reservas.py`
  - Creación al preparar
  - Ajuste en edición
  - Liberación al cancelar
  - Consumo al facturar
  - Concurrencia

- **Notificaciones**: `backend/tests/test_notifications.py`
  - Envío exitoso
  - Reintentos en fallo
  - Auditoría de errores
  - Skip si no hay teléfono
  - Skip si NOTIFY_ON_READY=false

- **PDFs**: `backend/tests/test_pdfs.py`
  - Remito HTML y PDF
  - Etiqueta PDF
  - Validación de contenido (> 0 bytes)

### Ejecutar Tests
```bash
# Todos los tests de pedidos
docker compose -f docker-compose.dev.yml exec sc_backend pytest tests/test_pedidos.py -v

# Solo reservas
docker compose -f docker-compose.dev.yml exec sc_backend pytest tests/test_reservas.py -v

# Solo notificaciones
docker compose -f docker-compose.dev.yml exec sc_backend pytest tests/test_notifications.py -v

# Solo PDFs
docker compose -f docker-compose.dev.yml exec sc_backend pytest tests/test_pdfs.py -v
```

## 🔍 Smoke Tests

### Ejecutar
```bash
./scripts/smoke.sh
```

### Cobertura
- **[P1-P8]**: CRUD de pedidos, packing, reportes
- **[R1-R9]**: Flujo completo de reservas con concurrencia
- **[N1]**: Auditoría de notificaciones
- **[PDF1-PDF3]**: Remito y etiquetas

## 🗃️ Base de Datos

### Tablas
- **pedidos**: Cabecera del pedido
- **pedido_items**: Items del pedido
- **stock_reservations**: Reservas de stock (v0.7.5)
  - Estados: RESERVADA, CANCELADA, CONSUMIDA
  - Índices: `(producto_id, estado)`, `(pedido_item_id)`

### Migraciones Recientes
- `a1b2c3d4e5f6_add_pedidos_module.py` - Creación inicial
- `b2c3d4e5f6g7_add_stock_reservations.py` - Reservas
- `c1d2e3f4g5h6_fix_users_fks.py` - Fix FKs a users
- `d3e4f5g6h7i8_add_venta_id_to_pedidos.py` - Link a ventas (v0.8.0)

## 📊 API Endpoints

### CRUD Básico
- `GET /pedidos` - Listar con filtros
- `GET /pedidos/{id}` - Detalle
- `POST /pedidos` - Crear
- `PUT /pedidos/{id}` - Editar (solo NUEVO/EN_PREPARACION)
- `POST /pedidos/{id}/estado` - Cambiar estado
- `POST /pedidos/bulk_estado` - Cambio masivo

### Facturación
- `POST /pedidos/{id}/facturar` - Convertir a venta

### Documentos
- `GET /pedidos/{id}/packing` - Packing slip HTML
- `GET /pedidos/{id}/packing.pdf` - Packing slip PDF
- `GET /pedidos/{id}/label.pdf` - Etiqueta con QR

### Reportes
- `GET /reportes/pedidos` - Agrupado por estado/día/cliente
- `GET /reportes/pedidos/export` - CSV/XLSX

## 🔐 Permisos
- **Lectura**: Cualquier usuario autenticado
- **Creación/Edición**: Usuarios autenticados
- **Cambio de estado**: Usuarios autenticados
- **Facturación**: Usuarios autenticados
- **Bulk actions**: Usuarios autenticados

## 🚀 Mejores Prácticas

### Al Crear Pedidos
1. Asignar cliente cuando sea posible (mejora notificaciones)
2. Incluir teléfono si el cliente no lo tiene
3. Usar `external_ref` para trazabilidad (ej: desde WhatsApp)

### Al Preparar
1. Verificar disponible antes de marcar EN_PREPARACION
2. Si falla por stock, revisar otros pedidos que puedan estar reservando
3. Usar packing slip para guiar la preparación

### Al Facturar
1. Solo facturar desde LISTO
2. Las reservas se consumen automáticamente
3. El stock se descuenta en la misma transacción
4. Se crea la venta y se vincula (`pedido.venta_id`)

### Notificaciones
1. Configurar webhook antes de habilitar `NOTIFY_ON_READY`
2. Monitorear auditoría de notificaciones para detectar fallos
3. Tener SMTP como backup opcional

## 🐛 Troubleshooting

### Error: "Stock insuficiente"
- **Causa**: No hay disponible suficiente (stock - reservas < cantidad)
- **Solución**: 
  1. Verificar reservas activas: `SELECT * FROM stock_reservations WHERE producto_id=X AND estado='RESERVADA'`
  2. Cancelar pedidos no necesarios para liberar reservas
  3. Ajustar stock del producto

### Error: "Transición no válida"
- **Causa**: Intentar cambio de estado no permitido
- **Solución**: Seguir el flujo de estados permitido

### Notificación no enviada
- **Causa posible**: NOTIFY_ON_READY=false, sin teléfono, webhook caído
- **Diagnóstico**: Revisar auditoría con `q=notificaciones`

### Remito no aparece en pedido facturado
- **Causa**: `venta_id` es NULL
- **Solución**: Verificar que la migración `d3e4f5g6h7i8` se aplicó correctamente

---

**Última actualización**: v0.8.0 - 2025-11-21  
**Mantenido por**: Sistema Comercial Team

