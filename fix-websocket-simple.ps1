# ========================================
# SmartParkU - Fix WebSocket SIMPLE
# ========================================

$ErrorActionPreference = "Stop"

Write-Host "`n======================================" -ForegroundColor Cyan
Write-Host "SmartParkU - Fix WebSocket" -ForegroundColor Cyan
Write-Host "======================================`n" -ForegroundColor Cyan

$RESOURCE_GROUP = "smartparku-rg"
$ACR_NAME = "smartparkuacr"
$FRONTEND_IMAGE = "$ACR_NAME.azurecr.io/smartparku-frontend"
$FRONTEND_APP = "smartparku-frontend"

Write-Host "1. Obteniendo URL del backend..." -ForegroundColor Yellow
$BACKEND_FQDN = az containerapp show --name smartparku-backend --resource-group $RESOURCE_GROUP --query "properties.configuration.ingress.fqdn" --output tsv

if (-not $BACKEND_FQDN) {
    Write-Host "ERROR: No se pudo obtener URL del backend" -ForegroundColor Red
    exit 1
}

$BACKEND_URL = "https://$BACKEND_FQDN"
$WS_URL = "wss://$BACKEND_FQDN/api/v1/parking/ws/parking"

Write-Host "   Backend: $BACKEND_URL" -ForegroundColor Green
Write-Host "   WebSocket: $WS_URL" -ForegroundColor Green

Write-Host "`n2. Login al registry..." -ForegroundColor Yellow
az acr login --name $ACR_NAME
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "`n3. Construyendo frontend (2-3 minutos)..." -ForegroundColor Yellow
docker build --build-arg NEXT_PUBLIC_API_URL=$BACKEND_URL --build-arg NEXT_PUBLIC_WS_URL=$WS_URL -t ${FRONTEND_IMAGE}:v4 -f frontend/Dockerfile frontend/

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR en build" -ForegroundColor Red
    exit 1
}

Write-Host "`n4. Subiendo imagen..." -ForegroundColor Yellow
docker push ${FRONTEND_IMAGE}:v4

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR en push" -ForegroundColor Red
    exit 1
}

Write-Host "`n5. Actualizando Container App..." -ForegroundColor Yellow
az containerapp update --name $FRONTEND_APP --resource-group $RESOURCE_GROUP --image ${FRONTEND_IMAGE}:v4

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR en update" -ForegroundColor Red
    exit 1
}

Write-Host "`n======================================" -ForegroundColor Green
Write-Host "COMPLETADO" -ForegroundColor Green
Write-Host "======================================`n" -ForegroundColor Green

$FRONTEND_FQDN = az containerapp show --name $FRONTEND_APP --resource-group $RESOURCE_GROUP --query "properties.configuration.ingress.fqdn" --output tsv

Write-Host "Frontend: https://$FRONTEND_FQDN" -ForegroundColor White
Write-Host "`nESPERA 2 MINUTOS, luego:" -ForegroundColor Yellow
Write-Host "1. Abre el frontend" -ForegroundColor White
Write-Host "2. Presiona Ctrl+Shift+R" -ForegroundColor White
Write-Host "3. Abre F12 y login" -ForegroundColor White
Write-Host "4. Verifica que diga wss:// en consola`n" -ForegroundColor White
