# Verificar variables de entorno del frontend
$ErrorActionPreference = "Stop"

Write-Host "`nVerificando configuracion actual del frontend...`n" -ForegroundColor Cyan

# Verificar variables de entorno
Write-Host "Variables de entorno:" -ForegroundColor Yellow
az containerapp show `
  --name smartparku-frontend `
  --resource-group smartparku-rg `
  --query "properties.template.containers[0].env" `
  --output table

# Verificar imagen actual
Write-Host "`nImagen actual:" -ForegroundColor Yellow
az containerapp show `
  --name smartparku-frontend `
  --resource-group smartparku-rg `
  --query "properties.template.containers[0].image" `
  --output tsv

# Obtener URL del backend
Write-Host "`nURL del backend:" -ForegroundColor Yellow
$BACKEND_FQDN = az containerapp show `
  --name smartparku-backend `
  --resource-group smartparku-rg `
  --query "properties.configuration.ingress.fqdn" `
  --output tsv

Write-Host "  https://$BACKEND_FQDN" -ForegroundColor Green
Write-Host "`nWebSocket URL deberia ser:" -ForegroundColor Yellow
Write-Host "  wss://$BACKEND_FQDN/api/v1/parking/ws/parking" -ForegroundColor Green
Write-Host ""
