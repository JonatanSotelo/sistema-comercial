# 🚀 Checklist de Deploy - v0.8.0

## 📋 Pre-Deploy

### 1. Verificar Requirements
```bash
# En backend/requirements.txt deben estar:
httpx>=0.27
qrcode[pil]==7.4.2
Pillow>=10.0
reportlab==4.0.7
```

### 2. Backup de Producción (CRÍTICO)
```bash
# Desde el servidor de producción
docker compose exec sc_backend python -m app.services.backup_service
# O via UI: /app/backups → "Crear Backup"
# Descargar el .zip antes de continuar
```

### 3. Variables de Entorno Nuevas

**⚠️ AGREGAR en producción (.env o secrets):**

```bash
# === NOTIFICACIONES (v0.8.0) ===
NOTIFY_ON_READY=true                                    # true para habilitar
NOTIFY_WHATS_ENDPOINT=https://tu-bot-prod.com/webhook  # URL del bot WhatsApp
NOTIFY_WHATS_TOKEN=tu-token-secreto-prod-12345         # Token seguro

# === SMTP (Opcional) ===
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=sistema@tuempresa.com
SMTP_PASS=app-password-secreto
SMTP_FROM=noreply@tuempresa.com

# === EXISTENTES (verificar) ===
SECRET_KEY=produccion-secret-cambiar-esto-por-uno-real-largo-y-seguro
DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/dbname
ENV=production
TZ=America/Argentina/Buenos_Aires
WHATS_ORDERS_TOKEN=tu-token-whatsapp-orders-prod
WHATS_CREATE_ORDERS=true
BACKUP_DIR=/data/backups
```

**🔒 Seguridad:**
- `NOTIFY_WHATS_TOKEN`: Mínimo 32 caracteres aleatorios
- `SECRET_KEY`: Mínimo 64 caracteres aleatorios
- NO commitear estos valores en git
- Usar secrets manager si está disponible

---

## 🚀 Deploy Steps

### Opción A: Docker Compose (Recomendado)

#### 1. Pull del código
```bash
cd /ruta/al/proyecto
git fetch --all --tags
git checkout v0.8.0
```

#### 2. Rebuild con nuevas dependencias
```bash
# Detener servicios
docker compose -f docker-compose.prod.yml down

# Rebuild (incluye httpx, qrcode, Pillow)
docker compose -f docker-compose.prod.yml build --no-cache sc_backend

# Iniciar base de datos primero
docker compose -f docker-compose.prod.yml up -d sc_postgres sc_redis

# Esperar 10s para que postgres esté ready
sleep 10
```

#### 3. Aplicar Migraciones
```bash
# Ver estado actual
docker compose -f docker-compose.prod.yml run --rm sc_backend alembic current

# Aplicar migraciones de v0.8.0
docker compose -f docker-compose.prod.yml run --rm sc_backend alembic upgrade head

# Verificar que llegó a d3e4f5g6h7i8 (head)
docker compose -f docker-compose.prod.yml run --rm sc_backend alembic current
```

**✅ Expected:** `d3e4f5g6h7i8 (head)`

#### 4. Iniciar Backend
```bash
# Iniciar todo
docker compose -f docker-compose.prod.yml up -d

# Ver logs
docker compose -f docker-compose.prod.yml logs -f sc_backend
```

### Opción B: Deploy Manual / Cloud

#### 1. Instalar Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### 2. Aplicar Migraciones
```bash
alembic upgrade head
alembic current  # Verificar d3e4f5g6h7i8
```

#### 3. Restart Service
```bash
# Systemd
sudo systemctl restart sistema-comercial

# PM2
pm2 restart sistema-comercial

# Supervisor
supervisorctl restart sistema-comercial
```

---

## ✅ Post-Deploy Verification

### 1. Health Check (30s)
```bash
BASE="https://tu-dominio-prod.com"

# Backend up
curl -s "$BASE/health" | jq .

# Expected: {"status":"ok"}
```

### 2. Login y UI (1 min)
```bash
# Login page
curl -s -o /dev/null -w "%{http_code}\n" "$BASE/app/login"
# Expected: 200

# Dashboard (puede redirect si no auth)
curl -s -o /dev/null -w "%{http_code}\n" "$BASE/app/dashboard"
# Expected: 200 o 302
```

### 3. Migración Aplicada (30s)
```bash
# Via API (requiere auth)
TOKEN="tu-admin-token"

# Verificar que pedidos tienen venta_id
curl -s "$BASE/pedidos/1" -H "Authorization: Bearer $TOKEN" | jq '.venta_id'
# Expected: null o un número (no debe fallar)
```

### 4. Notificaciones (2 min)

**Manual:**
1. Ir a `/app/pedidos`
2. Crear/tomar un pedido
3. Cambiar a estado **LISTO**
4. Ir a `/app/auditoria?q=notificaciones`
5. **✅ Verificar**: Debe aparecer registro con:
   ```json
   {
     "table_name": "notificaciones",
     "action": "CREATE",
     "details": {
       "type": "order_ready",
       "success": true/false,
       "phone": "...",
       "items_count": N
     }
   }
   ```

