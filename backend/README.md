# Sistema Comercial — MVP

FastAPI + SQLAlchemy + Alembic + Postgres (Docker) + Redis.

## Estado

* **Login** con JWT: `POST /auth/oauth2/token` (form) y `POST /auth/login` (JSON).
* **Roles**: `admin` (CRUD completo) y `consulta` (solo lectura).
* **Módulos**: usuarios, productos, clientes, proveedores, compras, ventas, stock, auditoría.
* **Healthcheck**: `GET /health` (sin warnings de OpenAPI).

---

## Requisitos

* Docker Desktop (con Compose)
* Git Bash (Windows) o bash/zsh

---

## Arranque rápido

```bash
# 1) Clonar
 git clone https://github.com/JonatanSotelo/sistema-comercial.git
 cd sistema-comercial

# 2) Levantar servicios
 docker compose -f infra/docker-compose.yml up -d --build

# 3) Ver logs de backend
 docker compose -f infra/docker-compose.yml logs -f backend --tail=100
# Esperar: "Application startup complete."
```

### Variables de entorno (backend/.env)

```ini
SECRET_KEY=super-secreto-cambialo
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DATABASE_URL=postgresql+psycopg2://admin:admin@db:5432/admin
```

> **Nota Windows**: asegurá finales **LF** para scripts. Si hace falta:
>
> ```bash
> dos2unix backend/start.sh 2>/dev/null || true
> ```

---

## Autenticación y uso en /docs

1. Abrir `http://localhost:8000/docs`.
2. Generar token:

   * **Opción A (form)**: `POST /auth/oauth2/token` con `username` y `password`.
   * **Opción B (JSON)**: `POST /auth/login` con body `{ "username":..., "password":... }`.
3. Click en **Authorize** (candado) y pegá el **token** (si te pide “value”, poné solo el token). Si prefieres cURL, usa `Authorization: Bearer <token>`.

**Credenciales iniciales**

* admin / **admin123** (cambiar en producción)
* crear usuarios `consulta` desde `/users/usuarios/` (admin requerido)

---

## Endpoints principales

* **Auth**

  * `POST /auth/oauth2/token` (form: `username`, `password`)
  * `POST /auth/login` (JSON: `{"username","password"}`)
* **Usuarios**

  * `GET /users/usuarios/` (admin)
  * `POST /users/usuarios/` (admin)
  * `PUT /users/usuarios/{user_id}` (admin)
  * `GET /users/usuarios/me` (autenticado)
* **Productos**

  * `GET /productos/` (consulta/admin)
  * `GET /productos/{prod_id}` (consulta/admin)
  * `POST /productos/` (admin)
  * `PUT /productos/{prod_id}` (admin)
  * `DELETE /productos/{prod_id}` (admin)
* **Clientes**

  * `GET /clientes/`, `GET /clientes/{cliente_id}`
* **Proveedores**

  * `GET /proveedores/`, `GET /proveedores/{prov_id}`
* **Compras / Ventas**

  * `GET /compras/`, `GET /compras/{compra_id}`
  * `GET /ventas/`, `GET /ventas/{venta_id}`
* **Stock**

  * `GET /stock/{producto_id}`
  * `GET /compras/stock/{producto_id}`
* **Auditoría**

  * `GET /auditoria/` (admin)
* **Health**

  * `GET /health`

> La lista exacta puede consultarse siempre en `/openapi.json` o `/docs`.

---

## Smoke test (rápido)

```bash
BASE="http://localhost:8000"

# Token admin (elige A o B)
ADMIN_T=$(curl -s -X POST "$BASE/auth/oauth2/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" \
| sed -n 's/.*"access_token":"\([^"]*\)".*/\1/p')

echo "ADMIN_T len=${#ADMIN_T}"

# /me → 200
curl -i "$BASE/users/usuarios/me" -H "Authorization: Bearer $ADMIN_T"

# Crear producto → 201
RESP=$(curl -s -X POST "$BASE/productos/" \
  -H "Authorization: Bearer $ADMIN_T" \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Prod MVP","codigo":"MVP-001","precio":1234}')
echo "$RESP"
ID=$(printf '%s' "$RESP" | grep -oE '"id":[0-9]+' | head -1 | cut -d: -f2)
echo "ID=$ID"

# Update → 200
curl -i -X PUT "$BASE/productos/$ID" \
  -H "Authorization: Bearer $ADMIN_T" \
  -H "Content-Type: application/json" \
  -d '{"precio":1500}'

# Delete → 204
curl -i -X DELETE "$BASE/productos/$ID" -H "Authorization: Bearer $ADMIN_T"

# Auditoría → 200
curl -i "$BASE/auditoria/" -H "Authorization: Bearer $ADMIN_T"
```

---

## Auditoría

* Registra `CREATE/UPDATE/DELETE` con: `username`, `path`, `ip`, `method`, `record_id`, `details`.
* Consultar en `GET /auditoria/` o directamente en la tabla `audit_logs`.

---

## Backup / Restore (rápido)

**Backup**

```bash
docker exec sc_postgres bash -lc 'pg_dump -U admin -d admin -F c -f /tmp/backup.dump'
docker cp sc_postgres:/tmp/backup.dump ./backup_$(date +%Y%m%d_%H%M%S).dump
```

**Restore**

```bash
docker compose -f infra/docker-compose.yml stop backend
pg_restore_cmd="pg_restore -U admin -d admin -c"
docker exec -i sc_postgres bash -lc "$pg_restore_cmd" < backup_YYYYMMDD_HHMMSS.dump
docker compose -f infra/docker-compose.yml start backend
```

---

## Troubleshooting

* **401 Unauthorized**

  * Token vacío/expirado o header mal formado.
  * Revisar: `echo ${#ADMIN_T}` debe ser > 0.
  * Header correcto: `Authorization: Bearer <token>`.
* **403 Solo admin**

  * Asegurar `role='admin'` en `users`.
  * SQL útil: `SELECT id, username, role FROM users WHERE username='admin';`
* **405 Method Not Allowed**

  * `PUT/DELETE` deben ir a `/productos/{id}`.
* **Windows CRLF → bash\r**

  * Convertir a LF: `dos2unix backend/start.sh`.
* **Alembic**

  * `backend/alembic.ini` → `script_location = migrations`.
  * `backend/migrations/env.py` debe importar `app.db.database` correctamente.

---

## Roadmap corto (sugerido)

* Paginación/filtrado en listados.
* Exportar a Excel.
* Seeds de datos de ejemplo.
* Tests (pytest) + CI.
* Endurecer CORS y rotar SECRET\_KEY en prod.

---

## Licencia

Pendiente.
