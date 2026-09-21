# ========================================
# SmartParkU - Redeployar Frontend con WebSocket Fix
# ========================================

$ErrorActionPreference = "Stop"

Write-Host "`n======================================" -ForegroundColor Cyan
Write-Host "SmartParkU - Redeployar Frontend (WebSocket Fix)" -ForegroundColor Cyan
Write-Host "======================================`n" -ForegroundColor Cyan

# Variables
$RESOURCE_GROUP = "smartparku-rg"
$ACR_NAME = "smartparkuacr"
$FRONTEND_IMAGE = "$ACR_NAME.azurecr.io/smartparku-frontend"
$FRONTEND_APP = "smartparku-frontend"

# Obtener URL del backend
Write-Host "Obteniendo URL del backend..." -ForegroundColor Yellow
$BACKEND_FQDN = az containerapp show `
    --name smartparku-backend `
    --resource-group $RESOURCE_GROUP `
    --query "properties.configuration.ingress.fqdn" `
    --output tsv

if (-not $BACKEND_FQDN) {
    Write-Host "ERROR: No se pudo obtener la URL del backend" -ForegroundColor Red
    exit 1
}

$BACKEND_URL = "https://$BACKEND_FQDN"
$WS_URL = "wss://$BACKEND_FQDN/api/v1/parking/ws/parking"

Write-Host "  Backend URL: $BACKEND_URL" -ForegroundColor Green
Write-Host "  WebSocket URL: $WS_URL" -ForegroundColor Green

# Login al Container Registry
Write-Host "`nLogeando al Container Registry..." -ForegroundColor Yellow
az acr login --name $ACR_NAME
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR logeando al registry" -ForegroundColor Red
    exit 1
}

# Rebuild frontend con las variables correctas
Write-Host "`nReconstruyendo Frontend con WebSocket fix..." -ForegroundColor Yellow
Write-Host "  (Esto puede tomar 2-3 minutos)" -ForegroundColor Gray

docker build `
    --build-arg NEXT_PUBLIC_API_URL=$BACKEND_URL `
    --build-arg NEXT_PUBLIC_WS_URL=$WS_URL `
    -t ${FRONTEND_IMAGE}:v3 `
    -f frontend/Dockerfile `
    frontend/

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR construyendo imagen del frontend" -ForegroundColor Red
    exit 1
}

Write-Host "Frontend reconstruido correctamente" -ForegroundColor Green

# Push de la imagen
Write-Host "`nSubiendo Frontend v3..." -ForegroundColor Yellow
docker push ${FRONTEND_IMAGE}:v3

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR subiendo frontend" -ForegroundColor Red
    exit 1
}

Write-Host "Frontend v3 subido correctamente" -ForegroundColor Green

# Actualizar Container App con la nueva imagen Y REMOVER variables de entorno
# (las variables ya estan en la imagen desde el build)
Write-Host "`nActualizando Container App con v3..." -ForegroundColor Yellow
Write-Host "  (Removiendo variables de entorno antiguas...)" -ForegroundColor Gray

# Primero remover TODAS las variables de entorno para empezar limpio
az containerapp update `
    --name $FRONTEND_APP `
    --resource-group $RESOURCE_GROUP `
    --image ${FRONTEND_IMAGE}:v3 `
    --remove-all-env-vars

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR actualizando container app" -ForegroundColor Red
    exit 1
}

Write-Host "Container App actualizado correctamente" -ForegroundColor Green

Write-Host "`n======================================" -ForegroundColor Green
Write-Host "  DESPLIEGUE COMPLETADO" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

# Obtener URL del frontend
$FRONTEND_FQDN = az containerapp show `
    --name $FRONTEND_APP `
    --resource-group $RESOURCE_GROUP `
    --query "properties.configuration.ingress.fqdn" `
    --output tsv

Write-Host "`nURLs de tu aplicacion:" -ForegroundColor Cyan
Write-Host "  Frontend: https://$FRONTEND_FQDN" -ForegroundColor White
Write-Host "  Backend:  $BACKEND_URL" -ForegroundColor White
Write-Host "`nWebSocket ahora usa WSS (seguro) en:" -ForegroundColor Cyan
Write-Host "  $WS_URL" -ForegroundColor White

Write-Host "`n PRUEBA LA APLICACION:" -ForegroundColor Yellow
Write-Host "  1. Abre https://$FRONTEND_FQDN" -ForegroundColor White
Write-Host "  2. Login con admin@ucc.edu.co / admin123" -ForegroundColor White
Write-Host "  3. Verifica que el dashboard diga 'En vivo' o 'Conectado'" -ForegroundColor White
Write-Host "  4. Genera un QR y escanealo" -ForegroundColor White
Write-Host "  5. El mapa debe actualizarse EN TIEMPO REAL" -ForegroundColor White

Write-Host "`n RECUERDA ELIMINAR TODO DESPUES:" -ForegroundColor Red
Write-Host "  .\delete-all.ps1" -ForegroundColor White
Write-Host ""