**Si `success: false`:**
- Revisar logs: `docker compose logs sc_backend | grep notif`
- Verificar que `NOTIFY_WHATS_ENDPOINT` es accesible
- Verificar que bot responde en ese endpoint

### 5. PDFs (2 min)

**Remito:**
```bash
# Via curl (requiere auth)
curl -s -o /tmp/remito_test.pdf "$BASE/ventas/1/remito.pdf" \
  -H "Authorization: Bearer $TOKEN"

# Verificar tamaño
ls -lh /tmp/remito_test.pdf
# Expected: > 5KB (no debe ser vacío)
```

**Etiqueta:**
```bash
# Via curl
curl -s -o /tmp/label_test.pdf "$BASE/pedidos/1/label.pdf" \
  -H "Authorization: Bearer $TOKEN"

# Verificar tamaño
ls -lh /tmp/label_test.pdf
# Expected: > 3KB
```

**Manual:**
1. Ir a `/app/pedidos`
2. Click en **🏷️ Etiqueta** de cualquier pedido
3. **✅ Verificar**: Se descarga PDF con QR + datos del pedido
4. Si hay pedido FACTURADO, click en **📄 Remito**
5. **✅ Verificar**: Se descarga PDF con cliente, items, firma

### 6. Reservas (verificar que v0.7.5 sigue OK) (2 min)

1. Ir a `/app/pedidos`
2. En lookup de producto ver **"Disponible: X"**
3. Crear pedido nuevo
4. Cambiar a **EN_PREPARACION**
5. **✅ Verificar**:
   - Si hay stock → pasa OK
   - Si no hay → error 409/400 con mensaje claro
6. Crear segundo pedido con mismo producto
7. Intentar pasar a EN_PREPARACION
8. **✅ Verificar**: Si el primer pedido consumió todo → debe fallar

### 7. Backups (1 min)

1. Ir a `/app/backups`
2. Click en "Crear Backup"
3. **✅ Verificar**: Se crea archivo .zip con timestamp
4. Descargar y verificar que no está corrupto

---

## 🔥 Rollback (Si algo falla)

### Opción 1: Rollback de Código
```bash
# Volver a v0.7.5
git checkout v0.7.5

# Rebuild
docker compose -f docker-compose.prod.yml build sc_backend

# Restart
docker compose -f docker-compose.prod.yml up -d
```

**⚠️ NO hacer downgrade de DB** - La migración `d3e4f5g6h7i8` solo agrega columna `venta_id` nullable, no rompe nada.

### Opción 2: Rollback de DB (Solo si crítico)
```bash
# Ver historial
docker compose -f docker-compose.prod.yml run --rm sc_backend alembic history

# Downgrade a versión anterior
docker compose -f docker-compose.prod.yml run --rm sc_backend \
  alembic downgrade c1d2e3f4g5h6

# Restart
docker compose -f docker-compose.prod.yml up -d
```

### Opción 3: Restaurar Backup
```bash
# Si el sistema está roto, restaurar backup pre-deploy
docker compose -f docker-compose.prod.yml exec sc_backend \
  python -m app.services.backup_service restore /data/backups/backup-YYYYMMDD-HHMMSS.zip
```

---

## 📊 Monitoring Post-Deploy (24h)

### Logs a Monitorear

```bash
# Errores en backend
docker compose -f docker-compose.prod.yml logs -f sc_backend | grep -i error

# Notificaciones
docker compose -f docker-compose.prod.yml logs -f sc_backend | grep notif

# PDFs
docker compose -f docker-compose.prod.yml logs -f sc_backend | grep -E "remito|label"
```

### Métricas Clave

1. **Notificaciones:**
   - Auditoría: `SELECT COUNT(*) FROM auditoria WHERE table_name='notificaciones' AND created_at > NOW() - INTERVAL '24 hours'`
   - Success rate: Comparar `success: true` vs `success: false`

2. **PDFs generados:**
   - Logs: Buscar `[label]` y `[remito]` en logs
   - Errores: Buscar "Error drawing QR" o "Error generating PDF"

3. **Reservas:**
   - Estado: `SELECT COUNT(*) FROM stock_reservations WHERE estado='RESERVADA'`
   - No debe crecer indefinidamente (se consumen al facturar)

### Alertas Recomendadas

- ❌ Tasa de error en notificaciones > 10%
- ❌ PDFs que fallan al generar
- ❌ Reservas que no se liberan (stuck en RESERVADA > 7 días)
- ❌ Endpoint `/health` con status != ok

---

## 🐛 Troubleshooting Común

### 1. "Notificación no enviada"

**Síntomas:** Auditoría muestra `success: false`

**Diagnóstico:**
```bash
# Ver logs detallados
docker compose logs sc_backend | grep -A 5 "notify_order_ready"

# Verificar conectividad al bot
curl -X POST "$NOTIFY_WHATS_ENDPOINT" \
  -H "Authorization: Bearer $NOTIFY_WHATS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"test": true}'
```

