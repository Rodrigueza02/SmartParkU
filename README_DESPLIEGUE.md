# 🚀 SmartParkU - Guía de Despliegue en Producción

## 🎯 Decisión Rápida

¿Tienes 20 minutos y quieres tu app en la nube?

```powershell
# 1. Asegúrate de tener Azure CLI instalado
az login

# 2. Ejecuta el script desde la raíz del proyecto
.\deploy-azure.ps1

# ¡Eso es todo! ✅
```

---

## 📚 Documentación Disponible

| Documento | Descripción | Cuando Usarlo |
|-----------|-------------|---------------|
| **`DESPLIEGUE_QUICKSTART.md`** | Inicio rápido con script automatizado | ⭐ Empieza aquí |
| **`COMPARACION_PROVEEDORES_CLOUD.md`** | Comparativa Azure vs AWS detallada | Decidir proveedor |
| **`GUIA_DESPLIEGUE_AZURE.md`** | Guía paso a paso completa para Azure | Setup manual Azure |
| **`GUIA_DESPLIEGUE_AWS.md`** | Guía paso a paso completa para AWS | Setup manual AWS |
| **`deploy-azure.ps1`** | Script automatizado de despliegue | Despliegue en 1 click |

---

## ⚡ Quick Start - 3 Opciones

### Opción 1: Script Automatizado (Más Rápido) ⭐

```powershell
# Prerequisitos:
# - Cuenta Azure (gratis con $200 crédito)
# - Azure CLI instalado
# - Docker Desktop corriendo

# Ejecutar:
.\deploy-azure.ps1

# Tiempo: 15-20 minutos
# Resultado: App completamente desplegada con HTTPS
```

### Opción 2: Azure Manual (Control Total)

```powershell
# Seguir la guía paso a paso
# Ver: GUIA_DESPLIEGUE_AZURE.md

# Tiempo: 30-45 minutos
# Ventaja: Entiendes cada paso
```

### Opción 3: AWS Manual (Avanzado)

```powershell
# Para equipos con experiencia en AWS
# Ver: GUIA_DESPLIEGUE_AWS.md

# Tiempo: 60-90 minutos
# Ventaja: Integración con ecosistema AWS
```

---

## 💰 Comparación de Costos

| Proveedor | Costo Mensual | Free Tier | Complejidad |
|-----------|---------------|-----------|-------------|
| **Azure** | **$55-80** | $200 crédito | ⭐⭐ Fácil |
| AWS | $82-118 | 12 meses limitado | ⭐⭐⭐⭐ Complejo |

**Recomendación:** Azure es 40% más barato y 3x más rápido de configurar.

---

## 🏗️ Arquitectura Desplegada

```
                     INTERNET
                        │
                        ▼
              ┌─────────────────┐
              │   Azure CDN     │ (SSL/HTTPS automático)
              │   (Opcional)    │
              └─────────────────┘
                        │
        ┌───────────────┴───────────────┐
        │                               │
        ▼                               ▼
┌───────────────┐              ┌───────────────┐
│   Frontend    │              │   Backend     │
│   Container   │─────────────▶│   Container   │
│   (Next.js)   │   API Calls  │   (FastAPI)   │
└───────────────┘              └───────────────┘
    Port 3000                       Port 8000
                                        │
                                        ▼
                              ┌─────────────────┐
                              │   PostgreSQL    │
                              │   Flexible      │
                              │   Server        │
                              └─────────────────┘
                                        │
                                        ▼
                              ┌─────────────────┐
                              │   HiveMQ Cloud  │
                              │   (MQTT Broker) │
                              └─────────────────┘
```

---

## 📋 Prerequisitos

### Software Requerido

1. **Azure CLI**
   ```powershell
   # Descargar: https://aka.ms/installazurecliwindows
   az --version
   ```

2. **Docker Desktop**
   ```powershell
   # Ya instalado ✅
   docker --version
   ```

3. **Cuenta Azure**
   - Crear en: https://azure.microsoft.com/free/
   - Incluye $200 de crédito gratis

### Verificar Todo Está Listo

```powershell
# Test 1: Azure CLI instalado
az --version

# Test 2: Logueado en Azure
az account show

# Test 3: Docker corriendo
docker ps

# Si todo funciona, estás listo! ✅
```

---

