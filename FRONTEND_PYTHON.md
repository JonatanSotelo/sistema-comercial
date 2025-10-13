# Frontend Python - Guía de Inicio Rápido

## 🎉 Nuevo Frontend: FastAPI + Jinja2 + HTMX

Hemos reemplazado completamente el frontend de React/Vite por un enfoque Python-first que elimina la dependencia de Node.js y simplifica el desarrollo y deployment.

## 🚀 Inicio Rápido

### 1. Instalar Dependencias

```bash
cd sistema-comercial/backend
pip install -r requirements.txt
```

Las únicas dependencias nuevas son:
- `jinja2`: Motor de templates (ya incluido en requirements.txt)
- `httpx`: Cliente HTTP (ya estaba instalado)
- `python-multipart`: Para formularios (ya estaba instalado)

### 2. Configurar Variables de Entorno

Editar `backend/.env` y asegurar:

```bash
# URL base del API (para desarrollo local)
API_BASE_URL=http://localhost:8000

# Secret key (debe ser la misma que SECRET_KEY del backend)
SECRET_KEY=tu-secret-key-muy-segura-cambiala-en-produccion

# Credenciales admin (opcional, se crean automáticamente en dev)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

### 3. Iniciar el Servidor

```bash
cd sistema-comercial/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Acceder al Sistema

Abrir en el navegador:

**🌐 Frontend Web (nuevo):**
- URL: http://localhost:8000/app
- Login: http://localhost:8000/app/login

**📚 API Docs (sigue funcionando igual):**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 5. Login

Credenciales por defecto (modo desarrollo):
```
Usuario: admin
Password: admin123
```

## 📁 Estructura del Frontend

```
backend/
├── app/
│   ├── web/                    # Módulo web (nuevo)
│   │   ├── core.py            # Settings
│   │   ├── deps.py            # SessionMiddleware, httpx
│   │   ├── router.py          # Router principal
│   │   └── routers/           # Sub-routers por módulo
│   │       ├── auth.py        # Login/logout
│   │       ├── productos.py   # CRUD productos ✅
│   │       ├── clientes.py    # CRUD clientes ✅
│   │       ├── proveedores.py # Base (TODO)
│   │       ├── ventas.py      # Base (TODO)
│   │       └── compras.py     # Base (TODO)
│   │
│   └── templates/             # Templates Jinja2 (nuevo)
│       ├── base.html          # Layout base
│       ├── login.html         # Login
│       ├── dashboard.html     # Dashboard
│       ├── productos/         # Templates productos
│       │   ├── index.html
│       │   ├── _table.html
│       │   └── _form.html
│       └── clientes/          # Templates clientes
│           ├── index.html
│           ├── _table.html
│           └── _form.html
```

## ✨ Características Implementadas

### ✅ Módulos Completos

1. **Productos** (CRUD completo)
   - Listado con paginación
   - Búsqueda por nombre/código/categoría
   - Crear/Editar/Eliminar
   - Toggle activo/inactivo
   - Exportar a Excel

2. **Clientes** (CRUD completo)
   - Listado con paginación
   - Búsqueda
   - Crear/Editar/Eliminar
   - Exportar a Excel

3. **Autenticación**
   - Login con sesión persistente
   - Logout
   - Protección de rutas

4. **Dashboard**
   - Acceso rápido a todos los módulos
   - Navegación intuitiva

### 🚧 Módulos Pendientes (Base Creada)

- **Proveedores**: Estructura base lista, falta CRUD completo
- **Ventas**: Estructura base lista, falta implementar alta con items
- **Compras**: Estructura base lista, falta implementar alta con items

## 🛠️ Tecnologías Usadas

| Tecnología | Propósito | CDN/Local |
|------------|-----------|-----------|
| **FastAPI** | Framework web | pip install |
| **Jinja2** | Templates HTML | pip install |
| **HTMX** | Interactividad | CDN |
| **Tailwind CSS** | Estilos | CDN |
| **Alpine.js** | Interacciones UI | CDN |
| **httpx** | Cliente HTTP | pip install |

## 🎯 Ventajas vs React/Vite

✅ **Sin Node.js**: No más npm, webpack, babel, etc.
✅ **Un Solo Lenguaje**: Todo en Python
✅ **Menos Dependencias**: Menos archivos node_modules
✅ **Deploy Más Simple**: Un solo proceso
✅ **SEO Friendly**: Server-Side Rendering
✅ **Menos Bundle Size**: Solo HTML, no JS pesado
✅ **Mantenimiento Más Fácil**: Código más simple

