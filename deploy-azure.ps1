# ═══════════════════════════════════════════════════════════════════════════
# 🚀 Script de Despliegue Automatizado - SmartParkU en Azure
# ═══════════════════════════════════════════════════════════════════════════

param(
    [string]$ResourceGroup = "smartparku-rg",
    [string]$Location = "eastus",
    [string]$AppName = "smartparku",
    [string]$AcrName = "smartparkuacr",
    [string]$DbServerName = "smartparku-db",
    [string]$DbAdminUser = "pgadmin",
    [string]$DbAdminPassword = "SmartParkU2026!Secure",  # CÁMBIALA EN PRODUCCIÓN
    [string]$SecretKey = "produccion-secret-key-$(Get-Random)-2026"  # Auto-generada
)

Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🚀 SmartParkU - Despliegue en Azure Container Apps" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# ─────────────────────────────────────────────────────────────────────────────
# PASO 0: Verificar prerequisitos
# ─────────────────────────────────────────────────────────────────────────────

Write-Host "⚙️  Verificando prerequisitos..." -ForegroundColor Yellow

# Verificar Azure CLI
try {
    $azVersion = az version --output json | ConvertFrom-Json
    Write-Host "✅ Azure CLI instalado: $($azVersion.'azure-cli')" -ForegroundColor Green
} catch {
    Write-Host "❌ Azure CLI no está instalado. Descárgalo de: https://aka.ms/installazurecliwindows" -ForegroundColor Red
    exit 1
}

# Verificar login en Azure
$account = az account show 2>$null
if (-not $account) {
    Write-Host "⚠️  No estás logueado en Azure. Iniciando login..." -ForegroundColor Yellow
    az login
}

$accountInfo = az account show | ConvertFrom-Json
Write-Host "✅ Logueado como: $($accountInfo.user.name)" -ForegroundColor Green
Write-Host "   Suscripción: $($accountInfo.name)" -ForegroundColor Gray
Write-Host ""

