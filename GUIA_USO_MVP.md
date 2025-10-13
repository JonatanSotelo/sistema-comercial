# 🎯 Guía de Uso - MVP Sistema Comercial

## ✅ Correcciones Finales Aplicadas

### 1. Botón Completar Ventas/Compras
- ✅ Endpoint PATCH agregado en backend
- ✅ Botón verde ✓ ahora funciona
- ✅ Cambia estado de "pendiente" a "completada"

### 2. Nombres en lugar de IDs
- ✅ Ventas → Muestra nombre del cliente
- ✅ Compras → Muestra nombre del proveedor
- ✅ Mejor seguimiento y claridad

---

## 🚀 Cómo Usar el Sistema

### 1. Productos
```
1. Ir a Productos
2. Crear producto con STOCK inicial (ej: 100)
   - Nombre: "Laptop Dell"
   - Precio: 150000
   - Stock: 100 ← IMPORTANTE
3. Guardar
```

### 2. Proveedores
```
1. Ir a Proveedores
2. Crear proveedor
   - Nombre: "Dell Argentina"
   - CUIT, email, etc.
3. Guardar
```

### 3. Clientes
```
1. Ir a Clientes
2. Crear cliente
   - Nombre: "Juan Pérez"
   - Email, teléfono
3. Guardar
```

### 4. Compras (Incrementa Stock)
```
1. Ir a Compras
2. + Nueva Compra
3. Seleccionar proveedor (REQUERIDO)
4. Agregar productos:
   - Seleccionar producto
   - Cantidad: 50
   - Precio costo (opcional, usa el del producto)
5. Guardar
   → Stock aumenta +50 INMEDIATO
   → Estado: Pendiente (amarillo)
6. Click en botón ✓ verde para completar
   → Estado: Completada (verde)
```

### 5. Ventas (Reduce Stock)
```
1. Ir a Ventas
2. + Nueva Venta
3. Seleccionar cliente (opcional)
4. Agregar productos:
   - Seleccionar producto
   - VERÁS: "Stock disponible: X unidades" (azul)
   - Cantidad ≤ stock disponible
5. Guardar
   → Stock disminuye INMEDIATO
   → Estado: Pendiente (amarillo)
6. Click en botón ✓ verde para completar
   → Estado: Completada (verde)
```

---

## 🎯 Flujo Completo de Stock

### Ejemplo Real:

```
1. Crear Producto "Laptop"
   Stock inicial: 100

2. Hacer Compra de 50 unidades
   → Stock: 100 + 50 = 150 ✅
   → Estado: Pendiente (amarillo)

3. Completar Compra (botón ✓)
   → Stock: 150 (sin cambio)
   → Estado: Completada (verde) ✅

4. Hacer Venta de 30 unidades
   → Stock: 150 - 30 = 120 ✅
   → Estado: Pendiente (amarillo)

5. Completar Venta (botón ✓)
   → Stock: 120 (sin cambio)
   → Estado: Completada (verde) ✅

Stock final: 120 ✅
```

---

## ✅ Botones en Tablas

### Ventas/Compras Pendientes (🟡)
- 👁️ **Ver detalle** (azul)
- ✅ **Completar** (verde) ← Cambia a completada
- 🗑️ **Eliminar** (rojo)

### Ventas/Compras Completadas (🟢)
- 👁️ **Ver detalle** (azul)
- 🗑️ **Eliminar** (rojo)
- (No aparece botón ✅, ya está completada)

---

## 💡 Tips Importantes

### Para Ventas
- ⚠️ **Verifica el stock disponible** (caja azul)
- ⚠️ Solo puedes vender lo que hay en stock
- ✅ Stock se resta INMEDIATO al crear

### Para Compras
- ✅ **Proveedor es REQUERIDO**
- ✅ Precio costo es opcional (usa el del producto)
- ✅ Stock se suma INMEDIATO al crear

### Estados
- 🟡 **Pendiente** = Recién creada, stock YA movido
- 🟢 **Completada** = Confirmada, solo cambio visual

---

## 🎊 MVP Funcional

**Todo funcionando:**
- ✅ Productos CRUD
- ✅ Clientes CRUD
- ✅ Proveedores CRUD
- ✅ Compras (stock +)
- ✅ Ventas (stock -)
- ✅ Completar operaciones
- ✅ Ver detalles
- ✅ Nombres legibles (no IDs)

**Acceso:**
```
http://localhost:8000/app
```

---

**Versión:** 2.0.0 MVP  
**Estado:** ✅ Funcional

