# ═══════════════════════════════════════════════════════════════════════════
# ▶️ Script para Reactivar SmartParkU
# ═══════════════════════════════════════════════════════════════════════════

param(
    [string]$ResourceGroup = "smartparku-rg",
    [string]$BackendApp = "smartparku-backend",
    [string]$FrontendApp = "smartparku-frontend",
    [string]$DbServer = "smartparku-db",
    [switch]$IncludeDatabase = $false
)

Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ▶️  Reactivando SmartParkU" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Verificar login
$account = az account show 2>$null
if (-not $account) {
    Write-Host "❌ No estás logueado en Azure" -ForegroundColor Red
    az login
}

# ─────────────────────────────────────────────────────────────────────────────
# PASO 1: Reactivar Base de Datos (si está detenida)
# ─────────────────────────────────────────────────────────────────────────────

if ($IncludeDatabase) {
    Write-Host "▶️  Iniciando Base de Datos..." -ForegroundColor Yellow
    Write-Host "   ⏱️ Esto puede tomar 2-3 minutos..." -ForegroundColor Gray
    
    az postgres flexible-server start `
        --name $DbServer `
        --resource-group $ResourceGroup `
        --output none
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Base de datos iniciada" -ForegroundColor Green
        Write-Host "   Esperando 30 segundos para que esté completamente lista..." -ForegroundColor Gray
        Start-Sleep -Seconds 30
    } else {
        Write-Host "⚠️  Error iniciando base de datos (puede que ya esté activa)" -ForegroundColor Yellow
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# PASO 2: Reactivar Backend
# ─────────────────────────────────────────────────────────────────────────────

Write-Host "▶️  Reactivando Backend..." -ForegroundColor Yellow

az containerapp update `
    --name $BackendApp `
    --resource-group $ResourceGroup `
    --min-replicas 1 `
    --max-replicas 3 `
    --output none

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Backend reactivado" -ForegroundColor Green
} else {
    Write-Host "⚠️  Error reactivando backend" -ForegroundColor Red
}

# ─────────────────────────────────────────────────────────────────────────────
# PASO 3: Reactivar Frontend
# ─────────────────────────────────────────────────────────────────────────────

Write-Host "▶️  Reactivando Frontend..." -ForegroundColor Yellow

az containerapp update `
    --name $FrontendApp `
    --resource-group $ResourceGroup `
    --min-replicas 1 `
    --max-replicas 3 `
    --output none

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Frontend reactivado" -ForegroundColor Green
} else {
    Write-Host "⚠️  Error reactivando frontend" -ForegroundColor Red
}

# ─────────────────────────────────────────────────────────────────────────────
# PASO 4: Esperar y Obtener URLs
# ─────────────────────────────────────────────────────────────────────────────

Write-Host ""
Write-Host "⏱️  Esperando a que las aplicaciones inicien..." -ForegroundColor Yellow
Write-Host "   (Esto puede tomar 1-2 minutos)" -ForegroundColor Gray
Start-Sleep -Seconds 30

$backendUrl = az containerapp show `
    --name $BackendApp `
    --resource-group $ResourceGroup `
    --query "properties.configuration.ingress.fqdn" `
    --output tsv 2>$null

$frontendUrl = az containerapp show `
    --name $FrontendApp `
    --resource-group $ResourceGroup `
    --query "properties.configuration.ingress.fqdn" `
    --output tsv 2>$null

# ─────────────────────────────────────────────────────────────────────────────
# RESUMEN
# ─────────────────────────────────────────────────────────────────────────────

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ✅ SmartParkU Reactivado" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

if ($frontendUrl -and $backendUrl) {
    Write-Host "🌐 URLS DE ACCESO:" -ForegroundColor Yellow
    Write-Host "   Frontend:  https://$frontendUrl" -ForegroundColor White
    Write-Host "   Backend:   https://$backendUrl" -ForegroundColor White
    Write-Host "   API Docs:  https://$backendUrl/docs" -ForegroundColor White
    Write-Host ""
    Write-Host "👤 USUARIOS DE PRUEBA:" -ForegroundColor Yellow
    Write-Host "   Admin:      admin@ucc.edu.co / admin123" -ForegroundColor White
    Write-Host "   Estudiante: estudiante@ucc.edu.co / estudiante123" -ForegroundColor White
} else {
    Write-Host "⚠️  No se pudieron obtener las URLs (puede que las apps aún no existan)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "⏱️  Las aplicaciones pueden tomar 1-2 minutos adicionales en estar completamente listas" -ForegroundColor Gray
Write-Host ""
Write-Host "💰 COSTOS ACTIVOS:" -ForegroundColor Yellow
Write-Host "   ~`$70/mes mientras las apps estén corriendo" -ForegroundColor White
Write-Host ""
Write-Host "💡 PARA DETENER Y AHORRAR:" -ForegroundColor Yellow
if ($IncludeDatabase) {
    Write-Host "   .\stop-azure.ps1 -IncludeDatabase  (ahorro: 93%)" -ForegroundColor White
} else {
    Write-Host "   .\stop-azure.ps1                   (ahorro: 64%)" -ForegroundColor White
    Write-Host "   .\stop-azure.ps1 -IncludeDatabase  (ahorro: 93%)" -ForegroundColor White
}
Write-Host ""
Write-Host "📖 Más información: GUIA_CONTROL_COSTOS_AZURE.md" -ForegroundColor Gray
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