# Verificar Docker
try {
    docker --version | Out-Null
    Write-Host "✅ Docker instalado" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker no está instalado o no está corriendo" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ─────────────────────────────────────────────────────────────────────────────
# PASO 1: Crear Grupo de Recursos
# ─────────────────────────────────────────────────────────────────────────────

Write-Host "📦 PASO 1/9: Creando grupo de recursos..." -ForegroundColor Cyan

$rgExists = az group exists --name $ResourceGroup
if ($rgExists -eq "true") {
    Write-Host "⚠️  Grupo de recursos '$ResourceGroup' ya existe. Usando el existente." -ForegroundColor Yellow
} else {
    az group create --name $ResourceGroup --location $Location --output none
    Write-Host "✅ Grupo de recursos creado: $ResourceGroup" -ForegroundColor Green
}

Write-Host ""

# ─────────────────────────────────────────────────────────────────────────────
# PASO 2: Crear Azure Container Registry
# ─────────────────────────────────────────────────────────────────────────────

Write-Host "📦 PASO 2/9: Creando Container Registry..." -ForegroundColor Cyan

$acrExists = az acr show --name $AcrName --resource-group $ResourceGroup 2>$null
if ($acrExists) {
    Write-Host "⚠️  Container Registry '$AcrName' ya existe. Usando el existente." -ForegroundColor Yellow
} else {
    az acr create `
        --resource-group $ResourceGroup `
        --name $AcrName `
        --sku Basic `
        --admin-enabled true `
        --output none
    Write-Host "✅ Container Registry creado: $AcrName" -ForegroundColor Green
}

# Obtener credenciales
$acrCreds = az acr credential show --name $AcrName --resource-group $ResourceGroup | ConvertFrom-Json
$acrUsername = $acrCreds.username
$acrPassword = $acrCreds.passwords[0].value
$acrLoginServer = "$AcrName.azurecr.io"

Write-Host "   Login Server: $acrLoginServer" -ForegroundColor Gray
Write-Host ""

# ─────────────────────────────────────────────────────────────────────────────
# PASO 3: Construir y Subir Imágenes Docker
# ─────────────────────────────────────────────────────────────────────────────

Write-Host "🐳 PASO 3/9: Construyendo y subiendo imágenes Docker..." -ForegroundColor Cyan

# Login en ACR
az acr login --name $AcrName --output none

Write-Host "   Construyendo Backend..." -ForegroundColor Gray
docker build -t "$acrLoginServer/smartparku-backend:latest" ./backend --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error construyendo imagen del backend" -ForegroundColor Red
    exit 1
}

Write-Host "   Subiendo Backend a ACR..." -ForegroundColor Gray
docker push "$acrLoginServer/smartparku-backend:latest" --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error subiendo imagen del backend" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Backend subido" -ForegroundColor Green

Write-Host "   Construyendo Frontend..." -ForegroundColor Gray
docker build -t "$acrLoginServer/smartparku-frontend:latest" ./frontend --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error construyendo imagen del frontend" -ForegroundColor Red
    exit 1
}

Write-Host "   Subiendo Frontend a ACR..." -ForegroundColor Gray
docker push "$acrLoginServer/smartparku-frontend:latest" --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error subiendo imagen del frontend" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Frontend subido" -ForegroundColor Green
Write-Host ""

# ─────────────────────────────────────────────────────────────────────────────
# PASO 4: Crear Base de Datos PostgreSQL
# ─────────────────────────────────────────────────────────────────────────────

Write-Host "🗄️  PASO 4/9: Creando base de datos PostgreSQL..." -ForegroundColor Cyan

$dbExists = az postgres flexible-server show --name $DbServerName --resource-group $ResourceGroup 2>$null
if ($dbExists) {
    Write-Host "⚠️  Servidor de base de datos '$DbServerName' ya existe. Usando el existente." -ForegroundColor Yellow
} else {
    Write-Host "   ⏳ Esto puede tomar 5-10 minutos..." -ForegroundColor Gray
    az postgres flexible-server create `
        --resource-group $ResourceGroup `
        --name $DbServerName `
        --location $Location `
        --admin-user $DbAdminUser `
        --admin-password $DbAdminPassword `
        --sku-name Standard_B1ms `
        --tier Burstable `
        --storage-size 32 `
        --version 15 `
        --public-access 0.0.0.0-255.255.255.255 `
        --yes `
        --output none
    
    Write-Host "✅ Servidor PostgreSQL creado" -ForegroundColor Green
    
    # Crear base de datos
    az postgres flexible-server db create `
        --resource-group $ResourceGroup `
        --server-name $DbServerName `
        --database-name smartparku `
        --output none
    
    Write-Host "✅ Base de datos 'smartparku' creada" -ForegroundColor Green
}

$dbHost = "$DbServerName.postgres.database.azure.com"
$databaseUrl = "postgresql+psycopg://${DbAdminUser}:${DbAdminPassword}@${dbHost}:5432/smartparku"

Write-Host "   Host: $dbHost" -ForegroundColor Gray
Write-Host ""

# ─────────────────────────────────────────────────────────────────────────────
# PASO 5: Crear Container Apps Environment
# ─────────────────────────────────────────────────────────────────────────────

Write-Host "🌐 PASO 5/9: Creando Container Apps Environment..." -ForegroundColor Cyan

$envName = "$AppName-env"
$envExists = az containerapp env show --name $envName --resource-group $ResourceGroup 2>$null
if ($envExists) {
    Write-Host "⚠️  Environment '$envName' ya existe. Usando el existente." -ForegroundColor Yellow
} else {
    az containerapp env create `
        --name $envName `
        --resource-group $ResourceGroup `
        --location $Location `
        --output none
    Write-Host "✅ Container Apps Environment creado" -ForegroundColor Green
}

Write-Host ""

# ─────────────────────────────────────────────────────────────────────────────
# PASO 6: Desplegar Backend
# ─────────────────────────────────────────────────────────────────────────────

Write-Host "🚀 PASO 6/9: Desplegando Backend..." -ForegroundColor Cyan

$backendAppName = "$AppName-backend"

# Variables de entorno para el backend
$envVars = @"
DATABASE_URL=$databaseUrl
SECRET_KEY=$SecretKey
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
MQTT_BROKER=7de2fa1d05f84c5c8f2fcacca06d98da.s1.eu.hivemq.cloud
MQTT_PORT=8883
MQTT_USERNAME=Juliana
MQTT_PASSWORD=1138524566Juli*
"@

# Crear archivo temporal con variables
$envVars | Out-File -FilePath "backend-env.txt" -Encoding utf8

$backendExists = az containerapp show --name $backendAppName --resource-group $ResourceGroup 2>$null
if ($backendExists) {
    Write-Host "   Actualizando backend existente..." -ForegroundColor Gray
    az containerapp update `
        --name $backendAppName `
        --resource-group $ResourceGroup `
        --image "$acrLoginServer/smartparku-backend:latest" `
        --output none
} else {
    Write-Host "   Creando nueva app backend..." -ForegroundColor Gray
    az containerapp create `
        --name $backendAppName `
        --resource-group $ResourceGroup `
        --environment $envName `
        --image "$acrLoginServer/smartparku-backend:latest" `
        --target-port 8000 `
        --ingress external `
        --registry-server $acrLoginServer `
        --registry-username $acrUsername `
        --registry-password $acrPassword `
        --cpu 0.5 `
        --memory 1Gi `
        --min-replicas 1 `
        --max-replicas 3 `
        --env-vars "DATABASE_URL=$databaseUrl" "SECRET_KEY=$SecretKey" "ALGORITHM=HS256" "ACCESS_TOKEN_EXPIRE_MINUTES=60" "MQTT_BROKER=7de2fa1d05f84c5c8f2fcacca06d98da.s1.eu.hivemq.cloud" "MQTT_PORT=8883" "MQTT_USERNAME=Juliana" "MQTT_PASSWORD=1138524566Juli*" `
        --output none
}

# Limpiar archivo temporal
Remove-Item "backend-env.txt" -ErrorAction SilentlyContinue

$backendUrl = az containerapp show `
    --name $backendAppName `
    --resource-group $ResourceGroup `
    --query "properties.configuration.ingress.fqdn" `
    --output tsv

Write-Host "✅ Backend desplegado" -ForegroundColor Green
Write-Host "   URL: https://$backendUrl" -ForegroundColor Green
Write-Host ""

# ─────────────────────────────────────────────────────────────────────────────
# PASO 7: Ejecutar Migraciones
# ─────────────────────────────────────────────────────────────────────────────

Write-Host "🔧 PASO 7/9: Ejecutando migraciones de base de datos..." -ForegroundColor Cyan

Write-Host "   Ejecutando: alembic upgrade head" -ForegroundColor Gray
az containerapp exec `
    --name $backendAppName `
    --resource-group $ResourceGroup `
    --command "alembic upgrade head" `
    --output none 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Migraciones ejecutadas" -ForegroundColor Green
} else {
    Write-Host "⚠️  Error ejecutando migraciones (puede que ya estén aplicadas)" -ForegroundColor Yellow
}

