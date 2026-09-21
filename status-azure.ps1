# ═══════════════════════════════════════════════════════════════════════════
# 📊 Script para Verificar Estado y Costos de SmartParkU
# ═══════════════════════════════════════════════════════════════════════════

param(
    [string]$ResourceGroup = "smartparku-rg",
    [string]$BackendApp = "smartparku-backend",
    [string]$FrontendApp = "smartparku-frontend",
    [string]$DbServer = "smartparku-db"
)

Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  📊 Estado de SmartParkU" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Verificar login
$account = az account show 2>$null
if (-not $account) {
    Write-Host "❌ No estás logueado en Azure" -ForegroundColor Red
    az login
}

# ─────────────────────────────────────────────────────────────────────────────
# Verificar si el grupo de recursos existe
# ─────────────────────────────────────────────────────────────────────────────

$rgExists = az group exists --name $ResourceGroup
if ($rgExists -eq "false") {
    Write-Host "❌ Grupo de recursos '$ResourceGroup' no existe" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Primero debes desplegar la aplicación:" -ForegroundColor Yellow
    Write-Host "   .\deploy-azure.ps1" -ForegroundColor White
    Write-Host ""
    exit 1
}

# ─────────────────────────────────────────────────────────────────────────────
# Backend
# ─────────────────────────────────────────────────────────────────────────────

Write-Host "🔹 BACKEND:" -ForegroundColor Cyan

$backendInfo = az containerapp show `
    --name $BackendApp `
    --resource-group $ResourceGroup `
    --output json 2>$null | ConvertFrom-Json

if ($backendInfo) {
    $backendReplicas = $backendInfo.properties.template.scale.minReplicas
    $backendUrl = $backendInfo.properties.configuration.ingress.fqdn
    
    if ($backendReplicas -eq 0) {
        Write-Host "   Estado:   🛑 DETENIDO (0 réplicas)" -ForegroundColor Yellow
        Write-Host "   Costo:    `$0/mes" -ForegroundColor Green
    } else {
        Write-Host "   Estado:   ✅ ACTIVO ($backendReplicas réplica(s))" -ForegroundColor Green
        Write-Host "   URL:      https://$backendUrl" -ForegroundColor White
        Write-Host "   API Docs: https://$backendUrl/docs" -ForegroundColor White
        Write-Host "   Costo:    ~`$20/mes" -ForegroundColor Yellow
    }
} else {
    Write-Host "   Estado:   ❌ NO EXISTE" -ForegroundColor Red
}

Write-Host ""

# ─────────────────────────────────────────────────────────────────────────────
# Frontend
# ─────────────────────────────────────────────────────────────────────────────

Write-Host "🔹 FRONTEND:" -ForegroundColor Cyan

$frontendInfo = az containerapp show `
    --name $FrontendApp `
    --resource-group $ResourceGroup `
    --output json 2>$null | ConvertFrom-Json

if ($frontendInfo) {
    $frontendReplicas = $frontendInfo.properties.template.scale.minReplicas
    $frontendUrl = $frontendInfo.properties.configuration.ingress.fqdn
    
    if ($frontendReplicas -eq 0) {
        Write-Host "   Estado:   🛑 DETENIDO (0 réplicas)" -ForegroundColor Yellow
        Write-Host "   Costo:    `$0/mes" -ForegroundColor Green
    } else {
        Write-Host "   Estado:   ✅ ACTIVO ($frontendReplicas réplica(s))" -ForegroundColor Green
        Write-Host "   URL:      https://$frontendUrl" -ForegroundColor White
        Write-Host "   Costo:    ~`$20/mes" -ForegroundColor Yellow
    }
} else {
    Write-Host "   Estado:   ❌ NO EXISTE" -ForegroundColor Red
}

Write-Host ""

# ─────────────────────────────────────────────────────────────────────────────
# Base de Datos
# ─────────────────────────────────────────────────────────────────────────────

Write-Host "🔹 BASE DE DATOS:" -ForegroundColor Cyan

$dbInfo = az postgres flexible-server show `
    --name $DbServer `
    --resource-group $ResourceGroup `
    --output json 2>$null | ConvertFrom-Json

if ($dbInfo) {
    $dbState = $dbInfo.state
    $dbHost = $dbInfo.fullyQualifiedDomainName
    
    if ($dbState -eq "Ready") {
        Write-Host "   Estado:   ✅ ACTIVA" -ForegroundColor Green
        Write-Host "   Host:     $dbHost" -ForegroundColor White
        Write-Host "   Costo:    ~`$20/mes" -ForegroundColor Yellow
    } elseif ($dbState -eq "Stopped") {
        Write-Host "   Estado:   🛑 DETENIDA" -ForegroundColor Yellow
        Write-Host "   Costo:    `$0/mes" -ForegroundColor Green
    } else {
        Write-Host "   Estado:   ⏳ $dbState" -ForegroundColor Gray
        Write-Host "   Costo:    Variable" -ForegroundColor Gray
    }
} else {
    Write-Host "   Estado:   ❌ NO EXISTE" -ForegroundColor Red
}