**Soluciones:**
- Verificar que `NOTIFY_WHATS_ENDPOINT` es correcto y accesible
- Verificar que `NOTIFY_WHATS_TOKEN` es válido
- Verificar que el bot responde en ese endpoint
- Si el bot está caído, las notificaciones se registrarán como fallidas pero el cambio de estado pasará OK

### 2. "PDF vacío o error"

**Síntomas:** PDF se descarga pero está corrupto o vacío

**Diagnóstico:**
```bash
# Verificar dependencias instaladas
docker compose exec sc_backend pip list | grep -E "reportlab|Pillow|qrcode"

# Verificar logs de generación
docker compose logs sc_backend | grep -E "generate_.*_pdf"
```

**Soluciones:**
- Verificar que `reportlab`, `Pillow`, `qrcode[pil]` están instalados
- Rebuild de la imagen: `docker compose build --no-cache sc_backend`
- Verificar que hay datos en el pedido/venta (items no vacíos)

### 3. "Error al crear reservas"

**Síntomas:** 409/400 al cambiar a EN_PREPARACION

**Diagnóstico:**
```bash
# Ver reservas activas del producto
psql -c "SELECT p.nombre, SUM(sr.cantidad) as reservado 
FROM stock_reservations sr 
JOIN productos p ON p.id=sr.producto_id 
WHERE sr.estado='RESERVADA' 
GROUP BY p.id, p.nombre"

# Ver disponible vs stock
psql -c "SELECT nombre, stock, 
  (stock - COALESCE((SELECT SUM(cantidad) FROM stock_reservations 
   WHERE producto_id=productos.id AND estado='RESERVADA'), 0)) as disponible
FROM productos WHERE stock > 0"
```

**Soluciones:**
- Si hay reservas "stuck": Verificar pedidos antiguos en EN_PREPARACION
- Cancelar pedidos que no se van a facturar (libera reservas)
- Ajustar stock del producto si es incorrecto

### 4. "Migración no aplicada"

**Síntomas:** Error "column venta_id does not exist"

**Diagnóstico:**
```bash
# Ver estado de migraciones
docker compose exec sc_backend alembic current

# Ver si la migración existe
docker compose exec sc_backend alembic history | grep d3e4f5g6h7i8
```

**Soluciones:**
```bash
# Forzar upgrade
docker compose exec sc_backend alembic upgrade head

# Si falla, verificar logs
docker compose exec sc_backend alembic upgrade head -v

# Si sigue fallando, verificar que postgres está up
docker compose ps sc_postgres
```

---

## 📞 Contacto y Soporte

### En caso de problemas críticos:

1. **Rollback inmediato** (ver sección Rollback arriba)
2. **Capturar evidencia**:
   ```bash
   # Logs
   docker compose logs sc_backend > backend_error.log
   
   # Estado DB
   docker compose exec sc_backend alembic current > migration_status.txt
   
   # Variables
   docker compose exec sc_backend env | grep -E "NOTIFY|SMTP" > env_vars.txt
   ```
3. **Restaurar backup** si el sistema está inoperativo

### Logs para Debug

```bash
# Todo (últimas 200 líneas)
docker compose logs --tail=200 sc_backend

# Solo errores
docker compose logs sc_backend | grep -i error

# Solo notificaciones
docker compose logs sc_backend | grep notif

# Solo PDFs
docker compose logs sc_backend | grep -E "remito|label"

# En tiempo real
docker compose logs -f --tail=50 sc_backend
```

---

## ✅ Deploy Exitoso

Si completaste todos los checks ✅ de la sección "Post-Deploy Verification":

### 🎉 **¡Deploy v0.8.0 Completado!**

**Funcionalidades nuevas operativas:**
- ✅ Notificaciones WhatsApp automáticas en LISTO
- ✅ Remito PDF descargable desde ventas
- ✅ Etiqueta PDF con QR desde pedidos
- ✅ UI con botones contextuales
- ✅ Reservas de stock (v0.7.5) funcionando
- ✅ Auditoría completa de todas las operaciones

**Próximos pasos:**
1. Monitorear logs por 24-48h
2. Verificar tasa de éxito de notificaciones
3. Recolectar feedback de usuarios sobre PDFs
4. Planificar v0.8.1 (fix tests unitarios si es necesario)

---

**Fecha de Deploy:** _____________  
**Deployed por:** _____________  
**Versión anterior:** v0.7.5  
**Versión actual:** v0.8.0  
**Rollback disponible:** Sí (v0.7.5 + backup)

---

## 📚 Documentación Relacionada

- `RELEASE_NOTES_v0.8.0.md` - Release notes completas
- `MODULO_PEDIDOS_V0.8.0.md` - Documentación del módulo
- `INTEGRACION_WHATSAPP.md` - Sección notificaciones
- `VALIDACION_RESERVAS.md` - Tests de reservas (v0.7.5)
- `docs/DEV_DATABASE_CHECKS.md` - Troubleshooting DB

---

**🚀 Deploy preparado por:** Sistema Comercial Team  
**📅 Última actualización:** 2025-11-21  
**🏷️ Versión:** v0.8.0

