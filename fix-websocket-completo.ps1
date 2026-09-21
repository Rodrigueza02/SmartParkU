# ========================================
# SmartParkU - Fix WebSocket COMPLETO
# ========================================

$ErrorActionPreference = "Stop"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "SmartParkU - Fix WebSocket COMPLETO" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Variables
$RESOURCE_GROUP = "smartparku-rg"
$ACR_NAME = "smartparkuacr"
$FRONTEND_IMAGE = "$ACR_NAME.azurecr.io/smartparku-frontend"
$FRONTEND_APP = "smartparku-frontend"

Write-Host "PASO 1/6: Obteniendo URL del backend..." -ForegroundColor Yellow
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

Write-Host "`nPASO 2/6: Login al Container Registry..." -ForegroundColor Yellow
az acr login --name $ACR_NAME | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR logeando al registry" -ForegroundColor Red
    exit 1
}
Write-Host "  Login exitoso" -ForegroundColor Green

Write-Host "`nPASO 3/6: Limpiando imagenes Docker locales antiguas..." -ForegroundColor Yellow
docker rmi ${FRONTEND_IMAGE}:v2 -f 2>&1 | Out-Null
docker rmi ${FRONTEND_IMAGE}:v3 -f 2>&1 | Out-Null
docker rmi ${FRONTEND_IMAGE}:latest -f 2>&1 | Out-Null
Write-Host "  Limpieza completada (errores de imagenes no existentes son normales)" -ForegroundColor Green

Write-Host "`nPASO 4/6: Construyendo Frontend con configuracion correcta..." -ForegroundColor Yellow
Write-Host "  Build args:" -ForegroundColor Gray
Write-Host "    NEXT_PUBLIC_API_URL = $BACKEND_URL" -ForegroundColor Gray
Write-Host "    NEXT_PUBLIC_WS_URL = $WS_URL" -ForegroundColor Gray
Write-Host "  (Esto puede tomar 2-3 minutos...)" -ForegroundColor Gray

docker build `
    --no-cache `
    --build-arg NEXT_PUBLIC_API_URL=$BACKEND_URL `
    --build-arg NEXT_PUBLIC_WS_URL=$WS_URL `
    -t ${FRONTEND_IMAGE}:v4 `
    -t ${FRONTEND_IMAGE}:latest `
    -f frontend/Dockerfile `
    frontend/

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR construyendo imagen del frontend" -ForegroundColor Red
    exit 1
}

Write-Host "  Frontend v4 construido correctamente" -ForegroundColor Green

Write-Host "`nPASO 5/6: Subiendo imagen a Azure Container Registry..." -ForegroundColor Yellow
docker push ${FRONTEND_IMAGE}:v4

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR subiendo frontend" -ForegroundColor Red
    exit 1
}

Write-Host "  Frontend v4 subido correctamente" -ForegroundColor Green

Write-Host "`nPASO 6/6: Actualizando Container App..." -ForegroundColor Yellow
Write-Host "  - Aplicando imagen v4" -ForegroundColor Gray
Write-Host "  - Removiendo variables de entorno antiguas" -ForegroundColor Gray

# Actualizar con la nueva imagen sin variables de entorno
# (las variables ya están baked en la imagen desde el build)
az containerapp update `
    --name $FRONTEND_APP `
    --resource-group $RESOURCE_GROUP `
    --image ${FRONTEND_IMAGE}:v4 `
    --replace-env-vars "" 2>$null

if ($LASTEXITCODE -ne 0) {
    # Si falla con --replace-env-vars, intentar sin esa opcion
    az containerapp update `
        --name $FRONTEND_APP `
        --resource-group $RESOURCE_GROUP `
        --image ${FRONTEND_IMAGE}:v4
        
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR actualizando container app" -ForegroundColor Red
        exit 1
    }
}

Write-Host "  Container App actualizado correctamente" -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  FIX COMPLETADO" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Obtener URL del frontend
$FRONTEND_FQDN = az containerapp show `
    --name $FRONTEND_APP `
    --resource-group $RESOURCE_GROUP `
    --query "properties.configuration.ingress.fqdn" `
    --output tsv

Write-Host "`nURLs de tu aplicacion:" -ForegroundColor Cyan
Write-Host "  Frontend: https://$FRONTEND_FQDN" -ForegroundColor White
Write-Host "  Backend:  $BACKEND_URL" -ForegroundColor White

Write-Host "`nConfiguracion WebSocket:" -ForegroundColor Cyan
Write-Host "  Protocolo: WSS (WebSocket Secure) " -NoNewline; Write-Host "" -ForegroundColor Green
Write-Host "  Endpoint: $WS_URL" -ForegroundColor White

Write-Host "`n ESPERA 1-2 MINUTOS para que Azure termine de aplicar cambios" -ForegroundColor Yellow

Write-Host "`n LUEGO PRUEBA:" -ForegroundColor Cyan
Write-Host "  1. Abre: https://$FRONTEND_FQDN" -ForegroundColor White
Write-Host "  2. Abre la consola del navegador (F12)" -ForegroundColor White
Write-Host "  3. Login: admin@ucc.edu.co / admin123" -ForegroundColor White
Write-Host "  4. Verifica en F12 que NO haya errores 'Mixed Content'" -ForegroundColor White
Write-Host "  5. Dashboard debe decir 'En vivo' o 'Conectado'" -ForegroundColor White
Write-Host "  6. Genera QR y escanealo -> Mapa debe actualizarse" -ForegroundColor White

Write-Host "`n Si aun ves 'ws://' en F12, presiona Ctrl+Shift+R para forzar recarga" -ForegroundColor Yellow

Write-Host "`n RECUERDA ELIMINAR TODO DESPUES:" -ForegroundColor Red
Write-Host "  .\delete-all.ps1" -ForegroundColor White
Write-Host ""
