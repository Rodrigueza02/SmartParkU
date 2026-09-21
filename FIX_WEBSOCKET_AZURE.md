# 🔧 Fix WebSocket en Azure - SmartParkU

## 🎯 PROBLEMA IDENTIFICADO

El mapa de parqueadero mostraba **"Sin señal"** y **"Desconectado"** porque:

1. **Mixed Content Error**: El frontend (HTTPS) intentaba conectarse al WebSocket usando `ws://` (HTTP inseguro)
2. **Hardcoded URLs**: El código de `parkingStore.ts` construía la URL del WebSocket sin usar las variables de entorno
3. **Azure Container Apps**: Usa HTTPS/WSS por defecto, pero el código estaba forzando HTTP/WS

### Error en Consola del Navegador:
```
Mixed Content: The page at 'https://smartparku-frontend...' was loaded over HTTPS, 
but requested an insecure resource 'ws://...'. This request has been blocked.
```

---

## ✅ SOLUCIÓN IMPLEMENTADA

### 1. Actualización de `parkingStore.ts`

**ANTES (incorrecto):**
```typescript
const WS_URL = typeof window !== 'undefined'
  ? `ws://${window.location.hostname}:8000/api/v1/parking/ws/parking`
  : 'ws://localhost:8000/api/v1/parking/ws/parking';
```

**DESPUÉS (correcto):**
```typescript
const WS_URL = typeof window !== 'undefined'
  ? (process.env.NEXT_PUBLIC_WS_URL || `ws://${window.location.hostname}:8000/api/v1/parking/ws/parking`)
  : 'ws://localhost:8000/api/v1/parking/ws/parking';
```

### 2. Variables de Entorno en Build Time

El `Dockerfile` del frontend ya estaba configurado para recibir las variables:

```dockerfile
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_WS_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_WS_URL=$NEXT_PUBLIC_WS_URL
```

### 3. Script de Redeployar Frontend

Creado `redeploy-frontend-ws.ps1` que:
- Obtiene automáticamente la URL del backend
- Construye las URLs correctas con `wss://` para Azure
- Reconstruye el frontend como **v3** con las variables correctas
- Actualiza el Container App

---

## 🚀 PASOS PARA APLICAR EL FIX

### Desde PowerShell (fuera de Kiro):

```powershell
# 1. Ir al directorio del proyecto
cd C:\Users\helen\Downloads\SmartParkU

# 2. Ejecutar el script de redeployar
.\redeploy-frontend-ws.ps1
```

**Tiempo estimado:** 3-5 minutos

---

## 📋 QUÉ HACE EL SCRIPT

1. **Obtiene URL del backend** desde Azure
   - Ejemplo: `https://smartparku-backend.wonderfulfield-904d25d8.westus.azurecontainerapps.io`

2. **Construye URLs correctas:**
   - API: `https://smartparku-backend...`
   - WebSocket: `wss://smartparku-backend.../api/v1/parking/ws/parking`

3. **Reconstruye imagen del frontend** con:
   ```
   --build-arg NEXT_PUBLIC_API_URL=https://...
   --build-arg NEXT_PUBLIC_WS_URL=wss://...
   ```

4. **Sube imagen como v3** a Azure Container Registry

5. **Actualiza Container App** para usar la nueva imagen

---

## ✅ VERIFICACIÓN POST-DESPLIEGUE

### 1. Abrir el Frontend en el Navegador

```
https://smartparku-frontend.wonderfulfield-904d25d8.westus.azurecontainerapps.io
```

### 2. Login de Prueba

- **Admin**: `admin@ucc.edu.co` / `admin123`
- **Estudiante**: `estudiante@ucc.edu.co` / `estudiante123`

### 3. Verificar Estado del WebSocket

**Dashboard de Admin:**
- Debe mostrar **"En vivo"** (con ícono verde) en lugar de **"Desconectado"**

**Mapa de Estudiante:**
- Debe mostrar **"En vivo"** en lugar de **"Sin señal"**

### 4. Prueba de Tiempo Real

1. En admin, ir a **"Generar QR"**
2. Generar código QR para un estudiante
3. Escanear el QR con el móvil o simulador
4. **El mapa debe actualizarse INSTANTÁNEAMENTE** mostrando el espacio ocupado

### 5. Verificar Consola del Navegador (F12)

**ANTES (error):**
```
❌ Mixed Content: ws://... blocked
```

**DESPUÉS (correcto):**
```
✅ WebSocket connection to 'wss://smartparku-backend....' succeeded
```

---

## 🔍 DEBUGGING SI AÚN HAY PROBLEMAS

### Verificar Variables de Entorno

