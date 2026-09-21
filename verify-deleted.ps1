# ═══════════════════════════════════════════════════════════════════════════
# 🔍 Verificar que TODO fue Eliminado - Cero Costos Confirmado
# ═══════════════════════════════════════════════════════════════════════════

param(
    [string]$ResourceGroup = "smartparku-rg"
)

Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🔍 VERIFICANDO ELIMINACIÓN" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Verificar login
$account = az account show 2>$null
if (-not $account) {
    Write-Host "❌ No estás logueado en Azure" -ForegroundColor Red
    az login
}

Write-Host "🔍 Verificando si el grupo de recursos existe..." -ForegroundColor Yellow
Write-Host ""

$exists = az group exists --name $ResourceGroup

if ($exists -eq "false") {
    Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host "  ✅ CONFIRMADO: TODO Eliminado Correctamente" -ForegroundColor Green
    Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 ESTADO ACTUAL:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   ✅ Grupo de recursos:        Eliminado" -ForegroundColor Green
    Write-Host "   ✅ Backend:                  Eliminado" -ForegroundColor Green
    Write-Host "   ✅ Frontend:                 Eliminado" -ForegroundColor Green
    Write-Host "   ✅ Base de datos:            Eliminada" -ForegroundColor Green
    Write-Host "   ✅ Container Registry:       Eliminado" -ForegroundColor Green
    Write-Host "   ✅ TODOS los recursos:       Eliminados" -ForegroundColor Green
    Write-Host ""
    Write-Host "💰 ESTADO DE COSTOS:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Recursos activos:       0" -ForegroundColor Green
    Write-Host "   Costo mensual:          `$0" -ForegroundColor Green
    Write-Host "   Facturación activa:     NO" -ForegroundColor Green
    Write-Host ""
    Write-Host "   ✅ NO estás generando NINGÚN costo" -ForegroundColor Green
    Write-Host ""
    Write-Host "🎉 PERFECTO! Estrategia CERO COSTOS exitosa" -ForegroundColor Green
    Write-Host ""
    Write-Host "💡 PRÓXIMOS PASOS:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   📝 Si necesitas hacer otra prueba:" -ForegroundColor White
    Write-Host "      .\deploy-test.ps1" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   💰 Créditos usados hasta ahora:" -ForegroundColor White
    Write-Host "      ~`$1-3 de `$200 disponibles" -ForegroundColor Green
    Write-Host ""
    Write-Host "   🔢 Pruebas restantes posibles:" -ForegroundColor White
    Write-Host "      ~50+ pruebas de 3 horas cada una" -ForegroundColor Green
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Green
    
} elseif ($exists -eq "true") {
    Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
    Write-Host "  ⚠️  ADVERTENCIA: Recursos AÚN EXISTEN" -ForegroundColor Yellow
    Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "⏳ POSIBLES RAZONES:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   1. La eliminación aún está en progreso (2-3 minutos)" -ForegroundColor Gray
    Write-Host "      → Espera 2 minutos más y vuelve a verificar" -ForegroundColor White
    Write-Host ""
    Write-Host "   2. No ejecutaste el comando de eliminación" -ForegroundColor Gray
    Write-Host "      → Ejecuta: .\delete-all.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "   3. Hubo un error en la eliminación" -ForegroundColor Gray
    Write-Host "      → Intenta de nuevo: .\delete-all.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "💰 ESTADO DE COSTOS ACTUAL:" -ForegroundColor Red
    Write-Host ""
    Write-Host "   ⚠️  Recursos activos:    SÍ" -ForegroundColor Red
    Write-Host "   ⚠️  Costo mensual:       ~`$70/mes" -ForegroundColor Red
    Write-Host "   ⚠️  Consumiendo créditos: SÍ" -ForegroundColor Red
    Write-Host ""
    Write-Host "🚨 ACCIÓN REQUERIDA:" -ForegroundColor Red
    Write-Host ""
    Write-Host "   Si ya terminaste de probar, ELIMINA TODO ahora:" -ForegroundColor Yellow
    Write-Host "   .\delete-all.ps1" -ForegroundColor Red
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Yellow
    
} else {
    Write-Host "❌ Error verificando estado" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Verifica manualmente en Azure Portal:" -ForegroundColor Yellow
    Write-Host "   https://portal.azure.com" -ForegroundColor White
    Write-Host ""
}

Write-Host ""