## 📝 Patrón de Desarrollo

Cada módulo CRUD sigue este patrón con HTMX:

### 1. Router (`routers/productos.py`)
```python
@router.get("/productos")
async def productos_index(request: Request):
    # Renderiza página principal
    
@router.get("/productos/table")
async def productos_table(request: Request, page: int, search: str):
    # Retorna fragmento HTML de tabla (HTMX)
    
@router.get("/productos/form")
async def producto_form(request: Request, id: int = None):
    # Retorna formulario modal (HTMX)
    
@router.post("/productos/save")
async def producto_save(request: Request, ...):
    # Guarda y dispara evento "refreshTable"
```

### 2. Templates

**index.html**: Página completa con contenedor para tabla
**_table.html**: Fragmento con tabla + paginación
**_form.html**: Modal con formulario

### 3. Eventos HTMX

- `hx-get`: Cargar fragmentos
- `hx-post`: Enviar formularios
- `hx-delete`: Eliminar registros
- `hx-trigger="refreshTable"`: Refrescar tabla después de cambios

## 🧪 Testing

Para probar el frontend:

1. **Login Manual**: Acceder a http://localhost:8000/app/login

2. **Navegación**: Usar el menú superior para acceder a módulos

3. **CRUD Productos**:
   - Click en "Productos"
   - Botón "+ Nuevo Producto" abre modal
   - Completar formulario y guardar
   - Ver tabla actualizada automáticamente
   - Probar editar, toggle activo, eliminar

4. **Búsqueda**: Usar el campo de búsqueda y botón "Buscar"

5. **Paginación**: Navegar entre páginas con botones Anterior/Siguiente

6. **Export**: Click en "Exportar Excel" descarga archivo

## 🐛 Troubleshooting

### Error: "No autenticado"
- Asegurar que estás logueado en `/app/login`
- Verificar que la cookie de sesión esté activa

### Error: "Error de conexión con el servidor"
- Verificar que el backend esté corriendo
- Revisar `API_BASE_URL` en settings

### Modal no se cierra
- Verificar que Alpine.js se cargó correctamente
- Revisar consola del navegador

### Tabla no se actualiza
- Verificar que HTMX se cargó correctamente
- Revisar eventos en Network tab del navegador

## 🔧 Configuración Avanzada

### Cambiar URL del API

Editar `backend/app/web/core.py`:

```python
class WebSettings(BaseSettings):
    API_BASE_URL: str = "http://tu-api.com"  # Cambiar aquí
```

### Agregar Nuevo Módulo CRUD

1. Crear router en `app/web/routers/mi_modulo.py`
2. Crear templates en `app/templates/mi_modulo/`
3. Registrar en `app/web/router.py`:

```python
from app.web.routers import mi_modulo
router.include_router(mi_modulo.router)
```

## 📚 Recursos

- [HTMX Docs](https://htmx.org/docs/)
- [Jinja2 Docs](https://jinja.palletsprojects.com/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)

## ❓ FAQ

**P: ¿Puedo usar el frontend React y este Python al mismo tiempo?**
R: Sí, pero no es recomendable. Este frontend reemplaza completamente al de React.

**P: ¿Funciona sin JavaScript?**
R: HTMX requiere JavaScript, pero no necesitas escribir código JS personalizado.

**P: ¿Cómo agrego validaciones?**
R: En el backend (FastAPI/Pydantic) o en el frontend (HTML5 + JavaScript vanilla).

**P: ¿Puedo personalizar los estilos?**
R: Sí, edita las clases de Tailwind en los templates o agrega CSS personalizado.

**P: ¿Dónde están los tests del frontend?**
R: Pendiente. Se recomienda agregar tests E2E con Playwright o Selenium.

## 🎉 ¡Listo!

El nuevo frontend está completamente funcional para Productos y Clientes. Los módulos de Proveedores, Ventas y Compras tienen la estructura base y solo necesitan replicar el patrón establecido.

**Próximos pasos sugeridos:**

1. ✅ Probar login y navegación
2. ✅ Probar CRUD de productos
3. ✅ Probar CRUD de clientes
4. 🔨 Implementar CRUD de proveedores (siguiendo patrón de productos)
5. 🔨 Implementar ventas con items
6. 🔨 Implementar compras con items

---

**¿Necesitas ayuda?** Revisa el código de referencia en `app/web/routers/productos.py` y `app/templates/productos/` para ver cómo está implementado el patrón completo.