```powershell
az containerapp show `
  --name smartparku-frontend `
  --resource-group smartparku-rg `
  --query "properties.template.containers[0].env" `
  --output table
```

**Debe mostrar:**
```
Name                 Value
-------------------  ------------------------------------------
NEXT_PUBLIC_API_URL  https://smartparku-backend...
NEXT_PUBLIC_WS_URL   wss://smartparku-backend.../api/v1/parking/ws/parking
```

### Verificar que la Imagen es v3

```powershell
az containerapp show `
  --name smartparku-frontend `
  --resource-group smartparku-rg `
  --query "properties.template.containers[0].image" `
  --output tsv
```

**Debe mostrar:**
```
smartparkuacr.azurecr.io/smartparku-frontend:v3
```

### Verificar Logs del Backend (MQTT)

```powershell
az containerapp logs show `
  --name smartparku-backend `
  --resource-group smartparku-rg `
  --follow `
  --tail 50
```

**Buscar:**
```
MQTT conectado al broker HiveMQ
```

---

## 🏗️ ARQUITECTURA DE COMUNICACIÓN

```
┌─────────────────┐
│   Frontend      │
│   (Next.js)     │ HTTPS
│   Browser       │
└────────┬────────┘
         │
         │ WSS (WebSocket Secure)
         │ wss://smartparku-backend.../ws/parking
         │
         ▼
┌─────────────────┐
│   Backend       │
│   (FastAPI)     │
│   Azure         │
└────────┬────────┘
         │
         │ MQTT over TLS (port 8883)
         │
         ▼
┌─────────────────┐
│   HiveMQ Cloud  │
│   MQTT Broker   │
└─────────────────┘
         │
         │ MQTT
         │
         ▼
┌─────────────────┐
│  Raspberry Pi   │
│  (Simuladores)  │
└─────────────────┘
```

### Flujo de Actualización en Tiempo Real:

1. **Estudiante escanea QR** en entrada
2. **Backend procesa** y registra entrada en BD
3. **Backend actualiza** `parking_state` en memoria
4. **Backend broadcast** via WebSocket a todos los clientes conectados
5. **Frontend recibe** mensaje WebSocket
6. **ParkingStore actualiza** estado de Zustand
7. **ParkingMap re-renderiza** mostrando el espacio ocupado

---

## 🧪 CONFIGURACIÓN MQTT (Opcional - Solo si hay problemas)

Si el WebSocket conecta pero no hay actualizaciones, verificar MQTT:

### Variables de Entorno del Backend

```powershell
az containerapp show `
  --name smartparku-backend `
  --resource-group smartparku-rg `
  --query "properties.template.containers[0].env" `
  --output table
```

**Debe incluir:**
```
MQTT_BROKER=<tu-broker>.hivemq.cloud
MQTT_PORT=8883
MQTT_USERNAME=<usuario>
MQTT_PASSWORD=<password>
```

---

## 💰 IMPORTANTE: ELIMINACIÓN DE RECURSOS

**RECUERDA ELIMINAR TODO DESPUÉS DE PROBAR:**

```powershell
.\delete-all.ps1
.\verify-deleted.ps1
```

Costo estimado por sesión de 3 horas: **$0.30-0.40** (cubierto por créditos gratis)

---

## 📊 COMPARACIÓN: LOCAL vs AZURE

| Aspecto | Docker Local | Azure |
|---------|-------------|-------|
| **API Protocol** | `http://localhost:8000` | `https://...azurecontainerapps.io` |
| **WebSocket** | `ws://localhost:8000` | `wss://...azurecontainerapps.io` |
| **MQTT Broker** | Mosquitto (port 1883, no TLS) | HiveMQ Cloud (port 8883, TLS) |
| **CORS** | `localhost:3000` | `*` (cualquier origen) |

---

## 🎓 LECCIONES APRENDIDAS

1. **Next.js necesita variables en BUILD time**, no en runtime
2. **Azure Container Apps** usa HTTPS/WSS por defecto
3. **Mixed Content** bloquea conexiones inseguras desde páginas seguras
4. **Environment Variables** deben pasarse como `--build-arg` en Docker
5. **WebSocket en Azure** requiere `wss://`, no `ws://`

---

## 📞 SOPORTE

Si sigues teniendo problemas después de aplicar este fix:

1. Verifica que ejecutaste `redeploy-frontend-ws.ps1`
2. Revisa la consola del navegador (F12) para errores
3. Verifica logs del backend con `az containerapp logs show`
4. Asegúrate de que HiveMQ Cloud está configurado correctamente

---

**Fecha de Creación:** 2026-09-21  
**Versión:** 3.0 (WebSocket Fix)  
**Autor:** Kiro AI Assistant
