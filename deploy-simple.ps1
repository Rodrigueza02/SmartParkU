# Despliegue Simple para Prueba - SmartParkU

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DESPLEGANDO SmartParkU para PRUEBA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANTE - LEE ESTO:" -ForegroundColor Red
Write-Host ""
Write-Host "  Este despliegue usa tus CREDITOS GRATIS de Azure" -ForegroundColor Green
Write-Host "  NO pagaras NADA si eliminas todo al terminar" -ForegroundColor Green
Write-Host ""
Write-Host "  DESPUES DE PROBAR, DEBES ejecutar:" -ForegroundColor Yellow
Write-Host "     .\delete-all.ps1" -ForegroundColor Red
Write-Host ""
Write-Host "  Si olvidas eliminar, pagaras aprox $70/mes" -ForegroundColor Red
Write-Host ""

$confirm = Read-Host "Entendiste que debes eliminar todo despues? (escribe 'SI')"

if ($confirm -ne "SI") {
    Write-Host ""
    Write-Host "Cancelado. Lee ESTRATEGIA_CERO_COSTOS.md primero" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Costo estimado de esta prueba:" -ForegroundColor Yellow
Write-Host "  Si eliminas al terminar:  $0 (usa creditos gratis)" -ForegroundColor Green
Write-Host "  Si olvidas eliminar:      aprox $70/mes" -ForegroundColor Red
Write-Host ""
Write-Host "Iniciando despliegue (15-20 minutos)..." -ForegroundColor Cyan
Write-Host ""

# Ejecutar despliegue normal
.\deploy-azure.ps1

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Despliegue Completado - LISTO PARA PROBAR" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "AHORA PUEDES:" -ForegroundColor Yellow
Write-Host "  1. Abrir el frontend en tu navegador" -ForegroundColor White
Write-Host "  2. Probar todas las funcionalidades" -ForegroundColor White
Write-Host "  3. Tomar notas de lo que funciona/no funciona" -ForegroundColor White
Write-Host ""
Write-Host "Tienes TODO el tiempo que necesites para probar" -ForegroundColor Green
Write-Host ""
Write-Host "MUY IMPORTANTE - CUANDO TERMINES DE PROBAR:" -ForegroundColor Red
Write-Host ""
Write-Host "  .\delete-all.ps1" -ForegroundColor Red
Write-Host ""
Write-Host "  Esto eliminara TODO y NO pagaras NADA" -ForegroundColor Yellow
Write-Host ""
Write-Host "TIP: Pon una alarma para recordarte eliminar" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
