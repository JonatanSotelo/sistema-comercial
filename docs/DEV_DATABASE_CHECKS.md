# Database Checks - Foreign Keys

## Evitar el Paginador (Pager) en psql

Cuando uses `psql` en scripts o comandos automatizados, **siempre desactiva el paginador** para evitar que el terminal se bloquee esperando input del usuario.

### Métodos:

1. **Flag `-P pager=off`** (recomendado para scripts):
   ```bash
   psql -U appuser -d appdb -P pager=off -c "SELECT * FROM users;"
   ```

2. **Variable de entorno** (para toda la sesión):
   ```bash
   export PAGER=cat
   psql -U appuser -d appdb -c "SELECT * FROM users;"
   ```

3. **Dentro de psql interactivo**:
   ```sql
   \pset pager off
   ```

4. **Configuración global** (`~/.psqlrc`):
   ```
   \pset pager off
   ```

## Verificar Foreign Keys a `users`

### Quick Check (1 comando)

**PowerShell:**
```powershell
.\scripts\check_db_fks.ps1
```

**Bash:**
```bash
bash scripts/check_db_fks.sh
```

### Manual Check

```bash
docker compose -f docker-compose.dev.yml exec -T sc_postgres \
  psql -U appuser -d appdb -P pager=off -f /app/scripts/sql/check_fks_users.sql
```

### Qué esperar

**✅ Resultado correcto:**
- Primer query: Lista todas las FKs que apuntan a `users` (debe haber varias)
- Segundo query: 0 filas (no debe haber FKs a `usuarios`)
- Tercer query: Solo debe existir tabla `users`, no `usuarios`

**⚠️ Problema detectado:**
- Si el segundo query devuelve filas → hay FKs apuntando a tabla obsoleta `usuarios`
- **Solución:** Ejecutar migración de fix:
  ```bash
  docker compose -f docker-compose.dev.yml exec -T sc_backend alembic upgrade head
  ```

## Pipeline Completo de Verificación

### 1. Reconstruir y Migrar
```bash
docker compose -f docker-compose.dev.yml up -d --build
docker compose -f docker-compose.dev.yml exec -T sc_backend alembic upgrade head
docker compose -f docker-compose.dev.yml exec -T sc_backend alembic current
```

### 2. Check FKs
```bash
# PowerShell
.\scripts\check_db_fks.ps1

# Bash
bash scripts/check_db_fks.sh
```

### 3. Smoke Test FK
```bash
# Obtener token
TOKEN=$(docker compose -f docker-compose.dev.yml exec -T sc_backend sh -c \
  "curl -s -X POST http://localhost:8000/auth/login \
   -H 'Content-Type: application/json' \
   -d '{\"username\":\"admin\",\"password\":\"admin\"}' \
   | jq -r '.access_token // .token'")

# Crear pedido (debe usar created_by con FK a users)
curl -s -X POST http://localhost:8000/pedidos \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cliente_id":null,"items":[{"producto_id":1,"cantidad":1,"precio_unitario":100}]}'
```

## Troubleshooting

### Terminal bloqueado con `less` o paginador

**Síntomas:**
- Terminal muestra `(END)` o `:` al final
- No puedes escribir comandos nuevos

**Solución inmediata:**
1. Presiona `q` para salir del paginador
2. Si no responde, presiona `Ctrl+C`
3. Como último recurso, cierra la terminal y abre una nueva

**Prevención:**
- Usa siempre `-P pager=off` en comandos `psql` automatizados
- Usa `-T` flag en `docker compose exec` para modo no-interactivo

### Alembic: Multiple heads

**Síntomas:**
```
Multiple head revisions are present for given argument 'head'
```

**Solución:**
```bash
# Ver heads
docker compose -f docker-compose.dev.yml exec sc_backend alembic heads

# Crear merge
docker compose -f docker-compose.dev.yml exec sc_backend \
  alembic merge -m "merge heads" <head1> <head2>

# Aplicar
docker compose -f docker-compose.dev.yml exec -T sc_backend alembic upgrade head
```

### FK Constraint Violation

**Síntomas:**
```
psycopg2.errors.ForeignKeyViolation: ... references table "usuarios"
```

**Causa:** Migración antigua que referencia tabla obsoleta

**Solución:**
1. Identificar la migración problemática
2. Editar el archivo para cambiar `usuarios` → `users`
3. Si la migración ya se aplicó, crear una migración de fix (como `fix_users_fks`)

## Archivos Relacionados

- `scripts/sql/check_fks_users.sql` - Query de diagnóstico
- `scripts/check_db_fks.ps1` - Script PowerShell para Windows
- `scripts/check_db_fks.sh` - Script Bash para Linux/Mac
- `backend/migrations/versions/c1d2e3f4g5h6_fix_users_fks.py` - Migración de fix

## Convenciones del Proyecto

1. **Tabla de usuarios:** `users` (NO `usuarios`)
2. **Columnas de FK a usuarios:** Típicamente `user_id` o `created_by`
3. **ON DELETE por defecto:** `SET NULL` (para audit trail)
4. **ON DELETE para cascada:** Solo en tablas dependientes (ej: `notificaciones`)
5. **Naming FKs:** `fk_{src_table}_{src_column}__{ref_table}_{ref_column}`

---

**Última actualización:** 2025-11-21  
**Versión:** v0.7.5 (Reservas + FK Fix)

