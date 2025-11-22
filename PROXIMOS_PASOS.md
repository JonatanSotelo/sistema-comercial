# 🚀 PRÓXIMOS PASOS - Sistema Comercial v0.9.x HTMX

**Estado Actual:** ✅ Código restaurado y bugs corregidos  
**Branch:** `main` (origin actualizado)  
**Commits aplicados:**
- `5a34176` - Restauración 118 archivos v0.9.1
- `a17eb89` - Corrección 4 bugs críticos
- `1f3a7f0` - Actualización FINAL_STATUS

---

## 📋 COMANDOS PARA EJECUTAR AHORA

### 1️⃣ Rebuild + Migraciones (5-10 min)

```bash
# 1. Rebuild contenedores
docker compose -f docker-compose.dev.yml up -d --build

# 2. Esperar que levanten (30 seg aprox)
Start-Sleep -Seconds 30

# 3. Aplicar migraciones
docker compose -f docker-compose.dev.yml exec sc_backend alembic upgrade head

# 4. Verificar head actual
docker compose -f docker-compose.dev.yml exec sc_backend alembic current
```

**✅ Esperado:** Head en versión `f5g6h7i8j9k0` (cobros_caja) o similar

---

### 2️⃣ Test de Imports (Verificar que Alembic ve todos los modelos)

```bash
docker compose -f docker-compose.dev.yml exec sc_backend python -c "from app.db.base import *; print('✅ OK -', len(__all__), 'modelos'); print(__all__)"
```

**✅ Esperado:** Lista de ~20 modelos sin errores

---

### 3️⃣ Smoke Test Automatizado (2-3 min)

```bash
# Dar permisos (solo primera vez)
chmod +x smoke_quick.sh

# Ejecutar
bash smoke_quick.sh
```

**✅ Esperado:**
```
✅ Login OAuth2
✅ Ventas API
✅ Cobro creado
✅ PDF Recibo (recibo_X.pdf > 1.5 KB)
✅ CSV IVA Compras (iva_compras.csv > 200 bytes)
✅ Backups
```

---

### 4️⃣ Verificación CARRERA (Sin campo "Activo")

```bash
grep -rn "is_active\|<th>Estado" backend/app/templates/ --include="*.html" | grep -v "Estado del Pedido\|Estado de" || echo "✅ Sin referencias a campo Activo"
```

**✅ Esperado:** Mensaje "✅ Sin referencias a campo Activo"

---

### 5️⃣ Quick UI Check (Navegador)

Abrir en navegador:
- http://localhost:8000/app/login (admin / admin123)
- http://localhost:8000/app/ventas
- http://localhost:8000/app/pedidos
- http://localhost:8000/app/cobros
- http://localhost:8000/app/facturacion
- http://localhost:8000/app/reportes

**✅ Esperado:** Todas las páginas cargan sin 404

---

## 🔧 SI ALGO FALLA

### Alembic - Múltiples Heads
```bash
docker compose -f docker-compose.dev.yml exec sc_backend alembic heads
# Si hay múltiples, merge manual necesario
```

### Backend no levanta
```bash
docker compose -f docker-compose.dev.yml logs sc_backend --tail=100
# Buscar errores de import o DB connection
```

### Smoke test falla
```bash
# Ver logs del backend
docker compose -f docker-compose.dev.yml logs sc_backend --tail=50

# Verificar que DB tiene datos
docker compose -f docker-compose.dev.yml exec sc_postgres psql -U appuser -d appdb -c "SELECT COUNT(*) FROM users;"
```

---

## 🎯 DESPUÉS DE VALIDAR TODO

### Opción A: Tag v0.9.2 (Si hubo cambios significativos)
```bash
git tag -a v0.9.2 -m "v0.9.2 - HTMX main finalized: restored v0.9.1 + 4 bug fixes"
git push origin v0.9.2
```

### Opción B: Quedarse en v0.9.1 (Si solo fueron fixes menores)
```bash
# No taggear, v0.9.1 sigue siendo la versión oficial
```

---

## 🌐 ACCIONES EN GITHUB

### ⚠️ CRÍTICO: Cambiar Default Branch

1. Ir a: https://github.com/JonatanSotelo/sistema-comercial/settings/branches
2. En **Default branch**, clic en ⇄ 
3. Seleccionar **`main`**
4. Confirmar: "I understand, update the default branch"

### 📦 OPCIONAL: Renombrar master → react-legacy

```bash
# Opción A: Desde GitHub UI
# Settings → Branches → master → Rename to "react-legacy"

# Opción B: Desde tu máquina
git branch -m master react-legacy
git push origin :master
git push origin react-legacy
git push origin -u react-legacy
```

---

## 📊 RESUMEN DE LO HECHO

### ✅ Completado
- [x] Auditoría completa de código
- [x] Restauración de 118 archivos desde v0.9.1
- [x] Corrección de 4 bugs críticos
- [x] Documentación (FINAL_STATUS.md, TRANSITION_TO_HTMX_MAIN.md)
- [x] Script smoke_quick.sh creado
- [x] Push a GitHub completado

### ⏳ Pendiente (Ejecutar arriba)
- [ ] Rebuild + Migraciones
- [ ] Smoke test
- [ ] Verificación CARRERA
- [ ] Quick UI check
- [ ] Cambiar default branch en GitHub

---

## 🆘 CONTACTO

Si algo no funciona:
1. Revisar `FINAL_STATUS.md` (detalles técnicos completos)
2. Logs: `docker compose -f docker-compose.dev.yml logs sc_backend --tail=200`
3. DB check: `docker compose -f docker-compose.dev.yml exec sc_postgres psql -U appuser -d appdb -c "\dt"`

---

**¡Todo listo para validar!** 🚀

Ejecutá los comandos de arriba en orden y avisame si algo falla.

