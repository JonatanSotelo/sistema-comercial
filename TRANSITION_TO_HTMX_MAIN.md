# 🔄 Transición a HTMX como Rama Principal

## ✅ Completado

### Limpieza del Repositorio
- ✅ Eliminados 54 archivos obsoletos
- ✅ Actualizado `.gitignore` y `.gitattributes`
- ✅ README.md reescrito para arquitectura HTMX
- ✅ Rama `main` creada desde `feat/ventas-stock-ui` (v0.9.1)
- ✅ Push completado a GitHub

### Archivos Eliminados
```
Archivos .bat (15):
- DEMO.bat, EJECUTAR.bat, INICIAR.bat, INICIAR_TODO.bat
- LEVANTAR_SISTEMA.bat, PARAR.bat, PROBAR_SISTEMA.bat
- TEST.bat, VERIFICAR.bat, detener_sistema.bat
- iniciar_sistema.bat, install.bat, start*.bat, stop_all.bat
- verificar_sistema.bat, levantar_*.bat

Artifacts de Test y Prueba (15):
- backup_20250901_123102.dump
- bash.exe.stackdump
- check_productos_endpoint.py
- clientes.csv, products.csv, proveedores.csv, iva_compras.csv
- recibo_9.pdf
- comandera.txt
- test_api.js, test_frontend.html, test_audit_qa.py
- test_stock.py, test_stock.sh, test_ultimo_reporte.py
- test_import_export_backups.ps1

Directorios Obsoletos:
- infra/ (10 archivos: docker-compose, package.json, CSVs de prueba)
- nginx/ (1 archivo: nginx.conf)

SQL y Scripts:
- create_reportes_financieros.sql
- create_reportes_simple.sql
- deploy.sh, install.sh
- smoke_v0_9_1.ps1
- nginx.conf (raíz)
```

---

## 📋 Pasos Pendientes (Manual en GitHub)

### 1. Cambiar Rama por Defecto en GitHub

**Ubicación:** https://github.com/JonatanSotelo/sistema-comercial/settings/branches

**Pasos:**
1. Ir a **Settings** → **Branches**
2. En **Default branch**, hacer clic en el ícono de cambio (⇄)
3. Seleccionar **`main`**
4. Confirmar el cambio con "I understand, update the default branch"

**Resultado esperado:** 
- `main` será la rama principal
- PRs nuevos apuntarán a `main` por defecto
- La UI de GitHub mostrará `main` como default

---

### 2. Renombrar `master` → `react-legacy`

**Opción A: Desde tu máquina local (Recomendado)**

```bash
# 1. Renombrar localmente
git branch -m master react-legacy

# 2. Eliminar master remoto
git push origin :master

# 3. Subir react-legacy
git push origin react-legacy

# 4. Configurar upstream
git push origin -u react-legacy
```

**Opción B: Desde GitHub UI**

1. Ir a **Branches** en GitHub
2. Buscar `master`
3. Hacer clic en el menú "..." → **Rename branch**
4. Cambiar a `react-legacy`

**⚠️ Importante:** NO borrar `master`/`react-legacy`. Es histórico y contiene el frontend React original.

---

### 3. (Opcional) Crear Pull Request

Si querés revisión formal antes del merge:

1. Ir a: https://github.com/JonatanSotelo/sistema-comercial/compare/main...chore/repo-cleanup-htmx-main
2. Crear PR con título: **"chore: cleanup repo, adopt HTMX as main"**
3. Descripción:

```markdown
## 🎯 Objetivo
Establecer la línea HTMX como rama principal del proyecto, archivando el frontend React.

## 📦 Cambios Realizados
- ✅ Eliminados 54 archivos obsoletos (.bat, tests antiguos, artifacts)
- ✅ Borrados directorios `infra/` y `nginx/` (legacy React)
- ✅ Actualizado `.gitignore` (caches, backups, node_modules)
- ✅ Creado `.gitattributes` (normalización EOL a LF)
- ✅ README.md reescrito para HTMX-first
- ✅ Rama `main` creada desde `feat/ventas-stock-ui` (v0.9.1)

## 🗂️ Archivos Eliminados (54)
- **15 scripts .bat** (Windows legacy)
- **15 artifacts de test** (CSVs, PDFs, dumps, scripts)
- **Directorio infra/** (10 archivos Node/React)
- **Directorio nginx/** (config obsoleto)
- **SQL y scripts** obsoletos

## 🔧 Stack Tecnológico Actual
- **Backend:** FastAPI + PostgreSQL + Redis
- **Frontend:** HTMX + Jinja2 (server-side rendering)
- **Versión:** v0.9.1 (Cobros & Caja + IVA Compras)

## 📖 Frontend React (Legacy)
El código React original está preservado en la rama `react-legacy` para referencia histórica.

**Acceder:**
```bash
git checkout react-legacy
```

## ✅ DoD Cumplido
- [x] No existen carpetas React, node_modules/, ni *.bat
- [x] .gitignore actualizado
- [x] Rama `main` apunta a HTMX (creada)
- [x] react-legacy documentado
- [x] Docker Compose solo backend + DB + Redis/PgAdmin
- [x] README.md actualizado
- [x] Sin campo "Activo" (CARRERA ✅)

## 🧪 Verificación
```bash
# Tests
docker compose -f docker-compose.dev.yml up -d --build
docker compose -f docker-compose.dev.yml exec sc_backend pytest -q

