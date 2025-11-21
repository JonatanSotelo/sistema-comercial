# v0.8.0 — Notificaciones + Remito + Etiqueta

## ✨ Nuevas Funcionalidades

### 🔔 Notificaciones Automáticas
- **WhatsApp**: Notificación automática cuando un pedido pasa a estado LISTO
- **Reintentos inteligentes**: 3 intentos con backoff exponencial (0.5s, 1s, 2s)
- **No bloqueante**: Ejecutado en `BackgroundTasks` de FastAPI
- **Email opcional**: Soporte para SMTP como backup
- **Auditoría completa**: Registro de todos los intentos en `table_name="notificaciones"`
- **Configuración flexible**: Variables `.env` para habilitar/deshabilitar

### 📄 Remito PDF (Ventas)
- **Endpoints**:
  - `GET /ventas/{id}/remito` - HTML imprimible
  - `GET /ventas/{id}/remito.pdf` - PDF con ReportLab
- **Contenido**: Cliente, fecha, items detallados, total, espacio para firma y observaciones
- **Acceso**: Desde pedidos FACTURADOS (botón "Remito" si tiene `venta_id`)

### 🏷️ Etiqueta PDF con QR (Pedidos)
- **Endpoint**: `GET /pedidos/{id}/label.pdf`
- **QR Code**: JSON con datos del pedido (id, cliente, total, estado)
- **Información legible**: Cliente, teléfono, items, total
- **Tamaño**: A6 (~105x148mm) - ideal para impresoras de etiquetas
- **Disponible en**: Estados EN_PREPARACION, LISTO, FACTURADO

## 🎨 Mejoras de UI

### Botones por Estado
- **EN_PREPARACION / LISTO**: 
  - 🏷️ Etiqueta PDF
  - 🖨️ Packing Slip (HTML)
  - 📄 Packing PDF
- **FACTURADO**:
  - 🏷️ Etiqueta PDF
  - 📄 Remito PDF (si tiene venta vinculada)

### Colores y UX
- Etiqueta: Fondo celeste (`#e1f5fe`)
- Remito: Fondo verde (`#e8f5e9`)
- Tooltips informativos en todos los botones

## 🗄️ Base de Datos

### Nueva Columna
- **pedidos.venta_id**: Link a la venta generada al facturar
  - Tipo: `INTEGER`
  - FK: `ventas.id` ON DELETE SET NULL
  - Permite acceder al remito desde pedidos facturados

### Migración
- `d3e4f5g6h7i8_add_venta_id_to_pedidos.py`

## 🔧 Cambios en Servicios

### notifications_service.py (NUEVO)
- `notify_order_ready(pedido_id)`: Envía notificación WhatsApp/Email
- `_send_whatsapp_notification()`: httpx con reintentos
- `_audit_notification()`: Registro en auditoría

### pedidos_service.py
- `change_estado()`: Hook para notificaciones en LISTO
- `facturar_pedido()`: Guarda `venta_id` en el pedido

### remito_service.py (NUEVO)
- `generate_remito_html()`: HTML imprimible
- `generate_remito_pdf()`: PDF con ReportLab

### label_service.py (NUEVO)
- `generate_label_pdf()`: PDF con QR code y datos del pedido

## 📦 Nuevas Dependencias

### requirements.txt
```
httpx>=0.27          # Cliente HTTP async para notificaciones
qrcode[pil]==7.4.2   # Generación de QR codes
Pillow>=10.0         # Procesamiento de imágenes (requerido por qrcode)
```

## ⚙️ Configuración

### Variables de Entorno (backend/.env)
```bash
# Notificaciones
NOTIFY_ON_READY=false                    # Habilitar notificaciones automáticas
NOTIFY_WHATS_ENDPOINT=                   # URL del webhook del bot WhatsApp
NOTIFY_WHATS_TOKEN=                      # Token de autenticación

# SMTP (Opcional)
SMTP_HOST=                               # Servidor SMTP
SMTP_PORT=587                            # Puerto SMTP
SMTP_USER=                               # Usuario SMTP
SMTP_PASS=                               # Contraseña SMTP
SMTP_FROM=noreply@sistema-comercial.com # Email remitente
```

## 🧪 Tests

### Nuevos Archivos
- `backend/tests/test_notifications.py` - 5 tests de notificaciones
- `backend/tests/test_pdfs.py` - 6 tests de PDFs (remito + etiqueta)

### Cobertura
- ✅ Notificación exitosa (200)
- ✅ Reintentos en fallo (500 → 500 → 200)
- ✅ Auditoría de errores
- ✅ Skip si no hay teléfono
- ✅ Skip si NOTIFY_ON_READY=false
- ✅ Remito HTML y PDF con contenido
- ✅ Etiqueta PDF con contenido
- ✅ Validación 404 para recursos inexistentes