## 🚀 Proceso de Despliegue Automatizado

El script `deploy-azure.ps1` realiza estos pasos:

```
1. ✅ Verificar prerequisitos
2. ✅ Crear grupo de recursos
3. ✅ Crear Container Registry
4. ✅ Construir y subir imágenes Docker
5. ✅ Crear base de datos PostgreSQL
6. ✅ Crear Container Apps Environment
7. ✅ Desplegar backend
8. ✅ Ejecutar migraciones de BD
9. ✅ Desplegar frontend
10. ✅ Configurar HTTPS automático
```

**Total: ~15-20 minutos** ⏱️

---

## 📊 URLs Después del Despliegue

Después de ejecutar el script, obtendrás:

```
Frontend:  https://smartparku-frontend-xxx.azurecontainerapps.io
Backend:   https://smartparku-backend-xxx.azurecontainerapps.io
API Docs:  https://smartparku-backend-xxx.azurecontainerapps.io/docs
DB:        smartparku-db.postgres.database.azure.com
```

### Usuarios de Prueba

| Usuario | Email | Contraseña | Rol |
|---------|-------|-----------|-----|
| Admin | `admin@ucc.edu.co` | `admin123` | SuperAdmin |
| Estudiante | `estudiante@ucc.edu.co` | `estudiante123` | Estudiante |
| Administrativo | `admin.campus@ucc.edu.co` | `admin123` | Administrativo |

---

## 🔧 Personalizar el Despliegue

### Cambiar Región

```powershell
.\deploy-azure.ps1 -Location "brazilsouth"  # Más cerca de Sudamérica
```

### Cambiar Nombres

```powershell
.\deploy-azure.ps1 `
  -ResourceGroup "mi-grupo" `
  -AppName "mi-app" `
  -AcrName "miregistro"
```

### Cambiar Credenciales de BD

```powershell
.\deploy-azure.ps1 `
  -DbAdminUser "admin" `
  -DbAdminPassword "TuPasswordSegura123!"
```

---

## 📈 Monitoreo Post-Despliegue

### Ver Logs en Tiempo Real

```powershell
# Backend logs
az containerapp logs show `
  --name smartparku-backend `
  --resource-group smartparku-rg `
  --follow

# Frontend logs
az containerapp logs show `
  --name smartparku-frontend `
  --resource-group smartparku-rg `
  --follow
```

### Ver Estado de Servicios

```powershell
# Listar todas las apps
az containerapp list `
  --resource-group smartparku-rg `
  --output table

# Estado de la base de datos
az postgres flexible-server show `
  --name smartparku-db `
  --resource-group smartparku-rg
```

### Portal de Azure

```powershell
# Abrir portal web
start https://portal.azure.com
```

---

## 🔄 Actualizar la Aplicación

Cuando hagas cambios en el código:

### Opción 1: Script de Update (Crear uno)

```powershell
# update-azure.ps1
$ACR_NAME = "smartparkuacr"
$RESOURCE_GROUP = "smartparku-rg"

# Login
az acr login --name $ACR_NAME

# Rebuild y push backend
docker build -t $ACR_NAME.azurecr.io/smartparku-backend:latest ./backend
docker push $ACR_NAME.azurecr.io/smartparku-backend:latest

# Rebuild y push frontend
docker build -t $ACR_NAME.azurecr.io/smartparku-frontend:latest ./frontend
docker push $ACR_NAME.azurecr.io/smartparku-frontend:latest

# Update apps (Azure detecta automáticamente)
Write-Host "✅ Imágenes actualizadas. Azure desplegará automáticamente." -ForegroundColor Green
```

### Opción 2: Manual

```powershell
# 1. Rebuild imagen
docker build -t smartparkuacr.azurecr.io/smartparku-backend:latest ./backend

# 2. Push a registry
az acr login --name smartparkuacr
docker push smartparkuacr.azurecr.io/smartparku-backend:latest

# 3. Update container app
az containerapp update `
  --name smartparku-backend `
  --resource-group smartparku-rg `
  --image smartparkuacr.azurecr.io/smartparku-backend:latest
```

---

## 🛡️ Seguridad en Producción

### 1. Cambiar Secret Key

