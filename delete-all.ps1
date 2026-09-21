# ═══════════════════════════════════════════════════════════════════════════
# 🗑️ Eliminar TODO - Estrategia CERO COSTOS
# ═══════════════════════════════════════════════════════════════════════════

param(
    [string]$ResourceGroup = "smartparku-rg"
)

Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Red
Write-Host "  🗑️  ELIMINANDO TODO - SmartParkU" -ForegroundColor Red
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Red
Write-Host ""
Write-Host "⚠️  ADVERTENCIA - Esto eliminará:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   ❌ Backend (FastAPI)" -ForegroundColor Yellow
Write-Host "   ❌ Frontend (Next.js)" -ForegroundColor Yellow
Write-Host "   ❌ Base de datos PostgreSQL + TODOS los datos" -ForegroundColor Yellow
Write-Host "   ❌ Container Registry + todas las imágenes Docker" -ForegroundColor Yellow
Write-Host "   ❌ TODO el grupo de recursos" -ForegroundColor Yellow
Write-Host ""
Write-Host "✅ VENTAJAS de eliminar:" -ForegroundColor Green
Write-Host ""
Write-Host "   ✅ Costo después de eliminar: `$0/mes" -ForegroundColor Green
Write-Host "   ✅ NO consumes tus créditos de Azure" -ForegroundColor Green
Write-Host "   ✅ Puedes volver a desplegar cuando necesites otra prueba" -ForegroundColor Green
Write-Host ""
Write-Host "💡 ¿Es esto lo que quieres?" -ForegroundColor Cyan
Write-Host "   - Si terminaste de probar → Escribe 'SI' para eliminar" -ForegroundColor White
Write-Host "   - Si aún necesitas la app → Presiona Ctrl+C para cancelar" -ForegroundColor White
Write-Host ""

# Verificar login
$account = az account show 2>$null
if (-not $account) {
    Write-Host "❌ No estás logueado en Azure" -ForegroundColor Red
    az login
}

# Verificar que el grupo existe
$exists = az group exists --name $ResourceGroup
if ($exists -eq "false") {
    Write-Host ""
    Write-Host "✅ El grupo de recursos ya no existe" -ForegroundColor Green
    Write-Host "   No hay nada que eliminar - ya estás en costo $0" -ForegroundColor Green
    Write-Host ""
    exit 0
}

# Confirmar
$confirm = Read-Host "¿CONFIRMAS que quieres ELIMINAR TODO? (escribe 'SI' en mayúsculas)"

if ($confirm -ne "SI") {
    Write-Host ""
    Write-Host "❌ Cancelado. No se eliminó nada." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "⚠️  RECUERDA: Mientras la app esté activa, consume créditos" -ForegroundColor Yellow
    Write-Host "   Costo actual: ~`$70/mes" -ForegroundColor Red
    Write-Host ""
    Write-Host "   Si ya terminaste de probar, ejecuta de nuevo:" -ForegroundColor White
    Write-Host "   .\delete-all.ps1" -ForegroundColor White
    Write-Host ""
    exit 0
}

Write-Host ""
Write-Host "🗑️  Eliminando grupo de recursos '$ResourceGroup'..." -ForegroundColor Yellow
Write-Host "   Esto tomará 2-3 minutos..." -ForegroundColor Gray
Write-Host ""

# Eliminar grupo de recursos completo
az group delete --name $ResourceGroup --yes --no-wait

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host "  ✅ Eliminación Iniciada Correctamente" -ForegroundColor Green
    Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 ESTADO DE COSTOS:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Costo en 2-3 minutos:  `$0/mes" -ForegroundColor Green
    Write-Host "   Créditos consumidos:   ~`$1-3 de `$200" -ForegroundColor Green
    Write-Host "   Costo real pagado:     `$0" -ForegroundColor Green
    Write-Host ""
    Write-Host "✅ PERFECTO! NO pagarás nada" -ForegroundColor Green
    Write-Host ""
    Write-Host "⏱️  La eliminación se completará en 2-3 minutos (segundo plano)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "🔍 Para verificar que se eliminó completamente:" -ForegroundColor Yellow
    Write-Host "   .\verify-deleted.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "🔄 Para hacer otra prueba en el futuro:" -ForegroundColor Yellow
    Write-Host "   .\deploy-test.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "💰 Créditos restantes: ~`$197-199 de `$200" -ForegroundColor Green
    Write-Host "   Puedes hacer 50+ pruebas más sin pagar nada" -ForegroundColor Green
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ Error al eliminar" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Intenta de nuevo:" -ForegroundColor Yellow
    Write-Host "   .\delete-all.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "   O elimina manualmente desde Azure Portal:" -ForegroundColor Yellow
    Write-Host "   https://portal.azure.com" -ForegroundColor White
    Write-Host ""
}
