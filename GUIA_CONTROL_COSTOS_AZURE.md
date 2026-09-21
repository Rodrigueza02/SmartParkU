# 💰 Guía de Control de Costos - Azure Container Apps

## 🎯 Objetivo: Pagar Solo Cuando Uses la App

Azure Container Apps cobra por tiempo de ejecución. Si detienes las apps cuando no las uses, **NO pagas nada** (o muy poco).

---

## 📊 Costos por Componente

| Componente | Costo Activo | Costo Detenido | Acción |
|------------|--------------|----------------|--------|
| Backend Container App | $20/mes | **$0/mes** | ✅ Detener |
| Frontend Container App | $20/mes | **$0/mes** | ✅ Detener |
| PostgreSQL | $20/mes | **$5/mes** | ⚠️ Solo escalar |
| Container Registry | $5/mes | $5/mes | ❌ Siempre activo |
| **TOTAL Detenido** | **$70/mes** | **~$10/mes** | **87% ahorro** |

---

## 🛑 Opción 1: Detener Container Apps (Recomendado)

### **Ventaja:** Ahorro instantáneo, fácil de reactivar

### Detener Aplicaciones

```powershell
# Variables
$RESOURCE_GROUP = "smartparku-rg"
$BACKEND_APP = "smartparku-backend"
$FRONTEND_APP = "smartparku-frontend"

# Detener backend (escalar a 0 réplicas)
az containerapp update `
  --name $BACKEND_APP `
  --resource-group $RESOURCE_GROUP `
  --min-replicas 0 `
  --max-replicas 0

Write-Host "✅ Backend detenido (0 réplicas)" -ForegroundColor Green

# Detener frontend (escalar a 0 réplicas)
az containerapp update `
  --name $FRONTEND_APP `
  --resource-group $RESOURCE_GROUP `
  --min-replicas 0 `
  --max-replicas 0

Write-Host "✅ Frontend detenido (0 réplicas)" -ForegroundColor Green
Write-Host "💰 Ahora solo pagarás por la base de datos (~$20/mes)" -ForegroundColor Yellow
```

### Reactivar Aplicaciones

```powershell
# Reactivar backend
az containerapp update `
  --name $BACKEND_APP `
  --resource-group $RESOURCE_GROUP `
  --min-replicas 1 `
  --max-replicas 3

Write-Host "✅ Backend reactivado" -ForegroundColor Green

# Reactivar frontend
az containerapp update `
  --name $FRONTEND_APP `
  --resource-group $RESOURCE_GROUP `
  --min-replicas 1 `
  --max-replicas 3

Write-Host "✅ Frontend reactivado" -ForegroundColor Green
Write-Host "⏱️ Espera 1-2 minutos para que las apps inicien" -ForegroundColor Yellow
```

---

## 🛑 Opción 2: Detener Base de Datos (Máximo Ahorro)

### **Ventaja:** Ahorro máximo (~$90/mes)
### **Desventaja:** Tarda 2-3 minutos en reiniciar

### Detener Base de Datos

```powershell
$DB_SERVER = "smartparku-db"

# Detener servidor PostgreSQL
az postgres flexible-server stop `
  --name $DB_SERVER `
  --resource-group $RESOURCE_GROUP

Write-Host "✅ Base de datos detenida" -ForegroundColor Green
Write-Host "💰 Ahorro: ~$20/mes adicionales" -ForegroundColor Yellow
```

### Reactivar Base de Datos

```powershell
# Iniciar servidor PostgreSQL
az postgres flexible-server start `
  --name $DB_SERVER `
  --resource-group $RESOURCE_GROUP

Write-Host "✅ Base de datos iniciada" -ForegroundColor Green
Write-Host "⏱️ Espera 2-3 minutos para que esté lista" -ForegroundColor Yellow
```

---

## 🔄 Script Completo: Detener Todo

Crea un archivo `stop-azure.ps1`:

```powershell
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
    Write-Host "⚠️  Error deteniendo backend" -ForegroundColor Red
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
    Write-Host "⚠️  Error deteniendo frontend" -ForegroundColor Red
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
        Write-Host "⚠️  Error deteniendo base de datos" -ForegroundColor Red
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
    Write-Host "   Container Apps:  $0/mes (detenidos)" -ForegroundColor Green
    Write-Host "   Base de Datos:   $0/mes (detenida)" -ForegroundColor Green
    Write-Host "   Registry:        $5/mes (siempre activo)" -ForegroundColor Gray
    Write-Host "   TOTAL:           ~$5/mes" -ForegroundColor Green
    Write-Host "   AHORRO:          ~$65/mes (93%)" -ForegroundColor Green
} else {
    Write-Host "   Container Apps:  $0/mes (detenidos)" -ForegroundColor Green
    Write-Host "   Base de Datos:   ~$20/mes (activa)" -ForegroundColor Yellow
    Write-Host "   Registry:        $5/mes (siempre activo)" -ForegroundColor Gray
    Write-Host "   TOTAL:           ~$25/mes" -ForegroundColor Yellow
    Write-Host "   AHORRO:          ~$45/mes (64%)" -ForegroundColor Green
}

Write-Host ""
Write-Host "💡 PARA REACTIVAR:" -ForegroundColor Yellow
Write-Host "   .\start-azure.ps1" -ForegroundColor White
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
```

---

## 🔄 Script Completo: Reactivar Todo

Crea un archivo `start-azure.ps1`:

```powershell
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
        Start-Sleep -Seconds 30  # Esperar a que esté completamente lista
    } else {
        Write-Host "⚠️  Error iniciando base de datos" -ForegroundColor Red
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
Start-Sleep -Seconds 30

$backendUrl = az containerapp show `
    --name $BackendApp `
    --resource-group $ResourceGroup `
    --query "properties.configuration.ingress.fqdn" `
    --output tsv

$frontendUrl = az containerapp show `
    --name $FrontendApp `
    --resource-group $ResourceGroup `
    --query "properties.configuration.ingress.fqdn" `
    --output tsv

# ─────────────────────────────────────────────────────────────────────────────
# RESUMEN
# ─────────────────────────────────────────────────────────────────────────────

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ✅ SmartParkU Reactivado" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 URLS DE ACCESO:" -ForegroundColor Yellow
Write-Host "   Frontend:  https://$frontendUrl" -ForegroundColor White
Write-Host "   Backend:   https://$backendUrl" -ForegroundColor White
Write-Host "   API Docs:  https://$backendUrl/docs" -ForegroundColor White
Write-Host ""
Write-Host "⏱️  Las aplicaciones pueden tomar 1-2 minutos en estar completamente listas" -ForegroundColor Gray
Write-Host ""
Write-Host "💰 COSTOS ACTIVOS:" -ForegroundColor Yellow
Write-Host "   ~$70/mes mientras las apps estén corriendo" -ForegroundColor White
Write-Host ""
Write-Host "💡 PARA DETENER:" -ForegroundColor Yellow
Write-Host "   .\stop-azure.ps1" -ForegroundColor White
if ($IncludeDatabase) {
    Write-Host "   .\stop-azure.ps1 -IncludeDatabase" -ForegroundColor White
}
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
```

---

## 📅 Estrategias de Ahorro

### Estrategia 1: Solo Pruebas Puntuales (Máximo Ahorro)

```powershell
# Cuando NO uses la app
.\stop-azure.ps1 -IncludeDatabase

# Cuando necesites probar (toma 3-5 minutos)
.\start-azure.ps1 -IncludeDatabase

# Costo mensual: ~$5 (93% ahorro)
```

### Estrategia 2: Desarrollo Activo (Balance)

```powershell
# Detener solo las apps al final del día
.\stop-azure.ps1

# Reactivar al día siguiente (toma 1-2 minutos)
.\start-azure.ps1

# Costo mensual: ~$25 (64% ahorro)
```

### Estrategia 3: Horario de Trabajo (Automático)