### Ejecutar Tests
```bash
# Todos los tests nuevos
docker compose -f docker-compose.dev.yml exec sc_backend pytest tests/test_notifications.py tests/test_pdfs.py -v

# Solo notificaciones
docker compose -f docker-compose.dev.yml exec sc_backend pytest tests/test_notifications.py -v

# Solo PDFs
docker compose -f docker-compose.dev.yml exec sc_backend pytest tests/test_pdfs.py -v
```

## 🔍 Smoke Tests

### Actualizaciones en scripts/smoke.sh
- `[N1]` - Auditoría de notificaciones
- `[PDF1]` - Remito PDF de venta
- `[PDF2]` - Etiqueta PDF de pedido
- `[PDF3]` - Etiqueta de pedido creado en test

## 📚 Documentación

### Nuevos Documentos
- `MODULO_PEDIDOS_V0.8.0.md` - Documentación completa del módulo
  - Flujo de estados
  - Gestión de reservas
  - Notificaciones automáticas
  - Documentos PDF
  - UI y botones
  - Tests y troubleshooting

### Actualizaciones
- `INTEGRACION_WHATSAPP.md` - Nueva sección "Notificaciones Automáticas"
  - Configuración
  - Payload enviado
  - Comportamiento y reintentos
  - Troubleshooting

## 🔒 Seguridad

### Tokens y Credenciales
- `NOTIFY_WHATS_TOKEN`: Token de autenticación para webhook
- **Auditoría sin tokens**: Los detalles de auditoría NO incluyen tokens sensibles
- **SMTP opcional**: Credenciales SMTP solo en `.env`, nunca en logs

### Validaciones
- Header `X-Integration-Token` requerido en webhook
- Timeout de 5 segundos en requests HTTP
- Validación de teléfono antes de enviar notificación

## 🚀 Deploy

### Pasos
1. **Actualizar dependencies**:
   ```bash
   cd backend
   pip install httpx>=0.27 qrcode[pil]==7.4.2 Pillow>=10.0
   ```

2. **Configurar .env**:
   ```bash
   cp backend/env.example backend/.env
   # Editar .env con valores reales
   ```

3. **Aplicar migraciones**:
   ```bash
   docker compose -f docker-compose.dev.yml exec sc_backend alembic upgrade head
   ```

4. **Rebuild containers**:
   ```bash
   docker compose -f docker-compose.dev.yml up -d --build
   ```

5. **Verificar**:
   ```bash
   ./scripts/smoke.sh
   ```

## 📊 Estadísticas

- **Archivos nuevos**: 9
- **Archivos modificados**: 8
- **Tests nuevos**: 11
- **Migraciones**: 1
- **Líneas de código**: ~1200 (aprox)
- **Endpoints nuevos**: 5

## 🐛 Fixes y Mejoras

### Correcciones
- ✅ Fix FK `created_by` en pedidos (usuarios → users) - heredado de v0.7.5
- ✅ Validación de disponible antes de crear reservas

### Optimizaciones
- ✅ Batch query para calcular disponible de múltiples productos
- ✅ Auditoría asíncrona para no bloquear operaciones críticas
- ✅ Background tasks para notificaciones (no impacta performance)

## 📋 Convenciones Mantenidas

- ✅ No reintroduce campo "Activo"
- ✅ Mantiene HTMX + OOB swap
- ✅ Auditoría completa en todas las operaciones
- ✅ CARRERA: código limpio y consistente
- ✅ Tests exhaustivos con mocks
- ✅ Documentación detallada

## 🎯 Roadmap Futuro

### Posibles Mejoras
- [ ] Dashboard de notificaciones (éxito/fallo por día)
- [ ] Plantillas personalizables para mensajes
- [ ] Notificaciones push (Firebase/OneSignal)
- [ ] Firma digital en remitos
- [ ] Código de barras en etiquetas (además de QR)
- [ ] Email con adjunto PDF automático

## 📞 Soporte

### Problemas Comunes

**Notificación no enviada:**
1. Verificar `NOTIFY_ON_READY=true`
2. Verificar teléfono en pedido/cliente
3. Revisar logs: `docker compose logs sc_backend | grep notif`
4. Revisar auditoría: `/app/auditoria?q=notificaciones`

**PDF vacío o error:**
1. Verificar instalación de Pillow: `pip list | grep Pillow`
2. Verificar fonts del sistema (ReportLab usa Helvetica por defecto)
3. Revisar logs de errores en `generate_*_pdf`

**Remito no aparece en pedido:**
1. Verificar que pedido está FACTURADO
2. Verificar que `pedido.venta_id` no es NULL
3. Aplicar migración `d3e4f5g6h7i8` si falta

---

**Fecha de Release:** 2025-11-21  
**Autor:** Sistema Comercial Team  
**Versión anterior:** v0.7.5 (Reservas + FK Fix)  
**Próximo Sprint:** v0.9.0 (TBD)

## 🙏 Agradecimientos

Gracias al equipo de QA por las validaciones exhaustivas y al equipo de desarrollo del bot WhatsApp por la coordinación en la integración de notificaciones.

---

**¡Sprint v0.8.0 completado exitosamente!** 🎉

