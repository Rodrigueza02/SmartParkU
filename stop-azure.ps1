# ═══════════════════════════════════════════════════════════════════════════
# 🛑 Script para Detener SmartParkU y Ahorrar Costos
# ═══════════════════════════════════════════════════════════════════════════

param(
    [string]$ResourceGroup = "smartparku-rg",
    [string]$BackendApp = "smartparku-backend",
    [string]$FrontendApp = "smartparku-frontend",
    [string]$DbServer = "smartparku-db",
    [switch]$IncludeDatabase = $false
)

Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🛑 Deteniendo SmartParkU" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Verificar login
$account = az account show 2>$null
if (-not $account) {
    Write-Host "❌ No estás logueado en Azure" -ForegroundColor Red
    az login
}

# ─────────────────────────────────────────────────────────────────────────────
# PASO 1: Detener Backend
# ─────────────────────────────────────────────────────────────────────────────

Write-Host "🛑 Deteniendo Backend..." -ForegroundColor Yellow

az containerapp update `
    --name $BackendApp `
    --resource-group $ResourceGroup `
    --min-replicas 0 `
    --max-replicas 0 `
    --output none

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Backend detenido (0 réplicas)" -ForegroundColor Green
} else {
    Write-Host "⚠️  Error deteniendo backend (puede que no exista aún)" -ForegroundColor Yellow
}

# ─────────────────────────────────────────────────────────────────────────────
# PASO 2: Detener Frontend
# ─────────────────────────────────────────────────────────────────────────────

Write-Host "🛑 Deteniendo Frontend..." -ForegroundColor Yellow

az containerapp update `
    --name $FrontendApp `
    --resource-group $ResourceGroup `
    --min-replicas 0 `
    --max-replicas 0 `
    --output none

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Frontend detenido (0 réplicas)" -ForegroundColor Green
} else {
    Write-Host "⚠️  Error deteniendo frontend (puede que no exista aún)" -ForegroundColor Yellow
}

# ─────────────────────────────────────────────────────────────────────────────
# PASO 3: Detener Base de Datos (Opcional)
# ─────────────────────────────────────────────────────────────────────────────

if ($IncludeDatabase) {
    Write-Host "🛑 Deteniendo Base de Datos..." -ForegroundColor Yellow
    
    az postgres flexible-server stop `
        --name $DbServer `
        --resource-group $ResourceGroup `
        --output none
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Base de datos detenida" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Error deteniendo base de datos (puede que no exista aún)" -ForegroundColor Yellow
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# RESUMEN
# ─────────────────────────────────────────────────────────────────────────────

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ✅ SmartParkU Detenido" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 ESTADO DE COSTOS:" -ForegroundColor Yellow

if ($IncludeDatabase) {
    Write-Host "   Container Apps:  `$0/mes (detenidos)" -ForegroundColor Green
    Write-Host "   Base de Datos:   `$0/mes (detenida)" -ForegroundColor Green
    Write-Host "   Registry:        `$5/mes (siempre activo)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   TOTAL:           ~`$5/mes" -ForegroundColor Green
    Write-Host "   AHORRO:          ~`$65/mes (93%)" -ForegroundColor Green
} else {
    Write-Host "   Container Apps:  `$0/mes (detenidos)" -ForegroundColor Green
    Write-Host "   Base de Datos:   ~`$20/mes (activa)" -ForegroundColor Yellow
    Write-Host "   Registry:        `$5/mes (siempre activo)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   TOTAL:           ~`$25/mes" -ForegroundColor Yellow
    Write-Host "   AHORRO:          ~`$45/mes (64%)" -ForegroundColor Green
}

Write-Host ""
Write-Host "💡 PARA REACTIVAR:" -ForegroundColor Yellow
if ($IncludeDatabase) {
    Write-Host "   .\start-azure.ps1 -IncludeDatabase" -ForegroundColor White
} else {
    Write-Host "   .\start-azure.ps1" -ForegroundColor White
}
Write-Host ""
Write-Host "📖 Más información: GUIA_CONTROL_COSTOS_AZURE.md" -ForegroundColor Gray
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