Write-Host ""

# ─────────────────────────────────────────────────────────────────────────────
# Container Registry
# ─────────────────────────────────────────────────────────────────────────────

Write-Host "🔹 CONTAINER REGISTRY:" -ForegroundColor Cyan

$acrList = az acr list --resource-group $ResourceGroup --output json 2>$null | ConvertFrom-Json

if ($acrList -and $acrList.Count -gt 0) {
    $acrName = $acrList[0].name
    Write-Host "   Estado:   ✅ ACTIVO (siempre)" -ForegroundColor Green
    Write-Host "   Nombre:   $acrName" -ForegroundColor White
    Write-Host "   Costo:    ~`$5/mes" -ForegroundColor Gray
} else {
    Write-Host "   Estado:   ❌ NO EXISTE" -ForegroundColor Red
}

Write-Host ""

# ─────────────────────────────────────────────────────────────────────────────
# Resumen de Costos
# ─────────────────────────────────────────────────────────────────────────────

Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  💰 RESUMEN DE COSTOS ESTIMADOS" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$totalCost = 0
$backendCost = 0
$frontendCost = 0
$dbCost = 0
$acrCost = 5

if ($backendInfo -and $backendReplicas -gt 0) {
    $backendCost = 20
    $totalCost += $backendCost
}

if ($frontendInfo -and $frontendReplicas -gt 0) {
    $frontendCost = 20
    $totalCost += $frontendCost
}

if ($dbInfo -and $dbState -eq "Ready") {
    $dbCost = 20
    $totalCost += $dbCost
}

$totalCost += $acrCost

Write-Host "   Backend:         `$$backendCost/mes" -ForegroundColor $(if ($backendCost -gt 0) { "Yellow" } else { "Green" })
Write-Host "   Frontend:        `$$frontendCost/mes" -ForegroundColor $(if ($frontendCost -gt 0) { "Yellow" } else { "Green" })
Write-Host "   Base de Datos:   `$$dbCost/mes" -ForegroundColor $(if ($dbCost -gt 0) { "Yellow" } else { "Green" })
Write-Host "   Registry:        `$$acrCost/mes" -ForegroundColor Gray
Write-Host "   ─────────────────────────" -ForegroundColor Gray
Write-Host "   TOTAL ACTUAL:    `$$totalCost/mes" -ForegroundColor $(if ($totalCost -gt 30) { "Yellow" } else { "Green" })
Write-Host ""

$maxCost = 70
$savings = $maxCost - $totalCost
$savingsPercent = [math]::Round(($savings / $maxCost) * 100)

if ($savings -gt 0) {
    Write-Host "   💰 AHORRO ACTUAL: `$$savings/mes ($savingsPercent%)" -ForegroundColor Green
}

Write-Host ""

# ─────────────────────────────────────────────────────────────────────────────
# Acciones sugeridas
# ─────────────────────────────────────────────────────────────────────────────

Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  💡 ACCIONES DISPONIBLES" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

if ($totalCost -gt 30) {
    Write-Host "⚠️  Las apps están activas y generando costos" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Para ahorrar, detén las apps cuando no las uses:" -ForegroundColor White
    Write-Host "   .\stop-azure.ps1                  (ahorra ~`$40/mes)" -ForegroundColor Green
    Write-Host "   .\stop-azure.ps1 -IncludeDatabase (ahorra ~`$65/mes)" -ForegroundColor Green
} elseif ($totalCost -le 10) {
    Write-Host "✅ Excelente! Estás ahorrando el máximo posible" -ForegroundColor Green
    Write-Host ""
    Write-Host "   Para reactivar cuando necesites:" -ForegroundColor White
    Write-Host "   .\start-azure.ps1                  (solo apps)" -ForegroundColor White
    Write-Host "   .\start-azure.ps1 -IncludeDatabase (apps + BD)" -ForegroundColor White
} else {
    Write-Host "✅ Buena gestión de costos" -ForegroundColor Green
    Write-Host ""
    Write-Host "   Comandos disponibles:" -ForegroundColor White
    Write-Host "   .\stop-azure.ps1     - Detener apps" -ForegroundColor White
    Write-Host "   .\start-azure.ps1    - Reactivar apps" -ForegroundColor White
}

Write-Host ""
Write-Host "📖 Más información: GUIA_CONTROL_COSTOS_AZURE.md" -ForegroundColor Gray
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
