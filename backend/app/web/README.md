# Módulo Web - Frontend Python-first

Este módulo implementa un frontend completamente en Python usando FastAPI + Jinja2 + HTMX, eliminando la dependencia de Node.js/React.

## Stack Tecnológico

- **FastAPI**: Framework web principal
- **Jinja2**: Motor de templates
- **HTMX**: Interactividad sin JavaScript personalizado
- **Tailwind CSS**: Estilos via CDN
- **Alpine.js**: Interacciones simples de UI
- **httpx**: Cliente HTTP para llamadas al API backend

## Estructura

```
app/web/
├── __init__.py
├── core.py              # Settings y configuración
├── deps.py              # SessionMiddleware, httpx client, helpers
├── router.py            # Router principal que monta sub-routers
├── routers/
│   ├── __init__.py
│   ├── shared.py        # Utilidades compartidas
│   ├── auth.py          # Login/logout
│   ├── productos.py     # CRUD completo de productos
│   ├── clientes.py      # CRUD de clientes
│   ├── proveedores.py   # Base para proveedores
│   ├── ventas.py        # Base para ventas
│   └── compras.py       # Base para compras

app/templates/
├── base.html            # Template base con navbar y estructura
├── login.html           # Página de login
├── dashboard.html       # Dashboard principal
├── productos/
│   ├── index.html       # Página principal de productos
│   ├── _table.html      # Fragmento HTMX: tabla con paginación
│   └── _form.html       # Fragmento HTMX: formulario modal
├── clientes/
│   ├── index.html
│   ├── _table.html
│   └── _form.html
├── proveedores/
│   └── index.html       # Placeholder
├── ventas/
│   └── index.html       # Placeholder
└── compras/
    └── index.html       # Placeholder
```

## Configuración

Variables de entorno en `.env`:

```bash
# URL base del API (para llamadas internas desde el servidor)
API_BASE_URL=http://localhost:8000

# Secret key para SessionMiddleware (debe coincidir con la del backend)
SECRET_KEY=tu-secret-key-muy-segura-cambiala-en-produccion
```

## Autenticación

El flujo de autenticación funciona así:

1. Usuario ingresa credenciales en `/app/login`
2. El servidor llama a `/auth/oauth2/token` del backend
3. Guarda el `access_token` en la sesión (cookie firmada)
4. Usa el token en todas las llamadas al API con header `Authorization: Bearer {token}`
5. Los datos del usuario se guardan en `request.session["user"]`

## Patrón HTMX

Todos los módulos CRUD siguen este patrón:

### index.html
- Página completa con buscador y contenedor para la tabla
- Usa `hx-get` para cargar la tabla dinámicamente
- Botón "Nuevo" que abre el formulario modal

### _table.html
- Fragmento HTML con la tabla y paginación
- Botones de acción: Editar, Toggle Activo, Eliminar
- Cada acción dispara un evento HTMX

### _form.html
- Modal con formulario para crear/editar
- Usa `hx-post` para guardar
- Al guardar con éxito, dispara evento `refreshTable` para actualizar la tabla
- Se cierra automáticamente con `HX-Redirect`

## Endpoints Web

Todos bajo el prefijo `/app`:

- `GET /app/` - Redirige a login o dashboard
- `GET /app/login` - Página de login
- `POST /app/login` - Procesa login
- `GET /app/logout` - Cierra sesión
- `GET /app/dashboard` - Dashboard principal

### Productos
- `GET /app/productos` - Listado principal
- `GET /app/productos/table?page=1&size=20&search=...` - Tabla HTMX
- `GET /app/productos/form?id=...` - Formulario modal
- `POST /app/productos/save` - Guardar producto
- `DELETE /app/productos/{id}` - Eliminar
- `PATCH /app/productos/{id}/toggle` - Toggle activo
- `GET /app/productos/export` - Exportar Excel

### Clientes
Similar a productos (ver `clientes.py`)

### Otros módulos
Proveedores, Ventas y Compras tienen estructura base pero requieren implementación completa siguiendo el patrón de Productos.

## TODOs Pendientes

1. **Proveedores**: Implementar CRUD completo similar a productos/clientes
2. **Ventas**: Implementar alta con items, listado, detalle
3. **Compras**: Implementar alta con items, listado, detalle
4. **Validaciones**: Mejorar validaciones client-side
5. **Mensajes**: Sistema de notificaciones/toasts más robusto
6. **Permisos**: Integrar sistema de permisos por rol
7. **Tests**: Agregar tests E2E para el frontend web

## Desarrollo Local

1. Instalar dependencias:
```bash
cd backend
pip install -r requirements.txt
```

2. Iniciar servidor:
```bash
uvicorn app.main:app --reload
```

3. Acceder a:
- API Docs: http://localhost:8000/docs
- Frontend Web: http://localhost:8000/app
- Login: http://localhost:8000/app/login

Credenciales por defecto (desarrollo):
- Usuario: `admin`
- Password: `admin123`

## Ventajas de este Enfoque

✅ **Sin Node.js**: No requiere npm, webpack, babel, etc.
✅ **Server-Side Rendering**: Mejora SEO y tiempo de carga inicial
✅ **Simplicidad**: Un solo lenguaje (Python) para backend y frontend
✅ **Mantenibilidad**: Código más simple y menos dependencias
✅ **Deploy**: Más fácil de desplegar (un solo proceso)
✅ **Performance**: HTMX envía solo HTML necesario, no JSON pesado
✅ **Progressive Enhancement**: Funciona sin JavaScript (excepto HTMX)

## Migración desde React

El frontend anterior en React/Vite queda obsoleto. Para limpiar:

```bash
# Opcional: eliminar frontend antiguo
rm -rf frontend/
```

Este nuevo frontend está completamente integrado en el backend FastAPI.


