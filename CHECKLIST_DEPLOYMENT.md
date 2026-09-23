# ✅ Checklist de Deployment - Mejoras de Registro y QR

## 📋 Pre-Deployment

### 1. Code Review
- [ ] Revisión de código por líder técnico
- [ ] Validación de patrones y arquitectura
- [ ] Verificación de seguridad
- [ ] Aprobación de cambios en PR

### 2. Testing Local
- [ ] Backend: `python -m pytest` (si hay tests)
- [ ] Frontend: `npm run build` exitoso
- [ ] No hay warnings de TypeScript
- [ ] No hay errores de sintaxis Python

### 3. Validación de Funcionalidades
- [ ] ✅ Botón "Crear cuenta" navega correctamente
- [ ] ✅ Formulario registro completo visible
- [ ] ✅ Selector de ROL funciona
- [ ] ✅ Selector de tipo vehículo funciona
- [ ] ✅ Campo placa aparece condicionalmente
- [ ] ✅ Validaciones frontend funcionan
- [ ] ✅ Backend crea usuario + vehículo
- [ ] ✅ QR selector de tipo funciona
- [ ] ✅ Backend asigna espacio del tipo

### 4. Base de Datos
- [ ] Verificar que tablas existen
  ```sql
  \dt usuarios
  \dt vehiculos
  \dt espacios_parqueo
  \dt accesos
  ```
- [ ] Verificar columnas necesarias
  ```sql
  SELECT column_name, data_type 
  FROM information_schema.columns 
  WHERE table_name = 'usuarios';
  ```
- [ ] No se requieren nuevas migraciones (campos ya existen)

---

## 🚀 Deployment

### Opción A: Railway (Recomendado)

#### Backend
```bash
# 1. Asegurarse de estar en develop
git checkout develop
git pull origin develop

# 2. Verificar variables de entorno en Railway:
# - DATABASE_URL
# - SECRET_KEY
# - ALGORITHM

# 3. Push automático (Railway detecta cambios)
git push origin develop

# 4. Verificar logs en Railway dashboard
```

#### Frontend
```bash
# 1. Build local para verificar
cd frontend
npm run build

# 2. Verificar variables de entorno
# - NEXT_PUBLIC_API_BASE_URL

# 3. Push y deploy automático
git push origin develop

# 4. Verificar en Railway dashboard
```

### Opción B: Docker Local → Manual Deploy

```bash
# 1. Build imágenes
docker-compose build

# 2. Verificar que todo funciona
docker-compose up -d
docker-compose ps

# 3. Test manual completo
# (ver GUIA_TESTING.md)

# 4. Si todo OK, push a registry
docker tag smartparku-backend:latest registry/smartparku-backend:v2.0
docker push registry/smartparku-backend:v2.0

docker tag smartparku-frontend:latest registry/smartparku-frontend:v2.0
docker push registry/smartparku-frontend:v2.0

# 5. Deploy en servidor de producción
ssh user@production-server
docker pull registry/smartparku-backend:v2.0
docker pull registry/smartparku-frontend:v2.0
docker-compose up -d
```

---

## 🧪 Post-Deployment Testing

### 1. Smoke Tests (Inmediato)

**Backend Health Check:**
```bash
curl https://api.smartparku.com/health
# Esperado: {"status": "ok"}

curl https://api.smartparku.com/docs
# Esperado: Swagger UI carga correctamente
```

**Frontend:**
```bash
# Abrir navegador:
https://smartparku.com
# Verificar: página de login carga
```

### 2. Functional Tests (5-10 min)

**Test 1: Registro de Usuario**
1. [ ] Abrir https://smartparku.com
2. [ ] Clic en "Crear cuenta"
3. [ ] Completar formulario:
   - Nombre: Test User
   - Correo: test@ucc.edu.co
   - Contraseña: test123456
   - Rol: Estudiante
   - Tipo: Moto
   - Placa: TEST123
4. [ ] Submit y verificar cuenta creada
5. [ ] Login exitoso

**Test 2: Generación de QR**
1. [ ] Login con test@ucc.edu.co
2. [ ] Navegar a sección QR
3. [ ] Seleccionar tipo: Motocicleta
4. [ ] Generar QR
5. [ ] Verificar: QR se muestra con contador

**Test 3: Validaciones**
1. [ ] Intentar registro con correo duplicado → Error
2. [ ] Intentar generar QR sin tipo → Botón desactivado
3. [ ] Registrar con tipo sin placa → Error frontend

### 3. Database Verification

```sql
-- Conectar a BD de producción
psql $DATABASE_URL

-- Verificar usuario test creado
SELECT * FROM usuarios WHERE correo = 'test@ucc.edu.co';

-- Verificar vehículo asociado
SELECT v.* FROM vehiculos v
JOIN usuarios u ON v.id_usuario = u.id_usuario
WHERE u.correo = 'test@ucc.edu.co';

-- Verificar no hay datos inconsistentes
SELECT COUNT(*) FROM vehiculos WHERE id_usuario IS NULL;
-- Esperado: 0
```

---

## 🔍 Monitoring (Primeras 24h)