```powershell
$NEW_SECRET = -join ((65..90) + (97..122) | Get-Random -Count 32 | % {[char]$_})

az containerapp update `
  --name smartparku-backend `
  --resource-group smartparku-rg `
  --set-env-vars SECRET_KEY=$NEW_SECRET
```

### 2. Configurar Firewall de BD

```powershell
# Permitir solo Container Apps
az postgres flexible-server firewall-rule create `
  --resource-group smartparku-rg `
  --name smartparku-db `
  --rule-name AllowContainerApps `
  --start-ip-address 0.0.0.0 `
  --end-ip-address 0.0.0.0
```

### 3. Habilitar Solo HTTPS

```powershell
az containerapp ingress update `
  --name smartparku-backend `
  --resource-group smartparku-rg `
  --allow-insecure false
```

---

## 🗑️ Eliminar Todo (Cleanup)

Si necesitas eliminar toda la infraestructura:

```powershell
# ⚠️ ADVERTENCIA: Esto eliminará TODOS los recursos y datos

# Ver qué se eliminará
az group show --name smartparku-rg

# Confirmar y eliminar
az group delete --name smartparku-rg --yes --no-wait

# Verificar eliminación
az group list --output table
```

---

## 🆘 Troubleshooting

### Problema: "Azure CLI not found"

```powershell
# Solución: Instalar Azure CLI
# Descargar de: https://aka.ms/installazurecliwindows
# Luego reiniciar PowerShell
```

### Problema: "Not logged in"

```powershell
# Solución: Login en Azure
az login
```

### Problema: "Docker daemon not running"

```powershell
# Solución:
# 1. Abrir Docker Desktop
# 2. Esperar a que inicie
# 3. Verificar: docker ps
```

### Problema: "Container not starting"

```powershell
# Ver logs detallados
az containerapp logs show `
  --name smartparku-backend `
  --resource-group smartparku-rg `
  --tail 100

# Ver eventos del contenedor
az containerapp revision list `
  --name smartparku-backend `
  --resource-group smartparku-rg `
  --output table
```

### Problema: "Database connection error"

```powershell
# Verificar reglas de firewall
az postgres flexible-server firewall-rule list `
  --resource-group smartparku-rg `
  --name smartparku-db `
  --output table

# Agregar regla si es necesario
az postgres flexible-server firewall-rule create `
  --resource-group smartparku-rg `
  --name smartparku-db `
  --rule-name AllowAll `
  --start-ip-address 0.0.0.0 `
  --end-ip-address 255.255.255.255
```

---

## 📚 Recursos Adicionales

### Documentación Oficial

- [Azure Container Apps](https://docs.microsoft.com/azure/container-apps/)
- [Azure PostgreSQL](https://docs.microsoft.com/azure/postgresql/)
- [Azure CLI Reference](https://docs.microsoft.com/cli/azure/)

### Calculadoras de Precio

- [Azure Pricing Calculator](https://azure.microsoft.com/pricing/calculator/)
- [AWS Pricing Calculator](https://calculator.aws/)

### Tutoriales

- [Container Apps Tutorial](https://docs.microsoft.com/azure/container-apps/quickstart-portal)
- [PostgreSQL Tutorial](https://docs.microsoft.com/azure/postgresql/flexible-server/quickstart-create-server-portal)

---

## ✅ Checklist Final

Antes de desplegar, verifica:

- [ ] Cuenta de Azure creada
- [ ] Azure CLI instalado (`az --version`)
- [ ] Logueado en Azure (`az account show`)
- [ ] Docker Desktop corriendo (`docker ps`)
- [ ] En directorio del proyecto (`pwd` debe mostrar SmartParkU)
- [ ] Revisaste costos estimados ($55-80/mes)
- [ ] Tienes 20 minutos libres
- [ ] Listo para ejecutar: `.\deploy-azure.ps1`

---

## 🎉 ¡Listo para Producción!

Una vez desplegado:

1. ✅ Abre el frontend en tu navegador
2. ✅ Inicia sesión con credenciales de prueba
3. ✅ Verifica que todo funciona
4. ✅ Configura dominio personalizado (opcional)
5. ✅ Configura monitoreo y alertas
6. ✅ ¡Disfruta tu app en la nube!

---

**¿Listo? Ejecuta el script y tendrás SmartParkU en producción en 20 minutos! 🚀**

```powershell
.\deploy-azure.ps1
```