Write-Host "   Cargando datos iniciales..." -ForegroundColor Gray
az containerapp exec `
    --name $backendAppName `
    --resource-group $ResourceGroup `
    --command "python app/initial_data.py" `
    --output none 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Datos iniciales cargados" -ForegroundColor Green
} else {
    Write-Host "⚠️  Error cargando datos iniciales (puede que ya existan)" -ForegroundColor Yellow
}

Write-Host ""

# ─────────────────────────────────────────────────────────────────────────────
# PASO 8: Desplegar Frontend
# ─────────────────────────────────────────────────────────────────────────────

Write-Host "🎨 PASO 8/9: Desplegando Frontend..." -ForegroundColor Cyan

$frontendAppName = "$AppName-frontend"

$frontendExists = az containerapp show --name $frontendAppName --resource-group $ResourceGroup 2>$null
if ($frontendExists) {
    Write-Host "   Actualizando frontend existente..." -ForegroundColor Gray
    az containerapp update `
        --name $frontendAppName `
        --resource-group $ResourceGroup `
        --image "$acrLoginServer/smartparku-frontend:latest" `
        --set-env-vars "NEXT_PUBLIC_API_URL=https://$backendUrl" "NEXT_PUBLIC_WS_URL=wss://$backendUrl/api/v1/parking/ws/parking" `
        --output none
} else {
    Write-Host "   Creando nueva app frontend..." -ForegroundColor Gray
    az containerapp create `
        --name $frontendAppName `
        --resource-group $ResourceGroup `
        --environment $envName `
        --image "$acrLoginServer/smartparku-frontend:latest" `
        --target-port 3000 `
        --ingress external `
        --registry-server $acrLoginServer `
        --registry-username $acrUsername `
        --registry-password $acrPassword `
        --cpu 0.5 `
        --memory 1Gi `
        --min-replicas 1 `
        --max-replicas 3 `
        --env-vars "NEXT_PUBLIC_API_URL=https://$backendUrl" "NEXT_PUBLIC_WS_URL=wss://$backendUrl/api/v1/parking/ws/parking" `
        --output none
}