```powershell
# Programar con Task Scheduler de Windows

# Detener a las 6 PM todos los días:
schtasks /create /tn "Detener SmartParkU" /tr "powershell.exe -File C:\path\to\stop-azure.ps1" /sc daily /st 18:00

# Reactivar a las 8 AM todos los días:
schtasks /create /tn "Iniciar SmartParkU" /tr "powershell.exe -File C:\path\to\start-azure.ps1" /sc daily /st 08:00

# Costo mensual: ~$20-30 (60% ahorro)
```

---

## 📊 Verificar Estado Actual

```powershell
# Ver réplicas activas de las apps
az containerapp show `
  --name smartparku-backend `
  --resource-group smartparku-rg `
  --query "properties.template.scale" `
  --output table

# Ver estado de la base de datos
az postgres flexible-server show `
  --name smartparku-db `
  --resource-group smartparku-rg `
  --query "state" `
  --output tsv
```

---

## 💡 Tips Adicionales

### 1. Auto-Scale a 0 (Ahorro Inteligente)

Azure puede escalar automáticamente a 0 si no hay tráfico:

```powershell
az containerapp update `
  --name smartparku-backend `
  --resource-group smartparku-rg `
  --min-replicas 0 `
  --max-replicas 3 `
  --scale-rule-name "http-scaling" `
  --scale-rule-type "http" `
  --scale-rule-http-concurrency 10
```

**Ventaja:** Se apaga automático si no hay uso por 10 minutos.

### 2. Usar Tier Burstable para BD

Ya está configurado, pero verifica:

```powershell
az postgres flexible-server show `
  --name smartparku-db `
  --resource-group smartparku-rg `
  --query "sku" `
  --output table
```

Debe ser: `Standard_B1ms` (más barato)

### 3. Monitorear Costos en Tiempo Real

```powershell
# Ver costos del mes actual
az consumption usage list `
  --start-date "2026-09-01" `
  --end-date "2026-09-30" `
  --query "[?contains(instanceName, 'smartparku')]" `
  --output table
```

---

## ⚠️ Advertencias Importantes

### ❌ NO elimines estos recursos:
- **Container Registry** - Necesitas las imágenes para reactivar
- **Resource Group** - Eliminaría TODO
- **Backups de BD** - Perderías los datos

### ✅ SÍ puedes detener:
- Container Apps (escalar a 0)
- PostgreSQL (stop/start)

### ⏱️ Tiempos de Reactivación:
- Container Apps: 1-2 minutos
- PostgreSQL: 2-3 minutos
- Total: ~5 minutos máximo

---

## 🎯 Resumen de Comandos Rápidos

```powershell
# DETENER TODO (máximo ahorro)
.\stop-azure.ps1 -IncludeDatabase

# DETENER SOLO APPS (mantener BD activa)
.\stop-azure.ps1

# REACTIVAR TODO
.\start-azure.ps1 -IncludeDatabase

# REACTIVAR SOLO APPS
.\start-azure.ps1

# VER ESTADO
az containerapp list --resource-group smartparku-rg --output table

# VER COSTOS
az consumption usage list --output table
```

---

## 📈 Comparación de Costos

| Escenario | Costo/Mes | Tiempo Activo |
|-----------|-----------|---------------|
| **24/7 activo** | **$70** | 720 hrs |
| **Solo días laborales 8-18h** | **$30** | ~220 hrs |
| **Solo cuando pruebes** | **$10** | ~40 hrs |
| **Todo detenido** | **$5** | 0 hrs |

---

## ✅ Checklist para Ahorrar

- [ ] Crear `stop-azure.ps1`
- [ ] Crear `start-azure.ps1`
- [ ] Probar detener: `.\stop-azure.ps1`
- [ ] Verificar estado: `az containerapp list`
- [ ] Probar reactivar: `.\start-azure.ps1`
- [ ] Configurar auto-scale a 0 (opcional)
- [ ] Programar horarios (opcional)
- [ ] Monitorear costos semanalmente

---

**💰 Resultado: Paga solo cuando uses la app!**

**Para pruebas ocasionales: ~$5-10/mes (93% ahorro)**