# Smoke
bash scripts/smoke.sh
```

## 🚦 Breaking Changes
**⚠️ Frontend React eliminado de esta rama.**
- El frontend React NO está en `main`
- Para acceder al React: `git checkout react-legacy`
- La línea activa es HTMX (server-side)

## 📋 Post-Merge
1. Cambiar default branch a `main` en GitHub Settings
2. Renombrar `master` → `react-legacy`
3. Actualizar README si es necesario
```

4. **Merge el PR** (o hacer merge directo si no querés PR):

```bash
# Merge directo sin PR
git checkout main
git merge chore/repo-cleanup-htmx-main --no-ff -m "Merge cleanup: adopt HTMX as main"
git push origin main
```

---

### 4. Verificar Tests y Smoke (Local)

Antes de dar por finalizado, ejecutar:

```bash
# Levantar servicios
docker compose -f docker-compose.dev.yml up -d --build

# Migraciones
docker compose -f docker-compose.dev.yml exec sc_backend alembic upgrade head

# Tests rápidos
docker compose -f docker-compose.dev.yml exec sc_backend pytest tests/test_cobros.py tests/test_pedidos.py -q

# Smoke
bash scripts/smoke.sh
```

**✅ Esperado:**
- Todos los tests pasan
- Smoke test sin errores
- `/app/*` endpoints funcionan
- PDFs (remito, recibo, etiqueta) generan correctamente

---

## 📚 Cómo Acceder al Frontend React (Legacy)

### Desde la Rama `react-legacy`

```bash
# Cambiar a react-legacy
git checkout react-legacy

# Ver estructura
ls -la frontend/

# Levantar (si se requiere)
cd frontend
npm install
npm run dev
```

**Nota:** La rama `react-legacy` NO se mantiene activamente. Es solo histórico.

---

## 🎯 Resultado Final

### Rama Principal: `main`
- **Stack:** FastAPI + PostgreSQL + HTMX/Jinja2
- **Versión:** v0.9.1 (Cobros & Caja + IVA Compras)
- **UI:** Server-side rendering con HTMX
- **Limpio:** Sin .bat, sin node_modules/, sin artifacts

### Rama Legacy: `react-legacy` (master renombrado)
- **Stack:** FastAPI + React/TypeScript
- **Estado:** Archivado (no se mantiene)
- **Propósito:** Referencia histórica

---

## ✅ Checklist Final

- [ ] Cambiar default branch a `main` en GitHub
- [ ] Renombrar `master` → `react-legacy`
- [ ] (Opcional) Crear y mergear PR
- [ ] Verificar tests locales pasan
- [ ] Ejecutar smoke test exitoso
- [ ] Actualizar README si falta algo
- [ ] Comunicar cambio al equipo (si aplica)
- [ ] Borrar rama `chore/repo-cleanup-htmx-main` después del merge

---

## 🆘 Troubleshooting

### Si GitHub no permite cambiar default branch
- Asegurarse de tener permisos de Admin en el repo
- Verificar que la rama `main` existe en GitHub (ya debería estar)

### Si hay problemas con react-legacy
- No borrar `master` hasta confirmar que `react-legacy` está OK
- Backup: `git tag react-legacy-backup master` antes de renombrar

### Si tests fallan
- Revisar que `docker-compose.dev.yml` no tenga referencias a frontend
- Confirmar que `/app/templates/` tiene todos los templates HTMX
- Verificar logs: `docker compose -f docker-compose.dev.yml logs sc_backend --tail=100`

---

## 📞 Contacto

Si algo falla o necesitas ayuda, revisar:
- Este documento
- `README.md` (actualizado)
- Logs del backend
- Tag `v0.9.1` (último release estable)

---

**Fecha de transición:** 2025-11-21  
**Commit de limpieza:** `44b5640`  
**Versión estable:** `v0.9.1`