$frontendUrl = az containerapp show `
    --name $frontendAppName `
    --resource-group $ResourceGroup `
    --query "properties.configuration.ingress.fqdn" `
    --output tsv

Write-Host "✅ Frontend desplegado" -ForegroundColor Green
Write-Host "   URL: https://$frontendUrl" -ForegroundColor Green
Write-Host ""

# ─────────────────────────────────────────────────────────────────────────────
# PASO 9: Resumen Final
# ─────────────────────────────────────────────────────────────────────────────

Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🎉 ¡DESPLIEGUE COMPLETADO!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 URLS DE ACCESO:" -ForegroundColor Yellow
Write-Host "   Frontend:      https://$frontendUrl" -ForegroundColor White
Write-Host "   Backend:       https://$backendUrl" -ForegroundColor White
Write-Host "   API Docs:      https://$backendUrl/docs" -ForegroundColor White
Write-Host "   Base de Datos: $dbHost" -ForegroundColor White
Write-Host ""
Write-Host "👤 USUARIOS DE PRUEBA:" -ForegroundColor Yellow
Write-Host "   Admin:         admin@ucc.edu.co / admin123" -ForegroundColor White
Write-Host "   Estudiante:    estudiante@ucc.edu.co / estudiante123" -ForegroundColor White
Write-Host ""
Write-Host "📊 MONITOREO:" -ForegroundColor Yellow
Write-Host "   Ver logs:      az containerapp logs show --name $backendAppName --resource-group $ResourceGroup --follow" -ForegroundColor White
Write-Host "   Portal Azure:  https://portal.azure.com/#@/resource/subscriptions/$($accountInfo.id)/resourceGroups/$ResourceGroup" -ForegroundColor White
Write-Host ""
Write-Host "💡 PRÓXIMOS PASOS:" -ForegroundColor Yellow
Write-Host "   1. Abre el frontend en tu navegador: https://$frontendUrl" -ForegroundColor White
Write-Host "   2. Inicia sesión con las credenciales de prueba" -ForegroundColor White
Write-Host "   3. Configura un dominio personalizado (opcional)" -ForegroundColor White
Write-Host "   4. Revisa los logs para verificar que todo funcione" -ForegroundColor White
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
