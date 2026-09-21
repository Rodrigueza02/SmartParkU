# 🚀 Guía Completa de Despliegue en Azure - SmartParkU

## 📋 Índice
1. [Prerequisitos](#prerequisitos)
2. [Opción Recomendada: Azure Container Apps](#opción-1-azure-container-apps-recomendado)
3. [Opción Alternativa: Azure App Service](#opción-2-azure-app-service-alternativa)
4. [Configuración de Base de Datos](#configuración-de-base-de-datos)
5. [Variables de Entorno](#variables-de-entorno)
6. [Verificación y Pruebas](#verificación-y-pruebas)
7. [Mantenimiento](#mantenimiento)

---

## 📦 Prerequisitos

### 1. Cuenta de Azure
- Crear cuenta gratuita: https://azure.microsoft.com/free/
- Incluye **$200 USD de crédito** por 30 días
- Después: free tier permanente disponible

### 2. Instalar Azure CLI
```powershell
# Descargar e instalar desde:
# https://aka.ms/installazurecliwindows

# Verificar instalación
az --version

# Iniciar sesión
az login
```

### 3. Instalar Docker (Ya lo tienes ✅)
```powershell
docker --version
```

---

## 🎯 Opción 1: Azure Container Apps (RECOMENDADO)

Esta es la opción **más fácil y moderna** para desplegar aplicaciones containerizadas.

### **Ventajas:**
- ✅ Deploy automático desde contenedores
- ✅ SSL/HTTPS gratis y automático
- ✅ Escalado automático
- ✅ Integración con GitHub/Docker Hub
- ✅ Ideal para microservicios

### **Costos Estimados:**
- Free tier: 180,000 vCPU-segundos y 360,000 GiB-segundos gratis/mes
- Después: ~$30-50 USD/mes para este proyecto

---

## 📝 Paso a Paso - Azure Container Apps

### **PASO 1: Crear Grupo de Recursos**

```powershell
# Definir variables
$RESOURCE_GROUP="smartparku-rg"
$LOCATION="eastus"  # Región cercana (puedes usar "brazilsouth" si estás en Sudamérica)
$APP_NAME="smartparku"

# Crear grupo de recursos
az group create --name $RESOURCE_GROUP --location $LOCATION
```

---

### **PASO 2: Crear Azure Container Registry (ACR)**

Necesitamos un lugar para almacenar nuestras imágenes Docker.

```powershell
$ACR_NAME="smartparkuacr"  # Debe ser único globalmente, solo minúsculas

# Crear registry
az acr create `
  --resource-group $RESOURCE_GROUP `
  --name $ACR_NAME `
  --sku Basic `
  --admin-enabled true

# Obtener credenciales
az acr credential show --name $ACR_NAME --resource-group $RESOURCE_GROUP
```

**⚠️ Guarda las credenciales (username y password) que aparecen**

---

### **PASO 3: Construir y Subir Imágenes Docker**

```powershell
# Ir a la raíz del proyecto
cd C:\Users\helen\Downloads\SmartParkU

# Login en ACR
az acr login --name $ACR_NAME

# Construir y subir Backend
docker build -t $ACR_NAME.azurecr.io/smartparku-backend:latest ./backend
docker push $ACR_NAME.azurecr.io/smartparku-backend:latest

# Construir y subir Frontend
docker build -t $ACR_NAME.azurecr.io/smartparku-frontend:latest ./frontend
docker push $ACR_NAME.azurecr.io/smartparku-frontend:latest
```

**Esto tomará varios minutos la primera vez** ⏱️

---

### **PASO 4: Crear Base de Datos PostgreSQL**

```powershell
$DB_SERVER_NAME="smartparku-db"  # Debe ser único
$DB_NAME="smartparku"
$DB_ADMIN_USER="pgadmin"
$DB_ADMIN_PASSWORD="SmartParkU2026!Secure"  # Cámbiala por una segura

# Crear servidor PostgreSQL Flexible
az postgres flexible-server create `
  --resource-group $RESOURCE_GROUP `
  --name $DB_SERVER_NAME `
  --location $LOCATION `
  --admin-user $DB_ADMIN_USER `
  --admin-password $DB_ADMIN_PASSWORD `
  --sku-name Standard_B1ms `
  --tier Burstable `
  --storage-size 32 `
  --version 15 `
  --public-access 0.0.0.0-255.255.255.255

# Crear base de datos
az postgres flexible-server db create `
  --resource-group $RESOURCE_GROUP `
  --server-name $DB_SERVER_NAME `
  --database-name $DB_NAME
```

**Conexión String:** (guárdala)
```
postgresql+psycopg://{DB_ADMIN_USER}:{DB_ADMIN_PASSWORD}@{DB_SERVER_NAME}.postgres.database.azure.com:5432/{DB_NAME}
```

---

### **PASO 5: Crear Container Apps Environment**

```powershell
$ENVIRONMENT_NAME="smartparku-env"

# Crear ambiente
az containerapp env create `
  --name $ENVIRONMENT_NAME `
  --resource-group $RESOURCE_GROUP `
  --location $LOCATION
```

---

### **PASO 6: Desplegar Backend**

```powershell
$BACKEND_APP="smartparku-backend"

# Obtener credenciales ACR
$ACR_USERNAME = az acr credential show --name $ACR_NAME --query username -o tsv
$ACR_PASSWORD = az acr credential show --name $ACR_NAME --query passwords[0].value -o tsv

# Crear app backend
az containerapp create `
  --name $BACKEND_APP `
  --resource-group $RESOURCE_GROUP `
  --environment $ENVIRONMENT_NAME `
  --image $ACR_NAME.azurecr.io/smartparku-backend:latest `
  --target-port 8000 `
  --ingress external `
  --registry-server $ACR_NAME.azurecr.io `
  --registry-username $ACR_USERNAME `
  --registry-password $ACR_PASSWORD `
  --cpu 0.5 `
  --memory 1Gi `
  --min-replicas 1 `
  --max-replicas 3 `
  --env-vars `
    DATABASE_URL="postgresql+psycopg://$DB_ADMIN_USER:$DB_ADMIN_PASSWORD@$DB_SERVER_NAME.postgres.database.azure.com:5432/$DB_NAME" `
    SECRET_KEY="produccion-secret-key-cambiar-por-una-segura-2026" `
    ALGORITHM="HS256" `
    ACCESS_TOKEN_EXPIRE_MINUTES="60" `
    MQTT_BROKER="7de2fa1d05f84c5c8f2fcacca06d98da.s1.eu.hivemq.cloud" `
    MQTT_PORT="8883" `
    MQTT_USERNAME="Juliana" `
    MQTT_PASSWORD="1138524566Juli*"

# Obtener URL del backend
$BACKEND_URL = az containerapp show `
  --name $BACKEND_APP `
  --resource-group $RESOURCE_GROUP `
  --query properties.configuration.ingress.fqdn -o tsv

Write-Host "Backend URL: https://$BACKEND_URL"
```

---

### **PASO 7: Ejecutar Migraciones de Base de Datos**

```powershell
# Ejecutar migraciones en el contenedor desplegado
az containerapp exec `
  --name $BACKEND_APP `
  --resource-group $RESOURCE_GROUP `
  --command "alembic upgrade head"

# Cargar datos iniciales
az containerapp exec `
  --name $BACKEND_APP `
  --resource-group $RESOURCE_GROUP `
  --command "python app/initial_data.py"
```

---

### **PASO 8: Desplegar Frontend**

```powershell
$FRONTEND_APP="smartparku-frontend"

# Crear app frontend
az containerapp create `
  --name $FRONTEND_APP `
  --resource-group $RESOURCE_GROUP `
  --environment $ENVIRONMENT_NAME `
  --image $ACR_NAME.azurecr.io/smartparku-frontend:latest `
  --target-port 3000 `
  --ingress external `
  --registry-server $ACR_NAME.azurecr.io `
  --registry-username $ACR_USERNAME `
  --registry-password $ACR_PASSWORD `
  --cpu 0.5 `
  --memory 1Gi `
  --min-replicas 1 `
  --max-replicas 3 `
  --env-vars `
    NEXT_PUBLIC_API_URL="https://$BACKEND_URL" `
    NEXT_PUBLIC_WS_URL="wss://$BACKEND_URL/api/v1/parking/ws/parking"

# Obtener URL del frontend
$FRONTEND_URL = az containerapp show `
  --name $FRONTEND_APP `
  --resource-group $RESOURCE_GROUP `
  --query properties.configuration.ingress.fqdn -o tsv

Write-Host "Frontend URL: https://$FRONTEND_URL"
```

---

### **PASO 9: Configurar CORS en el Backend**

Necesitamos permitir que el frontend acceda al backend. Vamos a actualizar el código:

---

## ✅ **URLs Finales**

Al terminar, tendrás:

```
Frontend:  https://{frontend-app}.{region}.azurecontainerapps.io
Backend:   https://{backend-app}.{region}.azurecontainerapps.io
API Docs:  https://{backend-app}.{region}.azurecontainerapps.io/docs
Database:  {db-server}.postgres.database.azure.com
```

---

## 🔄 Actualizar la Aplicación

Cuando hagas cambios en el código:

```powershell
# 1. Reconstruir imagen
docker build -t $ACR_NAME.azurecr.io/smartparku-backend:latest ./backend

# 2. Subir a ACR
docker push $ACR_NAME.azurecr.io/smartparku-backend:latest

# 3. Actualizar container app
az containerapp update `
  --name smartparku-backend `
  --resource-group $RESOURCE_GROUP `
  --image $ACR_NAME.azurecr.io/smartparku-backend:latest
```

---

## 📊 Monitoreo y Logs

```powershell
# Ver logs del backend
az containerapp logs show `
  --name smartparku-backend `
  --resource-group $RESOURCE_GROUP `
  --follow

# Ver logs del frontend
az containerapp logs show `
  --name smartparku-frontend `
  --resource-group $RESOURCE_GROUP `
  --follow

# Ver métricas
az monitor metrics list `
  --resource-group $RESOURCE_GROUP `
  --resource smartparku-backend `
  --resource-type Microsoft.App/containerApps `
  --metric CpuUsage
```

---

## 💰 Costos Estimados Mensuales

| Servicio | Configuración | Costo Aprox. |
|----------|---------------|--------------|
| Container Apps (Backend) | 0.5 vCPU, 1 GB RAM | $15-20 USD |
| Container Apps (Frontend) | 0.5 vCPU, 1 GB RAM | $15-20 USD |
| PostgreSQL Flexible | Standard_B1ms | $15-25 USD |
| Container Registry | Basic | $5 USD |
| Egress/Bandwidth | Normal usage | $5-10 USD |
| **TOTAL** | | **$55-80 USD/mes** |

**Free Tier disponible:** Primeros meses con créditos gratis ($200)

---

## 🛡️ Seguridad

### 1. Configurar Firewall de Base de Datos

```powershell
# Permitir solo Container Apps
az postgres flexible-server firewall-rule create `
  --resource-group $RESOURCE_GROUP `
  --name $DB_SERVER_NAME `
  --rule-name AllowAzureServices `
  --start-ip-address 0.0.0.0 `
  --end-ip-address 0.0.0.0
```

### 2. Rotar Secret Key

```powershell
# Generar nueva secret key
$NEW_SECRET = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})

# Actualizar backend
az containerapp update `
  --name smartparku-backend `
  --resource-group $RESOURCE_GROUP `
  --set-env-vars SECRET_KEY=$NEW_SECRET
```

### 3. Habilitar HTTPS Only

```powershell
az containerapp ingress update `
  --name smartparku-backend `
  --resource-group $RESOURCE_GROUP `
  --allow-insecure false
```

---

## 🔧 Troubleshooting

### Error: Container no inicia

```powershell
# Ver logs detallados
az containerapp logs show `
  --name smartparku-backend `
  --resource-group $RESOURCE_GROUP `
  --tail 100

# Revisar eventos
az containerapp revision list `
  --name smartparku-backend `
  --resource-group $RESOURCE_GROUP `
  --output table
```

### Error: No se conecta a la base de datos

```powershell
# Verificar reglas de firewall
az postgres flexible-server firewall-rule list `
  --resource-group $RESOURCE_GROUP `
  --name $DB_SERVER_NAME `
  --output table

# Probar conexión manualmente
az containerapp exec `
  --name smartparku-backend `
  --resource-group $RESOURCE_GROUP `
  --command "psql -h $DB_SERVER_NAME.postgres.database.azure.com -U $DB_ADMIN_USER -d $DB_NAME"
```

### Error: Frontend no se conecta al Backend

1. Verificar CORS en backend
2. Verificar variables de entorno del frontend
3. Comprobar que ambas apps estén en la misma red virtual

---

## 🗑️ Eliminar Todo (Cleanup)

Si necesitas eliminar todo el despliegue:

```powershell
# Eliminar grupo de recursos completo
az group delete --name $RESOURCE_GROUP --yes --no-wait
```

**⚠️ Esto eliminará TODOS los recursos** incluyendo base de datos y datos.

---

## 📚 Recursos Adicionales

- [Azure Container Apps Docs](https://docs.microsoft.com/azure/container-apps/)
- [Azure PostgreSQL Docs](https://docs.microsoft.com/azure/postgresql/)
- [Azure CLI Reference](https://docs.microsoft.com/cli/azure/)
- [Precios Azure](https://azure.microsoft.com/pricing/calculator/)

---

## ✅ Checklist de Despliegue

- [ ] Cuenta de Azure creada
- [ ] Azure CLI instalado y login exitoso
- [ ] Grupo de recursos creado
- [ ] Container Registry creado
- [ ] Imágenes Docker subidas
- [ ] Base de datos PostgreSQL creada
- [ ] Container Apps Environment creado
- [ ] Backend desplegado
- [ ] Migraciones ejecutadas
- [ ] Frontend desplegado
- [ ] CORS configurado
- [ ] URLs funcionando
- [ ] SSL/HTTPS habilitado
- [ ] Monitoreo configurado

---

**¡Tu aplicación SmartParkU estará en producción! 🎉**
