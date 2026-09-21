# Despliegue SmartParkU en Azure - Version Limpia
# Sin caracteres especiales

param(
    [string]$ResourceGroup = "smartparku-rg",
    [string]$Location = "eastus",
    [string]$AcrName = "smartparkuacr",
    [string]$DbServerName = "smartparku-db",
    [string]$DbAdminUser = "pgadmin",
    [string]$DbAdminPassword = "SmartParkU2026!Secure"
)

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "SmartParkU - Despliegue en Azure" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Azure CLI
$account = az account show 2>$null
if (-not $account) {
    Write-Host "ERROR: No estas logueado en Azure" -ForegroundColor Red
    Write-Host "Ejecuta: az login" -ForegroundColor Yellow
    exit 1
}

$accountInfo = az account show | ConvertFrom-Json
Write-Host "Logueado como: $($accountInfo.user.name)" -ForegroundColor Green
Write-Host ""

# PASO 1: Crear grupo de recursos
Write-Host "PASO 1/9: Creando grupo de recursos..." -ForegroundColor Cyan
$rgExists = az group exists --name $ResourceGroup
if ($rgExists -eq "true") {
    Write-Host "Grupo de recursos ya existe" -ForegroundColor Yellow
} else {
    az group create --name $ResourceGroup --location $Location --output none
    Write-Host "Grupo de recursos creado" -ForegroundColor Green
}
Write-Host ""

# PASO 2: Crear Container Registry
Write-Host "PASO 2/9: Creando Container Registry..." -ForegroundColor Cyan
$acrExists = az acr show --name $AcrName --resource-group $ResourceGroup 2>$null
if ($acrExists) {
    Write-Host "Container Registry ya existe" -ForegroundColor Yellow
} else {
    az acr create `
        --resource-group $ResourceGroup `
        --name $AcrName `
        --sku Basic `
        --admin-enabled true `
        --output none
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Container Registry creado" -ForegroundColor Green
    } else {
        Write-Host "ERROR creando Container Registry" -ForegroundColor Red
        exit 1
    }
}

# Obtener credenciales
$acrCreds = az acr credential show --name $AcrName --resource-group $ResourceGroup | ConvertFrom-Json
$acrUsername = $acrCreds.username
$acrPassword = $acrCreds.passwords[0].value
$acrLoginServer = "$AcrName.azurecr.io"

Write-Host "Login Server: $acrLoginServer" -ForegroundColor Gray
Write-Host ""

# PASO 3: Login en ACR y construir imagenes
Write-Host "PASO 3/9: Subiendo imagenes Docker..." -ForegroundColor Cyan
Write-Host "Esto puede tomar 10-15 minutos..." -ForegroundColor Gray

az acr login --name $AcrName --output none

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: No se pudo hacer login en ACR" -ForegroundColor Red
    exit 1
}

# Construir y subir Backend
Write-Host "Construyendo Backend..." -ForegroundColor Gray
docker build -t "$acrLoginServer/smartparku-backend:latest" ./backend

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR construyendo imagen del backend" -ForegroundColor Red
    exit 1
}

Write-Host "Subiendo Backend..." -ForegroundColor Gray
docker push "$acrLoginServer/smartparku-backend:latest"

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR subiendo backend" -ForegroundColor Red
    exit 1
}

Write-Host "Backend subido correctamente" -ForegroundColor Green

# Construir y subir Frontend
Write-Host "Construyendo Frontend..." -ForegroundColor Gray
docker build -t "$acrLoginServer/smartparku-frontend:latest" ./frontend

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR construyendo imagen del frontend" -ForegroundColor Red
    exit 1
}

Write-Host "Subiendo Frontend..." -ForegroundColor Gray
docker push "$acrLoginServer/smartparku-frontend:latest"

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR subiendo frontend" -ForegroundColor Red
    exit 1
}

Write-Host "Frontend subido correctamente" -ForegroundColor Green
Write-Host ""

# PASO 4: Crear Base de Datos
Write-Host "PASO 4/9: Creando base de datos PostgreSQL..." -ForegroundColor Cyan
Write-Host "Esto puede tomar 5-10 minutos..." -ForegroundColor Gray

$dbExists = az postgres flexible-server show --name $DbServerName --resource-group $ResourceGroup 2>$null
if ($dbExists) {
    Write-Host "Base de datos ya existe" -ForegroundColor Yellow
} else {
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
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Servidor PostgreSQL creado" -ForegroundColor Green
        
        az postgres flexible-server db create `
            --resource-group $ResourceGroup `
            --server-name $DbServerName `
            --database-name smartparku `
            --output none
        
        Write-Host "Base de datos creada" -ForegroundColor Green
    } else {
        Write-Host "ERROR creando base de datos" -ForegroundColor Red
        exit 1
    }
}

$dbHost = "$DbServerName.postgres.database.azure.com"
$databaseUrl = "postgresql+psycopg://${DbAdminUser}:${DbAdminPassword}@${dbHost}:5432/smartparku"
Write-Host ""

# PASO 5: Crear Container Apps Environment
Write-Host "PASO 5/9: Creando Container Apps Environment..." -ForegroundColor Cyan

$envName = "smartparku-env"
$envExists = az containerapp env show --name $envName --resource-group $ResourceGroup 2>$null
if ($envExists) {
    Write-Host "Environment ya existe" -ForegroundColor Yellow
} else {
    az containerapp env create `
        --name $envName `
        --resource-group $ResourceGroup `
        --location $Location `
        --output none
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Container Apps Environment creado" -ForegroundColor Green
    } else {
        Write-Host "ERROR creando environment" -ForegroundColor Red
        exit 1
    }
}
Write-Host ""

# PASO 6: Desplegar Backend
Write-Host "PASO 6/9: Desplegando Backend..." -ForegroundColor Cyan

$backendAppName = "smartparku-backend"
$backendExists = az containerapp show --name $backendAppName --resource-group $ResourceGroup 2>$null

if ($backendExists) {
    Write-Host "Actualizando backend..." -ForegroundColor Gray
    az containerapp update `
        --name $backendAppName `
        --resource-group $ResourceGroup `
        --image "$acrLoginServer/smartparku-backend:latest" `
        --output none
} else {
    Write-Host "Creando backend..." -ForegroundColor Gray
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
        --env-vars "DATABASE_URL=$databaseUrl" "SECRET_KEY=produccion-secret-key-2026" "ALGORITHM=HS256" "ACCESS_TOKEN_EXPIRE_MINUTES=60" "MQTT_BROKER=7de2fa1d05f84c5c8f2fcacca06d98da.s1.eu.hivemq.cloud" "MQTT_PORT=8883" "MQTT_USERNAME=Juliana" "MQTT_PASSWORD=1138524566Juli*" `
        --output none
}

