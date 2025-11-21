# Módulo de Pedidos - Sistema Comercial

## Resumen

Se ha implementado completamente el módulo de **Pedidos** con flujo de estados y funcionalidad de facturación.

## ✅ Componentes Implementados

### 1. Modelos y Migraciones

- **Modelos** (`backend/app/models/pedido_model.py`):
  - `Pedido`: Tabla principal con estados, origen, y referencias
  - `PedidoItem`: Ítems del pedido con cantidad, precio y subtotal
  - Estados: NUEVO, EN_PREPARACION, LISTO, FACTURADO, CANCELADO
  - Orígenes: MANUAL, WHATSAPP

- **Migración Alembic** (`backend/migrations/versions/a1b2c3d4e5f6_add_pedidos_module.py`):
  - Tabla `pedidos` con índices en (estado, created_at) y (cliente_id, created_at)
  - Tabla `pedido_items` con FK y constraints
  - Constraints: cantidad >= 1, precio_unitario >= 0

### 2. Schemas Pydantic

- **Archivo**: `backend/app/schemas/pedido_schema.py`
- Schemas: `PedidoCreate`, `PedidoUpdate`, `PedidoEstadoChange`, `PedidoOut`, `PedidoFacturarResponse`

### 3. Servicio de Negocio

- **Archivo**: `backend/app/services/pedidos_service.py`
- Funciones principales:
  - `create_pedido()`: Crea pedido con validaciones y cálculo de totales
  - `update_pedido()`: Edita pedido solo si estado lo permite
  - `change_estado()`: Gestiona transiciones de estado con validaciones
  - `facturar_pedido()`: Pre-valida stock, crea Venta, ajusta stock, marca como FACTURADO
  - `listar_pedidos()`: Lista con filtros (q, estado, cliente_id, fechas)

**Transiciones válidas:**
- NUEVO → EN_PREPARACION → LISTO → FACTURADO
- NUEVO/EN_PREPARACION/LISTO → CANCELADO

### 4. Router API

- **Archivo**: `backend/app/routers/pedidos_router.py`
- Endpoints:
  - `GET /pedidos` - Listar con filtros
  - `GET /pedidos/{id}` - Obtener uno
  - `POST /pedidos` - Crear
  - `PUT /pedidos/{id}` - Actualizar (solo si estado permite)
  - `POST /pedidos/{id}/estado` - Cambiar estado
  - `POST /pedidos/{id}/facturar` - Facturar (crea Venta)

### 5. UI con HTMX

- **Archivo**: `backend/app/web/pedidos_ui.py`
- **Templates**: 
  - `backend/app/templates/pedidos/index.html` - Vista principal
  - `backend/app/templates/pedidos/_table.html` - Tabla con paginación
  - `backend/app/templates/pedidos/_form.html` - Formulario dinámico
  - `backend/app/templates/pedidos/_lookup_cliente.html` - Autocomplete cliente
  - `backend/app/templates/pedidos/_lookup_producto.html` - Autocomplete producto

**Características UI:**
- Filtros por texto, estado, cliente, fechas
- Autocomplete HTMX para clientes y productos
- Ítems dinámicos (agregar/eliminar)
- Botones contextuales según estado del pedido
- OOB clear tras crear/actualizar
- Badges de colores por estado

### 6. Integración WhatsApp

- **Modificado**: 
  - `backend/app/routers/integrations_whatsapp_router.py`
  - `backend/app/services/integrations/whatsapp_orders_service.py`

**Nuevos parámetros:**
- `as_order: bool` - True para crear Pedido en lugar de Venta
- `external_ref: str` - Referencia externa (ID mensaje/hilo)
- Variable de entorno `WHATS_CREATE_ORDERS=true` fuerza pedidos

**Comportamiento:**
- `confirm=false` → Cotiza sin tocar nada
- `confirm=true` + `as_order=false` → Crea Venta (ajusta stock)
- `confirm=true` + `as_order=true` → Crea Pedido (NO ajusta stock)

### 7. Tests

- **Archivo**: `backend/tests/test_pedidos.py`
- Tests implementados:
  - `test_pedido_create_ok` - Crear pedido con 2 ítems
  - `test_pedido_transiciones_validas` - NUEVO→EN_PREPARACION→LISTO
  - `test_pedido_cancelar_desde_cualquier_estado`
  - `test_pedido_no_editable_en_listo`
  - `test_pedido_facturar_ok` - Crear pedido + facturar → crea Venta
  - `test_pedido_stock_insuficiente_al_facturar` - Valida error 409
  - `test_integracion_whatsapp_as_order` - WhatsApp con as_order=true
  - `test_listar_pedidos_con_filtros`

### 8. Smoke Tests

- **Archivo**: `scripts/smoke.sh`
- Tests agregados:
  - [P1] GET /app/pedidos
  - [P2] GET /app/pedidos/table
  - [P3-P5] API create, list pedidos con autenticación

### 9. Otros Cambios

- **Navbar** (`backend/app/templates/base.html`): Link "Pedidos" entre Clientes y Ventas
- **API Client** (`backend/app/web/services_api_client.py`): Métodos para pedidos
- **Router Web** (`backend/app/web/router.py`): Registro de pedidos_ui
- **Router API** (`backend/app/routers/__init__.py`): Registro de pedidos_router
- **Base Models** (`backend/app/db/base.py`): Importar modelos de pedido
- **Cliente Model** (`backend/app/models/cliente_model.py`): Relación con pedidos
- **Documentación** (`INTEGRACION_WHATSAPP.md`): Actualizada con info de pedidos