### Métricas a Monitorear

**Backend:**
- [ ] Response times < 500ms promedio
- [ ] Error rate < 1%
- [ ] CPU usage < 80%
- [ ] Memory usage < 80%

**Frontend:**
- [ ] Page load time < 2s
- [ ] No errores 404
- [ ] Assets cargan correctamente
- [ ] Animaciones fluidas

**Database:**
- [ ] Query time < 100ms promedio
- [ ] Connections < max_connections
- [ ] Disk usage monitoreado

### Logs a Revisar

```bash
# Backend logs (Railway)
# Ver en dashboard Railway → Logs tab

# Buscar errores
# grep "ERROR" logs
# grep "500" logs

# Frontend logs
# Browser console
# Network tab

# Database logs
# Ver en Railway dashboard
```

---

## 🚨 Rollback Plan

### Si algo falla crítico:

#### Opción 1: Git Revert (Rápido)
```bash
# 1. Identificar commit problemático
git log --oneline

# 2. Revert
git revert <commit-hash>
git push origin develop

# 3. Railway/Vercel/etc auto-redeploy
```

#### Opción 2: Rollback Manual
```bash
# 1. Checkout versión anterior
git checkout <previous-commit-hash>

# 2. Force push (CUIDADO)
git push --force origin develop

# Railway redeploys automáticamente
```

#### Opción 3: Feature Flag (Recomendado)
```python
# Backend: agregar feature flag
ENABLE_NEW_REGISTER = os.getenv("ENABLE_NEW_REGISTER", "false") == "true"

if ENABLE_NEW_REGISTER:
    # nuevo código
else:
    # código antiguo
```

```tsx
// Frontend
const ENABLE_NEW_REGISTER = process.env.NEXT_PUBLIC_ENABLE_NEW_REGISTER === 'true';

if (ENABLE_NEW_REGISTER) {
  // nuevo formulario
} else {
  // formulario antiguo
}
```

---

## 📊 Success Criteria

### Deployment es exitoso si:

**Funcionalidad:**
- ✅ Todas las features nuevas funcionan
- ✅ Features existentes no rotas
- ✅ No errores 500 en backend
- ✅ No errores en consola frontend

**Performance:**
- ✅ Response times aceptables
- ✅ No degradación de performance
- ✅ Recursos dentro de límites

**User Experience:**
- ✅ Flujo intuitivo
- ✅ Sin confusión en UI
- ✅ Validaciones claras
- ✅ Mensajes de error útiles

**Estabilidad:**
- ✅ Sin crashes en 24h
- ✅ Sin memory leaks
- ✅ BD consistente

---

## 📞 Contactos de Emergencia

**Líder Técnico:** [Nombre]  
**DevOps:** [Nombre]  
**DBA:** [Nombre]  

**Escalación:**
1. Desarrollador (Kiro AI)
2. Líder Técnico
3. CTO / Director de Tecnología

---

## 📝 Notas Finales

### Backup Antes de Deploy
```bash
# Backup de BD
pg_dump $DATABASE_URL > backup_pre_deploy_$(date +%Y%m%d).sql

# Backup de código (tag)
git tag v2.0-pre-deploy
git push origin v2.0-pre-deploy
```

### Variables de Entorno Nuevas
No hay variables nuevas, pero verificar que existan:

**Backend:**
```env
DATABASE_URL=postgresql://...
SECRET_KEY=...
ALGORITHM=HS256
```

**Frontend:**
```env
NEXT_PUBLIC_API_BASE_URL=https://api.smartparku.com
```

### Post-Deploy Communication

**Email al equipo:**
```
Asunto: ✅ Deploy SmartParkU v2.0 - Mejoras Registro y QR

Equipo,

Se ha desplegado exitosamente la versión 2.0 de SmartParkU con las siguientes mejoras:

1. Selector de tipo de vehículo en generación de QR
2. Formulario de registro completo con rol y vehículo
3. Validaciones mejoradas en frontend y backend

Testing: Ver GUIA_TESTING.md
Documentación: Ver IMPLEMENTACION_MEJORAS_REGISTRO_QR.md

Por favor reportar cualquier issue.

Saludos,
Kiro AI
```

---

## ✅ Final Checklist

Antes de cerrar el deployment:

- [ ] Código en producción
- [ ] Smoke tests pasados
- [ ] Functional tests pasados
- [ ] Database verificada
- [ ] Monitoring activo
- [ ] Logs revisados (sin errores críticos)
- [ ] Backup tomado
- [ ] Equipo notificado
- [ ] Documentación actualizada
- [ ] Rollback plan listo (por si acaso)

**Deployment completado:** _________ (Fecha/Hora)  
**Aprobado por:** _________  
**Próxima revisión:** 24h después del deploy

---

## 🎉 Success!

Si llegaste aquí y todo está ✅, ¡felicidades! El deployment fue exitoso.

**Próximos pasos:**
1. Monitorear por 24-48 horas
2. Recolectar feedback de usuarios
3. Planificar siguiente iteración

**¡Buen trabajo equipo! 🚀**