if ($LASTEXITCODE -eq 0) {
    $backendUrl = az containerapp show `
        --name $backendAppName `
        --resource-group $ResourceGroup `
        --query "properties.configuration.ingress.fqdn" `
        --output tsv
    
    Write-Host "Backend desplegado correctamente" -ForegroundColor Green
    Write-Host "URL: https://$backendUrl" -ForegroundColor Green
} else {
    Write-Host "ERROR desplegando backend" -ForegroundColor Red
    exit 1
}
Write-Host ""

# PASO 7: Ejecutar migraciones
Write-Host "PASO 7/9: Ejecutando migraciones..." -ForegroundColor Cyan

Start-Sleep -Seconds 10

az containerapp exec `
    --name $backendAppName `
    --resource-group $ResourceGroup `
    --command "alembic upgrade head" `
    --output none 2>$null

Write-Host "Migraciones ejecutadas" -ForegroundColor Green

az containerapp exec `
    --name $backendAppName `
    --resource-group $ResourceGroup `
    --command "python app/initial_data.py" `
    --output none 2>$null

Write-Host "Datos iniciales cargados" -ForegroundColor Green
Write-Host ""

# PASO 8: Desplegar Frontend
Write-Host "PASO 8/9: Desplegando Frontend..." -ForegroundColor Cyan

$frontendAppName = "smartparku-frontend"
$frontendExists = az containerapp show --name $frontendAppName --resource-group $ResourceGroup 2>$null

if ($frontendExists) {
    Write-Host "Actualizando frontend..." -ForegroundColor Gray
    az containerapp update `
        --name $frontendAppName `
        --resource-group $ResourceGroup `
        --image "$acrLoginServer/smartparku-frontend:latest" `
        --set-env-vars "NEXT_PUBLIC_API_URL=https://$backendUrl" "NEXT_PUBLIC_WS_URL=wss://$backendUrl/api/v1/parking/ws/parking" `
        --output none
} else {
    Write-Host "Creando frontend..." -ForegroundColor Gray
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

if ($LASTEXITCODE -eq 0) {
    $frontendUrl = az containerapp show `
        --name $frontendAppName `
        --resource-group $ResourceGroup `
        --query "properties.configuration.ingress.fqdn" `
        --output tsv
    
    Write-Host "Frontend desplegado correctamente" -ForegroundColor Green
    Write-Host "URL: https://$frontendUrl" -ForegroundColor Green
} else {
    Write-Host "ERROR desplegando frontend" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Resumen
Write-Host "======================================" -ForegroundColor Green
Write-Host "DESPLIEGUE COMPLETADO" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""
Write-Host "URLS DE ACCESO:" -ForegroundColor Yellow
Write-Host "  Frontend:  https://$frontendUrl" -ForegroundColor White
Write-Host "  Backend:   https://$backendUrl" -ForegroundColor White
Write-Host "  API Docs:  https://$backendUrl/docs" -ForegroundColor White
Write-Host ""
Write-Host "USUARIOS DE PRUEBA:" -ForegroundColor Yellow
Write-Host "  Admin:      admin@ucc.edu.co / admin123" -ForegroundColor White
Write-Host "  Estudiante: estudiante@ucc.edu.co / estudiante123" -ForegroundColor White
Write-Host ""
Write-Host "IMPORTANTE:" -ForegroundColor Red
Write-Host "  Cuando termines de probar, ejecuta:" -ForegroundColor Yellow
Write-Host "  .\delete-all.ps1" -ForegroundColor Red
Write-Host ""
Write-Host "======================================" -ForegroundColor Green
