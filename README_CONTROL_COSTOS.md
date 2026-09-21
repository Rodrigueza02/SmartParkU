# 💰 Control de Costos Azure - Resumen Rápido

## 🎯 Objetivo: Solo Pagar Cuando Uses la App

Azure cobra por tiempo de uso. Si detienes los servicios cuando no los necesites, **NO pagas**.

---

## ⚡ Comandos Rápidos

```powershell
# Ver estado actual y costos
.\status-azure.ps1

# Detener apps (ahorra 64% - ~$40/mes)
.\stop-azure.ps1

# Detener TODO (ahorra 93% - ~$65/mes)
.\stop-azure.ps1 -IncludeDatabase

# Reactivar apps (toma 1-2 min)
.\start-azure.ps1

# Reactivar TODO (toma 3-5 min)
.\start-azure.ps1 -IncludeDatabase
```

---

## 📊 Tabla de Costos

| Escenario | Costo/Mes | Ahorro | Comando |
|-----------|-----------|--------|---------|
| **Todo activo 24/7** | **$70** | - | - |
| **Solo BD activa** | **$25** | $45 (64%) | `.\stop-azure.ps1` |
| **Todo detenido** | **$5** | $65 (93%) | `.\stop-azure.ps1 -IncludeDatabase` |

---

## 🔄 Flujo Recomendado para Pruebas

### Cuando Vayas a Probar

```powershell
# 1. Reactivar servicios (3-5 minutos)
.\start-azure.ps1 -IncludeDatabase

# 2. Esperar a que inicien
# Backend y frontend tardan ~2 minutos
# Base de datos tarda ~3 minutos

# 3. Acceder a la app
# Las URLs las muestra el script al finalizar

# 4. Probar la aplicación
# Hacer todas las pruebas necesarias
```

### Cuando Termines de Probar

```powershell
# Detener TODO para no generar costos
.\stop-azure.ps1 -IncludeDatabase

# Ahora pagarás solo ~$5/mes (solo Container Registry)
```

---

## ⏱️ Tiempos de Reactivación

| Componente | Tiempo |
|------------|--------|
| Container Apps | 1-2 minutos |
| PostgreSQL | 2-3 minutos |
| **Total** | **3-5 minutos** |

**Nota:** La primera solicitud después de reactivar puede tardar un poco más.

---

## 💡 Estrategias de Ahorro

### Estrategia 1: Pruebas Ocasionales (Máximo Ahorro)

```powershell
# Solo activa cuando necesites probar
.\start-azure.ps1 -IncludeDatabase
# ... hacer pruebas ...
.\stop-azure.ps1 -IncludeDatabase

# Costo: ~$5/mes (93% ahorro)
```

### Estrategia 2: Desarrollo Activo

```powershell
# Deja BD activa, solo apaga apps al final del día
.\stop-azure.ps1

# Por la mañana
.\start-azure.ps1

# Costo: ~$25/mes (64% ahorro)
```

### Estrategia 3: Horario de Trabajo (Programado)

```powershell
# Programar detención a las 6 PM
schtasks /create /tn "Detener SmartParkU" /tr "powershell -File C:\ruta\stop-azure.ps1" /sc daily /st 18:00

# Programar inicio a las 8 AM
schtasks /create /tn "Iniciar SmartParkU" /tr "powershell -File C:\ruta\start-azure.ps1" /sc daily /st 08:00

# Costo: ~$20-30/mes (60% ahorro)
```

---

## 📈 Cálculo de Ahorro Real

### Ejemplo: Solo pruebas 2 horas/día, 5 días/semana

```
Uso mensual: ~40 horas

Costo 24/7:        $70/mes
Costo solo pruebas: ~$10/mes
─────────────────────────────
AHORRO MENSUAL:    $60 (86%)
AHORRO ANUAL:      $720
```

---

## 🔍 Verificar Estado Actual

```powershell
# Ver estado detallado
.\status-azure.ps1
```

**Esto muestra:**
- ✅ Estado de cada servicio (activo/detenido)
- 💰 Costo actual estimado
- 📊 Ahorro comparado con 24/7
- 💡 Acciones sugeridas

