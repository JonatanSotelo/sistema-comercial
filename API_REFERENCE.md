# 📚 API Reference - Sistema Comercial

## 📋 Tabla de Contenidos
- [Autenticación](#-autenticación)
- [Usuarios](#-usuarios)
- [Clientes](#-clientes)
- [Proveedores](#-proveedores)
- [Productos](#-productos)
- [Stock](#-stock)
- [Compras](#-compras)
- [Ventas](#-ventas)
- [Auditoría](#-auditoría)
- [Respaldos](#-respaldos)
- [Monitoreo](#-monitoreo)
- [Parámetros de Consulta](#-parámetros-de-consulta)
- [Códigos de Error](#-códigos-de-error)

---

## 🔐 Autenticación

### **POST /auth/login**
Login de usuario con credenciales.

**Request Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### **POST /auth/register**
Registro de nuevo usuario (solo admin).

**Request Body:**
```json
{
  "username": "nuevo_usuario",
  "password": "password123",
  "role": "consulta"
}
```

### **GET /auth/me**
Obtener información del usuario actual.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "username": "admin",
  "role": "admin",
  "created_at": "2024-01-15T10:30:00"
}
```

---

## 👥 Usuarios

### **GET /users/usuarios/**
Listar usuarios con paginación.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (int): Número de página (default: 1)
- `size` (int): Tamaño de página (default: 20, max: 200)
- `search` (string): Búsqueda por username
- `sort` (string): Ordenamiento (ej: `username,-created_at`)

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "username": "admin",
      "role": "admin",
      "created_at": "2024-01-15T10:30:00"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 20,
  "pages": 1
}
```

### **POST /users/usuarios/**
Crear nuevo usuario.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "username": "nuevo_usuario",
  "password": "password123",
  "role": "consulta"
}
```

### **GET /users/usuarios/{id}**
Obtener usuario por ID.

### **PUT /users/usuarios/{id}**
Actualizar usuario.

### **DELETE /users/usuarios/{id}**
Eliminar usuario.

---

## 👤 Clientes

### **GET /clientes/**
Listar clientes con paginación.

**Query Parameters:**
- `page` (int): Número de página
- `size` (int): Tamaño de página
- `search` (string): Búsqueda por nombre, email, teléfono
- `sort` (string): Ordenamiento

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "nombre": "Cliente Test",
      "email": "cliente@test.com",
      "telefono": "123456789",
      "created_at": "2024-01-15T10:30:00"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 20,
  "pages": 1
}
```

### **POST /clientes/**
Crear nuevo cliente.

**Request Body:**
```json
{
  "nombre": "Cliente Test",
  "email": "cliente@test.com",
  "telefono": "123456789"
}
```

### **GET /clientes/{id}**
Obtener cliente por ID.

### **PUT /clientes/{id}**
Actualizar cliente.

### **DELETE /clientes/{id}**
Eliminar cliente.

### **GET /clientes/export**
Exportar clientes a Excel.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** Archivo Excel (.xlsx)

---

## 🏢 Proveedores

### **GET /proveedores/**
Listar proveedores con paginación.

**Query Parameters:**
- `page` (int): Número de página
- `size` (int): Tamaño de página
- `search` (string): Búsqueda por nombre, email
- `sort` (string): Ordenamiento

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "nombre": "Proveedor Test",
      "email": "proveedor@test.com",
      "created_at": "2024-01-15T10:30:00"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 20,
  "pages": 1
}
```

### **POST /proveedores/**
Crear nuevo proveedor.

**Request Body:**
```json
{
  "nombre": "Proveedor Test",
  "email": "proveedor@test.com"
}
```

### **GET /proveedores/{id}**
Obtener proveedor por ID.

### **PUT /proveedores/{id}**
Actualizar proveedor.

### **DELETE /proveedores/{id}**
Eliminar proveedor.

### **GET /proveedores/export**
Exportar proveedores a Excel.

---

## 📦 Productos

### **GET /productos/**
Listar productos con paginación.

**Query Parameters:**
- `page` (int): Número de página
- `size` (int): Tamaño de página
- `search` (string): Búsqueda por nombre, descripción
- `sort` (string): Ordenamiento

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "nombre": "Producto Test",
      "descripcion": "Descripción del producto",
      "precio": 100.0,
      "created_at": "2024-01-15T10:30:00"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 20,
  "pages": 1
}
```

### **POST /productos/**
Crear nuevo producto.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "nombre": "Producto Test",
  "descripcion": "Descripción del producto",
  "precio": 100.0
}
```

### **GET /productos/{id}**
Obtener producto por ID.

### **PUT /productos/{id}**
Actualizar producto.

### **DELETE /productos/{id}**
Eliminar producto.

### **GET /productos/export**
Exportar productos a Excel.

---

## 📊 Stock

### **GET /stock/{producto_id}**
Obtener stock actual de un producto.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "producto_id": 1,
  "producto_nombre": "Producto Test",
  "stock": 50.0,
  "ultimo_movimiento": "2024-01-15T10:30:00"
}
```

---

## 🛒 Compras

### **GET /compras/**
Listar compras con paginación.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (int): Número de página
- `size` (int): Tamaño de página
- `search` (string): Búsqueda por proveedor
- `sort` (string): Ordenamiento

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "proveedor_id": 1,
      "proveedor_nombre": "Proveedor Test",
      "total": 500.0,
      "created_at": "2024-01-15T10:30:00",
      "items": [
        {
          "producto_id": 1,
          "producto_nombre": "Producto Test",
          "cantidad": 10,
          "costo_unitario": 50.0,
          "subtotal": 500.0
        }
      ]
    }
  ],
  "total": 1,
  "page": 1,
  "size": 20,
  "pages": 1
}
```

### **POST /compras/**
Crear nueva compra.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "proveedor_id": 1,
  "items": [
    {
      "producto_id": 1,
      "cantidad": 10,
      "costo_unitario": 50.0
    }
  ]
}
```

### **GET /compras/{id}**
Obtener compra por ID.

### **DELETE /compras/{id}**
Eliminar compra.

---

## 💰 Ventas

### **GET /ventas/**
Listar ventas con paginación.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (int): Número de página
- `size` (int): Tamaño de página
- `search` (string): Búsqueda por cliente
- `sort` (string): Ordenamiento

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "cliente_id": 1,
      "cliente_nombre": "Cliente Test",
      "total": 500.0,
      "created_at": "2024-01-15T10:30:00",
      "items": [
        {
          "producto_id": 1,
          "producto_nombre": "Producto Test",
          "cantidad": 5,
          "precio_unitario": 100.0,
          "subtotal": 500.0
        }
      ]
    }
  ],
  "total": 1,
  "page": 1,
  "size": 20,
  "pages": 1
}
```

### **POST /ventas/**
Crear nueva venta.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "cliente_id": 1,
  "items": [
    {
      "producto_id": 1,
      "cantidad": 5,
      "precio_unitario": 100.0
    }
  ]
}
```

### **GET /ventas/{id}**
Obtener venta por ID.

### **PUT /ventas/{id}**
Actualizar venta.

### **DELETE /ventas/{id}**
Eliminar venta.

---

## 📋 Auditoría

### **GET /auditoria/**
Listar logs de auditoría.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `page` (int): Número de página
- `size` (int): Tamaño de página
- `search` (string): Búsqueda por usuario, acción
- `sort` (string): Ordenamiento

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "usuario": "admin",
      "accion": "CREATE",
      "tabla": "productos",
      "registro_id": 1,
      "datos_anteriores": null,
      "datos_nuevos": {"nombre": "Producto Test"},
      "ip_address": "127.0.0.1",
      "created_at": "2024-01-15T10:30:00"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 20,
  "pages": 1
}
```

---

## 💾 Respaldos

### **GET /backup/**
Listar respaldos disponibles.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
[
  {
    "id": "backup_20240115_023000.zip",
    "fecha": "2024-01-15T02:30:00",
    "tamaño": "1024000"
  }
]
```

### **POST /backup/**
Crear respaldo manual.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Respaldo creado exitosamente",
  "archivo": "backup_20240115_103000.zip"
}
```

### **GET /backup/{id}**
Descargar respaldo.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:** Archivo ZIP

---

## 📊 Monitoreo

### **GET /monitoring/health**
Health check completo del sistema.

**Response:**
```json
{
  "overall_status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "database": {
    "status": "healthy",
    "response_time": 0.002
  },
  "backup": {
    "status": "healthy",
    "backup_dir": "/app/backups"
  },
  "metrics": {
    "uptime_seconds": 3600,
    "total_requests": 150,
    "error_rate": 0.02
  }
}
```

### **GET /monitoring/metrics**
Métricas del sistema.

**Response:**
```json
{
  "uptime_seconds": 3600,
  "total_requests": 150,
  "total_errors": 3,
  "error_rate": 0.02,
  "average_response_time": 0.5,
  "endpoint_stats": {
    "GET /productos": {"count": 50, "errors": 0},
    "POST /ventas": {"count": 20, "errors": 1}
  }
}
```

### **GET /monitoring/alerts**
Alertas recientes.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "alerts": [
    {
      "type": "HIGH_ERROR_RATE",
      "message": "Error rate is 15.00%",
      "timestamp": "2024-01-15T10:30:00",
      "severity": "warning"
    }
  ],
  "total_alerts": 1
}
```