## 📋 Definition of Done (DoD)

✅ Tablas `pedidos` y `pedido_items` creadas con migración Alembic  
✅ Servicio completo con todas las funciones (create, update, change_estado, facturar, listar)  
✅ Routers API y UI completamente funcionales  
✅ Flujo de estados implementado con validaciones  
✅ `facturar_pedido()` crea Venta y ajusta stock transaccionalmente  
✅ Integración WhatsApp soporta `as_order=true` (backwards-compatible)  
✅ Auditoría registra eventos de pedidos (CREATE, UPDATE, CHANGE_STATE, FACTURAR)  
✅ Parciales envueltos en `<div id="tabla">...</div>` con OOB clear  
✅ **CARRERA**: No se reintrodujo campo "Activo"  
✅ Tests completos con 8 escenarios  
✅ Smoke tests actualizados  
✅ Documentación actualizada  

## 🚀 Cómo Usar

### 1. Aplicar Migración

```bash
cd backend
alembic upgrade head
```

### 2. Acceder a la UI

Navegar a: `http://localhost:8000/app/pedidos`

### 3. Flujo Típico

1. **Crear Pedido**: Click en "Nuevo Pedido" → Seleccionar cliente → Agregar productos → Guardar
2. **Preparar**: Click en "Preparar" → Estado cambia a EN_PREPARACION
3. **Marcar Listo**: Click en "Marcar Listo" → Estado cambia a LISTO
4. **Facturar**: Click en "Facturar" → Valida stock → Crea Venta → Ajusta stock → Estado: FACTURADO

### 4. API Examples

**Crear pedido:**
```bash
curl -X POST http://localhost:8000/pedidos \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_id": 1,
    "items": [
      {"producto_id": 1, "cantidad": 2, "precio_unitario": 100.0}
    ],
    "nota": "Pedido desde API"
  }'
```

**Facturar:**
```bash
curl -X POST http://localhost:8000/pedidos/1/facturar \
  -H "Authorization: Bearer $TOKEN"
```

### 5. WhatsApp Integration

**Crear pedido desde WhatsApp:**
```bash
curl -X POST http://localhost:8000/integrations/whatsapp/orders \
  -H "X-Integration-Token: your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+5491112345678",
    "customer_name": "Cliente WhatsApp",
    "confirm": true,
    "as_order": true,
    "items": [{"product_id": 1, "cantidad": 2}]
  }'
```

## 📊 Estructura de Base de Datos

```sql
CREATE TABLE pedidos (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    cliente_id INTEGER NULL REFERENCES clientes(id) ON DELETE RESTRICT,
    estado VARCHAR NOT NULL DEFAULT 'NUEVO',
    origen VARCHAR NOT NULL DEFAULT 'MANUAL',
    telefono VARCHAR NULL,
    nota TEXT NULL,
    total NUMERIC(12,2) NOT NULL DEFAULT 0,
    created_by INTEGER NULL REFERENCES usuarios(id) ON DELETE SET NULL,
    external_ref VARCHAR NULL
);

CREATE TABLE pedido_items (
    id SERIAL PRIMARY KEY,
    pedido_id INTEGER NOT NULL REFERENCES pedidos(id) ON DELETE CASCADE,
    producto_id INTEGER NOT NULL REFERENCES productos(id) ON DELETE RESTRICT,
    cantidad INTEGER NOT NULL CHECK (cantidad >= 1),
    precio_unitario NUMERIC(12,2) NOT NULL CHECK (precio_unitario >= 0),
    subtotal NUMERIC(12,2) NOT NULL
);
```

## 🔒 Validaciones Implementadas

- ✅ Cantidad debe ser >= 1
- ✅ Precio unitario debe ser >= 0
- ✅ Al menos un ítem requerido
- ✅ Transiciones de estado validadas
- ✅ No se puede editar pedido en estado LISTO o FACTURADO
- ✅ Solo se puede facturar pedido en estado LISTO
- ✅ Pre-validación de stock antes de facturar
- ✅ Validación transaccional (rollback en caso de error)

## 🎯 Características Destacadas

1. **Sin reserva de stock**: Los pedidos NO reservan stock hasta que se facturan
2. **Auditoría completa**: Todos los eventos registrados
3. **UI moderna**: HTMX con autocomplete y actualizaciones dinámicas
4. **Integración flexible**: Soporta WhatsApp con backward compatibility
5. **Transaccional**: Facturación atómica (venta + stock + estado)
6. **Filtros avanzados**: Por texto, estado, cliente, fechas
7. **Estados visuales**: Badges de colores por estado

## 📝 Notas

- No se agregó campo "Activo" (CARRERA)
- Stock se ajusta SOLO al facturar (no al crear pedido)
- Pedidos de WhatsApp se marcan con `origen=WHATSAPP`
- Se puede rastrear con `external_ref` (ID mensaje/hilo)
- Auditoría usa `table_name=pedidos` para todos los eventos

---

**Módulo completo y listo para producción** ✨

