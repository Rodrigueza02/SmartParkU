# ⚡ Quick Start - Despliegue en la Nube

## 🎯 Recomendación: Azure Container Apps

**Azure es MÁS FÁCIL y MÁS BARATO para este proyecto.**

---

## 🚀 Opción 1: Script Automatizado (Recomendado)

### Prerequisitos
1. ✅ Cuenta de Azure (gratis con $200 de crédito)
2. ✅ Azure CLI instalado
3. ✅ Docker Desktop corriendo

### Desplegar en 1 Comando

```powershell
# Ejecutar desde la raíz del proyecto
.\deploy-azure.ps1
```

**Eso es todo!** El script hará:
- ✅ Crear infraestructura en Azure
- ✅ Subir imágenes Docker
- ✅ Crear base de datos PostgreSQL
- ✅ Desplegar backend y frontend
- ✅ Ejecutar migraciones
- ✅ Configurar HTTPS automáticamente

**Tiempo estimado:** 15-20 minutos

---

## 📝 Opción 2: Paso a Paso Manual

Si prefieres control total, sigue estas guías:

- **Azure**: Ver `GUIA_DESPLIEGUE_AZURE.md` (Recomendado - ~10 pasos)
- **AWS**: Ver `GUIA_DESPLIEGUE_AWS.md` (Avanzado - ~15 pasos)

---

## 💰 Comparación de Costos

| Proveedor | Costo Mensual | Complejidad | Free Tier |
|-----------|---------------|-------------|-----------|
| **Azure** | **$55-80** | ⭐⭐ Fácil | $200 crédito |
| AWS | $82-118 | ⭐⭐⭐⭐ Complejo | 12 meses limitado |

---

## ⏱️ Tiempo de Despliegue

| Método | Tiempo |
|--------|--------|
| **Script Azure automatizado** | **15-20 min** |
| Azure manual | 30-45 min |
| AWS manual | 60-90 min |

---

## 🆘 Solución de Problemas Rápida

### Error: Azure CLI no instalado
```powershell
# Descargar desde:
https://aka.ms/installazurecliwindows
```

### Error: No logueado en Azure
```powershell
az login
```

### Error: Docker no corriendo
- Abrir Docker Desktop
- Esperar a que inicie
- Verificar: `docker ps`

### Error en migraciones
```powershell
# Conectarse manualmente al contenedor
az containerapp exec `
  --name smartparku-backend `
  --resource-group smartparku-rg `
  --command "bash"

# Luego ejecutar:
alembic upgrade head
python app/initial_data.py
```

---

## 🎯 URLs Después del Despliegue

El script te mostrará las URLs finales:

```
Frontend:  https://smartparku-frontend.region.azurecontainerapps.io
Backend:   https://smartparku-backend.region.azurecontainerapps.io
API Docs:  https://smartparku-backend.region.azurecontainerapps.io/docs
```

**Usuarios de prueba:**
- Admin: `admin@ucc.edu.co` / `admin123`
- Estudiante: `estudiante@ucc.edu.co` / `estudiante123`

---

## 📊 Monitorear la Aplicación

```powershell
# Ver logs del backend en tiempo real
az containerapp logs show `
  --name smartparku-backend `
  --resource-group smartparku-rg `
  --follow

# Ver logs del frontend
az containerapp logs show `
  --name smartparku-frontend `
  --resource-group smartparku-rg `
  --follow

# Abrir portal de Azure
start https://portal.azure.com
```

---

## 🔄 Actualizar la Aplicación

Cuando hagas cambios en el código:

```powershell
# 1. Reconstruir y subir imagen
az acr login --name smartparkuacr
docker build -t smartparkuacr.azurecr.io/smartparku-backend:latest ./backend
docker push smartparkuacr.azurecr.io/smartparku-backend:latest

# 2. Actualizar container app (Azure lo hace automáticamente)
az containerapp update `
  --name smartparku-backend `
  --resource-group smartparku-rg `
  --image smartparkuacr.azurecr.io/smartparku-backend:latest
```

---

## 🗑️ Eliminar Todo

```powershell
# Eliminar grupo de recursos completo
az group delete --name smartparku-rg --yes --no-wait
```

⚠️ Esto eliminará TODA la infraestructura y datos.

---

## 📚 Documentación Completa

- **Guía Azure Completa**: `GUIA_DESPLIEGUE_AZURE.md`
- **Guía AWS Completa**: `GUIA_DESPLIEGUE_AWS.md`
- **Configuración Local**: `CONFIGURACION_INICIAL.md`

---

## ✅ Checklist Pre-Despliegue

- [ ] Cuenta de Azure creada
- [ ] Azure CLI instalado (`az --version`)
- [ ] Logueado en Azure (`az login`)
- [ ] Docker Desktop corriendo (`docker ps`)
- [ ] En el directorio del proyecto (`cd SmartParkU`)
- [ ] Listo para ejecutar: `.\deploy-azure.ps1`

---

**¿Listo? Ejecuta el script y tendrás tu app en producción en 20 minutos! 🚀**