### **GET /monitoring/status**
Estado básico del sistema.

**Response:**
```json
{
  "status": "healthy",
  "uptime": 3600,
  "requests": 150,
  "errors": 3,
  "error_rate": 0.02,
  "avg_response_time": 0.5
}
```

---

## 🔍 Parámetros de Consulta

### **Paginación**
- `page` (int): Número de página (default: 1)
- `size` (int): Tamaño de página (default: 20, max: 200)

### **Filtros**
- `search` (string): Búsqueda de texto
- `fecha_desde` (date): Fecha desde (formato: YYYY-MM-DD)
- `fecha_hasta` (date): Fecha hasta (formato: YYYY-MM-DD)

### **Ordenamiento**
- `sort` (string): Campo para ordenar (ej: `nombre,-precio`)

### **Ejemplos**
```bash
# Listar productos con paginación
GET /productos?page=1&size=10

# Buscar clientes
GET /clientes?search=empresa&page=1&size=5

# Ordenar productos por precio descendente
GET /productos?sort=-precio

# Filtrar por fecha
GET /ventas?fecha_desde=2024-01-01&fecha_hasta=2024-01-31
```

---

## ❌ Códigos de Error

### **400 Bad Request**
```json
{
  "detail": "Datos de entrada inválidos"
}
```

### **401 Unauthorized**
```json
{
  "detail": "Token de autenticación inválido"
}
```

### **403 Forbidden**
```json
{
  "detail": "No tienes permisos para realizar esta acción"
}
```

### **404 Not Found**
```json
{
  "detail": "Recurso no encontrado"
}
```

### **422 Unprocessable Entity**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "Formato de email inválido",
      "type": "value_error"
    }
  ]
}
```

### **429 Too Many Requests**
```json
{
  "detail": {
    "error": "Rate limit exceeded",
    "remaining": 0,
    "reset_time": 1642248600,
    "retry_after": 60
  }
}
```

### **500 Internal Server Error**
```json
{
  "detail": "Error interno del servidor"
}
```

---

## 📚 Documentación Adicional

- **Guía Completa**: `GUIA_COMPLETA.md`
- **Quick Start**: `QUICK_START.md`
- **Deployment**: `DEPLOYMENT_GUIDE.md`
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

**¡API Reference completa del Sistema Comercial! 🚀**
