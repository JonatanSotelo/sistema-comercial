# Sistema Comercial - Frontend

Frontend moderno para el Sistema Comercial, construido con React, TypeScript y Tailwind CSS.

## 🚀 Características

- **React 18** con TypeScript para type safety
- **Tailwind CSS** para estilos modernos y responsivos
- **React Router** para navegación
- **React Query** para manejo de estado del servidor
- **Lucide React** para iconos
- **Diseño neutral** y profesional
- **Responsive** - funciona en desktop, tablet y móvil
- **Accesible** - fácil de usar para cualquier nivel técnico

## 🎨 Diseño UI/UX

### Principios de Diseño
- **Neutral y Profesional** - Colores corporativos neutros
- **Minimalista** - Interfaz limpia y sin distracciones
- **Consistente** - Patrones de diseño uniformes
- **Accesible** - Fácil de usar para cualquier nivel técnico

### Paleta de Colores
- **Primario**: Azul corporativo (#2563EB)
- **Secundario**: Gris profesional (#64748B)
- **Éxito**: Verde (#10B981)
- **Advertencia**: Naranja (#F59E0B)
- **Error**: Rojo (#EF4444)
- **Fondo**: Gris claro (#F8FAFC)

## 📁 Estructura del Proyecto

```
frontend/
├── src/
│   ├── components/          # Componentes reutilizables
│   │   ├── Layout.tsx       # Layout principal
│   │   ├── Sidebar.tsx      # Barra lateral de navegación
│   │   ├── Header.tsx       # Header de la aplicación
│   │   ├── MetricCard.tsx   # Tarjeta de métricas
│   │   ├── ChartCard.tsx    # Tarjeta de gráficos
│   │   └── ...
│   ├── pages/               # Páginas de la aplicación
│   │   ├── DashboardPage.tsx
│   │   ├── ProductosPage.tsx
│   │   ├── ClientesPage.tsx
│   │   └── ...
│   ├── services/            # Servicios de API
│   │   └── api.ts           # Cliente de API
│   ├── contexts/            # Contextos de React
│   │   └── AuthContext.tsx  # Contexto de autenticación
│   ├── types/               # Tipos TypeScript
│   │   └── index.ts         # Definiciones de tipos
│   ├── styles/              # Estilos globales
│   │   └── globals.css      # Estilos con Tailwind
│   ├── App.tsx              # Componente principal
│   └── main.tsx             # Punto de entrada
├── package.json
├── tailwind.config.js
├── vite.config.ts
└── tsconfig.json
```

## 🛠️ Instalación y Desarrollo

### Prerrequisitos
- Node.js 18+ 
- npm o yarn
- Backend del Sistema Comercial ejecutándose

### Instalación
```bash
# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env

# Iniciar servidor de desarrollo
npm run dev
```

### Scripts Disponibles
```bash
# Desarrollo
npm run dev          # Inicia servidor de desarrollo

# Construcción
npm run build        # Construye para producción
npm run preview      # Previsualiza build de producción

# Linting
npm run lint         # Ejecuta ESLint
```

## 🔧 Configuración

### Variables de Entorno
Crea un archivo `.env` en la raíz del proyecto:

```env
# URL del backend
VITE_API_URL=http://localhost:8000

# Configuración de la aplicación
VITE_APP_NAME=Sistema Comercial
VITE_APP_VERSION=1.0.0
VITE_DEBUG=true
```

### Configuración de Tailwind
El proyecto usa Tailwind CSS con configuración personalizada en `tailwind.config.js`:
- Colores corporativos personalizados
- Fuentes optimizadas
- Animaciones personalizadas
- Componentes base reutilizables

## 📱 Páginas Disponibles

### Dashboard
- Vista general del negocio
- Métricas clave en tiempo real
- Gráficos y análisis
- Alertas y notificaciones

### Gestión de Productos
- Catálogo de productos
- Búsqueda y filtros
- Gestión de stock
- Exportación de datos

### Gestión de Clientes
- Base de datos de clientes
- Historial de compras
- Segmentación de clientes

### Gestión de Proveedores
- Catálogo de proveedores
- Integración automática
- Gestión de pedidos

### Ventas y Compras
- Registro de transacciones
- Seguimiento de pedidos
- Análisis de tendencias

### Métricas y Reportes
- KPIs del negocio
- Reportes financieros
- Análisis de rendimiento

### Configuración
- Perfil de usuario
- Configuración del sistema
- Preferencias de notificaciones

## 🎯 Funcionalidades Clave

### Autenticación
- Login y registro de usuarios
- Gestión de sesiones
- Roles y permisos

### Dashboard Interactivo
- Métricas en tiempo real
- Gráficos dinámicos
- Alertas inteligentes

### Gestión de Datos
- CRUD completo para todas las entidades
- Búsqueda y filtros avanzados
- Paginación y ordenamiento

### Exportación
- Exportar datos en múltiples formatos
- Reportes personalizados
- Programación de reportes

### Responsive Design
- Adaptable a todos los dispositivos
- Navegación móvil optimizada
- Interfaz táctil amigable

## 🔒 Seguridad

- Autenticación JWT
- Validación de formularios
- Sanitización de datos
- Rutas protegidas

## 🚀 Despliegue

### Build de Producción
```bash
npm run build
```

### Variables de Entorno de Producción
```env
VITE_API_URL=https://api.tu-dominio.com
VITE_DEBUG=false
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Si tienes preguntas o necesitas ayuda:
- Revisa la documentación del backend
- Abre un issue en GitHub
- Contacta al equipo de desarrollo

---

**¡El frontend está listo para usar!** 🎉