---

## ⚠️ Importante: No Elimines Recursos

### ❌ NO HAGAS ESTO:
```powershell
# NO elimines el grupo de recursos
az group delete --name smartparku-rg

# NO elimines el Container Registry
az acr delete --name smartparkuacr
```

**Si los eliminas, pierdes:**
- Las imágenes Docker
- Los datos de la BD
- Toda la configuración

### ✅ HAZ ESTO:
```powershell
# Solo detén los servicios
.\stop-azure.ps1 -IncludeDatabase
```

---

## 🆘 Troubleshooting

### Problema: "Error deteniendo backend"
**Solución:** La app puede que no exista aún. Primero despliega:
```powershell
.\deploy-azure.ps1
```

### Problema: "No se pudieron obtener URLs"
**Solución:** Las apps están detenidas. Reactivarlas:
```powershell
.\start-azure.ps1
```

### Problema: "Tarda mucho en reactivar"
**Solución:** Es normal. Primera vez tarda 3-5 minutos. Ten paciencia.

---

## 📊 Monitoreo de Costos Real

### Ver costos acumulados del mes

```powershell
# Abrir portal de Azure
start https://portal.azure.com

# Ir a: Cost Management + Billing > Cost Analysis
# Filtrar por: Resource Group = smartparku-rg
```

### Configurar Alertas de Presupuesto

```powershell
# Crear alerta si gastas más de $50/mes
az consumption budget create `
  --resource-group smartparku-rg `
  --budget-name "smartparku-budget" `
  --amount 50 `
  --time-grain Monthly `
  --start-date 2026-09-01
```

---

## 📅 Calendario de Costos Estimado

| Mes | Escenario | Costo | Acumulado |
|-----|-----------|-------|-----------|
| 1 | Free tier + créditos | $0 | $0 |
| 2 | Usando créditos | $0 | $0 |
| 3 | Solo pruebas puntuales | $10 | $10 |
| 4 | Solo pruebas puntuales | $10 | $20 |
| 5 | Solo pruebas puntuales | $10 | $30 |
| 6 | Solo pruebas puntuales | $10 | $40 |
| **Total 6 meses** | | | **$40** |

**Comparado con 24/7:** $420 (ahorras $380)

---

## ✅ Checklist de Control de Costos

Después de desplegar:

- [ ] Ejecutar `.\status-azure.ps1` para ver estado
- [ ] Detener servicios: `.\stop-azure.ps1 -IncludeDatabase`
- [ ] Verificar que se detengan: `.\status-azure.ps1`
- [ ] Probar reactivación: `.\start-azure.ps1 -IncludeDatabase`
- [ ] Configurar alertas de presupuesto en Azure Portal
- [ ] Programar horarios si usas regularmente (opcional)

---

## 🎯 Regla de Oro

```
┌─────────────────────────────────────────┐
│                                         │
│  Siempre que termines de probar,       │
│  detén los servicios:                   │
│                                         │
│  .\stop-azure.ps1 -IncludeDatabase     │
│                                         │
│  Pagarás solo $5/mes en lugar de $70   │
│                                         │
└─────────────────────────────────────────┘
```

---

## 📚 Documentación Relacionada

- **`GUIA_CONTROL_COSTOS_AZURE.md`** - Guía completa de control de costos
- **`stop-azure.ps1`** - Script para detener servicios
- **`start-azure.ps1`** - Script para reactivar servicios
- **`status-azure.ps1`** - Script para ver estado y costos
- **`deploy-azure.ps1`** - Script de despliegue inicial

---

## 💬 Resumen de 3 Pasos

```powershell
# 1️⃣ DESPLEGAR (una vez)
.\deploy-azure.ps1

# 2️⃣ DETENER (cuando no uses)
.\stop-azure.ps1 -IncludeDatabase

# 3️⃣ REACTIVAR (cuando necesites)
.\start-azure.ps1 -IncludeDatabase
```

**Con esto pagas solo cuando usas la app! 🎉**

**Ahorro anual estimado: ~$780 (92%)**
