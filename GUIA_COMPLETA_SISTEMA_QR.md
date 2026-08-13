# 📱 GUÍA COMPLETA DEL SISTEMA QR - SmartParkU

## 📑 ÍNDICE
1. [¿Cómo funciona el sistema de QR?](#cómo-funciona-el-sistema-de-qr)
2. [Arquitectura técnica](#arquitectura-técnica)
3. [Flujo completo del usuario](#flujo-completo-del-usuario)
4. [Componentes del sistema](#componentes-del-sistema)
5. [Paso a paso para probar](#paso-a-paso-para-probar)
6. [Solución de problemas](#solución-de-problemas)

---

## 🎯 ¿CÓMO FUNCIONA EL SISTEMA DE QR?

El sistema de QR de SmartParkU permite a los estudiantes **generar un código QR temporal** que les asigna un espacio de parqueadero. Luego, al llegar a la entrada física del campus, **escanean ese QR** para confirmar su ingreso y ocupar el espacio.

### **Flujo simplificado:**

```
1. ESTUDIANTE → Genera QR desde la app
   ↓
2. BACKEND → Busca primer espacio libre y crea QR firmado (válido 10 min)
   ↓
3. ESTUDIANTE → Recibe imagen QR en su celular
   ↓
4. ESTUDIANTE → Llega a la entrada del parqueadero
   ↓
5. LECTOR/APP → Escanea el QR con la cámara
   ↓
6. BACKEND → Valida firma, verifica expiración, marca espacio como ocupado
   ↓
7. SISTEMA → Crea registro de acceso y actualiza mapa en tiempo real
   ↓
8. ✅ ESTUDIANTE → Ingresa al parqueadero en el espacio asignado
```

---

## 🏗️ ARQUITECTURA TÉCNICA

### **1. Backend (Python/FastAPI)**

#### **Endpoints principales:**

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/v1/qr/generar` | Genera un QR firmado y asigna espacio temporalmente |
| `POST` | `/api/v1/qr/escanear` | Valida el QR, crea acceso y marca espacio ocupado |
| `GET` | `/api/v1/qr/acceso/{id}` | Consulta detalles de un acceso registrado |

#### **Componentes clave:**

**📄 `backend/app/api/qr.py`**
- Define los endpoints REST
- Maneja permisos (estudiantes, visitantes, admins pueden generar QR)
- Cualquier usuario autenticado puede escanear

**📄 `backend/app/services/qr_service.py`**
- **`generar_qr()`**: 
  - Busca el primer espacio libre en la BD
  - Crea payload con: `espacio_id`, `id_usuario`, `timestamp`, `expira_en`
  - Firma el payload con HMAC-SHA256 usando SECRET_KEY
  - Genera imagen PNG del QR en base64
  - **No reserva el espacio todavía** (solo al escanear)
  
- **`escanear_qr()`**:
  - Decodifica el token del QR escaneado
  - Verifica firma HMAC (detecta manipulación)
  - Verifica que no haya expirado (10 minutos)
  - Verifica que el espacio siga libre
  - **Marca el espacio como "ocupado"**
  - **Crea registro en tabla `accesos`**
  - Actualiza mapa en tiempo real vía WebSocket

**📄 `backend/app/utils/qr_utils.py`**
- **`sign_qr_payload()`**: Firma el dict con HMAC-SHA256
- **`decode_qr_payload()`**: Decodifica base64 del QR
- **`verify_qr_signature()`**: Valida integridad del QR

**📄 `backend/app/schemas/qr.py`**
- Define los modelos Pydantic para request/response
- `QRGenerarRequest`: `{ id_usuario, id_vehiculo? }`
- `QRGeneradoResponse`: `{ espacio_id, qr_token, qr_image_base64, expira_en, ... }`
- `QREscanearRequest`: `{ qr_token }`
- `QREscanearResponse`: `{ acceso_id, label, hora_entrada, ... }`

---

### **2. Frontend Web (Next.js/React)**

#### **Componentes principales:**

**📄 `frontend/src/components/QRAcceso.tsx`**
- Componente principal con **3 pantallas**:
  1. **Generar QR**: Botón para solicitar QR → muestra imagen con cuenta regresiva
  2. **Escanear con cámara**: Usa `html5-qrcode` para leer QR con cámara del dispositivo
  3. **Confirmación**: Muestra espacio asignado, hora de entrada, mensaje de éxito

- **Tabs**: Alterna entre "Generar QR" y "Escanear QR"
- **Botón de prueba**: "Simular escaneo en entrada" (solo visible en PC para testing sin cámara)

**📄 `frontend/src/components/QRScanner.tsx`**
- Wrapper de `html5-qrcode` library
- Activa cámara trasera del dispositivo
- Detecta QR automáticamente
- Se carga dinámicamente (no SSR) para evitar errores

**📄 `frontend/src/store/qrStore.ts`**
- Estado global con Zustand
- Maneja todos los steps del flujo QR
- Funciones:
  - `generarQR()`: Llama POST `/qr/generar`
  - `escanearQR()`: Llama POST `/qr/escanear`
  - `tickTimer()`: Cuenta regresiva de 10 minutos
  - `reset()`: Reinicia el flujo

---

### **3. Mobile (Flutter/Dart)**

#### **Componentes principales:**

**📄 `mobile/lib/features/parking/presentation/student_dashboard_page.dart`**
- Pestaña "Mi QR" con **3 estados**:
  1. **Inicial**: Botones "Generar mi QR" y "Escanear QR existente"
  2. **QR generado**: Muestra imagen del QR, botón para escanear
  3. **Acceso confirmado**: Muestra espacio asignado con ícono de éxito

**📄 `mobile/lib/core/providers/parking_provider.dart`**
- Funciones:
  - `generarQR()`: Llama al service
  - `escanearQR()`: Llama al service
  
**📄 `mobile/lib/core/services/parking_service.dart`**
- Hace las peticiones HTTP a los endpoints del backend
- Maneja autenticación JWT

**📄 Librería usada:** `mobile_scanner: ^5.2.3`
- Escáner nativo de QR para Android/iOS
- Activa cámara trasera automáticamente

---

## 🔄 FLUJO COMPLETO DEL USUARIO

### **ESCENARIO 1: Usuario genera QR y lo escanea él mismo**

```
┌─────────────────────────────────────────────────────────────┐
│ PASO 1: GENERAR QR                                          │
└─────────────────────────────────────────────────────────────┘
  App → POST /api/v1/qr/generar
       { "id_usuario": 1, "id_vehiculo": 2 }
  
  Backend:
    1. Verifica que usuario existe
    2. Obtiene tipo de vehículo (ej: "carro")
    3. Busca primer espacio libre de tipo "carro" (ej: C-01)
    4. Crea payload:
       {
         "espacio_id": 3,
         "slot_id": "C-01",
         "id_usuario": 1,
         "id_vehiculo": 2,
         "emitido_en": "2026-06-18T14:30:00Z",
         "expira_en": "2026-06-18T14:40:00Z"
       }
    5. Firma payload con HMAC-SHA256
    6. Genera imagen QR PNG en base64
    7. Devuelve respuesta
  
  App recibe:
    ✅ Imagen QR (data:image/png;base64,...)
    ✅ Token firmado (para validar después)
    ✅ Espacio asignado: "C-01"
    ✅ Expira en: 10 minutos

┌─────────────────────────────────────────────────────────────┐
│ PASO 2: ESTUDIANTE LLEGA A LA ENTRADA (5 minutos después)  │
└─────────────────────────────────────────────────────────────┘
  
  App → Abre pestaña "Escanear QR"
       → Activa cámara trasera
       → Apunta a su propio QR
       → Lee el token: "eyJlc3BhY2lvX2lkIjozLCAic2lnb..."

┌─────────────────────────────────────────────────────────────┐
│ PASO 3: VALIDAR Y REGISTRAR ACCESO                         │
└─────────────────────────────────────────────────────────────┘
  App → POST /api/v1/qr/escanear
       { "qr_token": "eyJlc3BhY2lvX2lkIjozLCAic2lnb..." }
  
  Backend:
    1. Decodifica el token base64
    2. Extrae signature y payload
    3. ✅ Verifica firma HMAC (detecta manipulación)
    4. ✅ Verifica expiración (5 min < 10 min → OK)
    5. ✅ Verifica que espacio C-01 siga "libre"
    6. 🔒 Marca espacio C-01 como "ocupado"
    7. 📝 Crea registro en tabla accesos:
       INSERT INTO accesos 
         (id_usuario, id_vehiculo, id_espacio, hora_entrada, metodo)
       VALUES 
         (1, 2, 3, '2026-06-18T14:35:00', 'qr')
    8. 🔄 Actualiza mapa en tiempo real (WebSocket broadcast)
    9. Devuelve respuesta de éxito
  
  App recibe:
    ✅ acceso_id: 42
    ✅ label: "C-01"
    ✅ hora_entrada: "14:35:00"
    ✅ mensaje: "✅ Acceso registrado. Espacio C-01 asignado."

┌─────────────────────────────────────────────────────────────┐
│ PASO 4: CONFIRMACIÓN                                        │
└─────────────────────────────────────────────────────────────┘
  App muestra:
    🎉 "¡Bienvenido al campus!"
    🅿️ Espacio: C-01
    🕐 Hora: 14:35:00
    
  Mapa en tiempo real:
    → Todos los usuarios ven C-01 en ROJO (ocupado)
```

---

### **ESCENARIO 2: QR expira antes de escanear**

```
PASO 1: Usuario genera QR → expira_en: 14:40:00
PASO 2: Usuario se distrae, llega a las 14:45:00 (pasaron 15 minutos)
PASO 3: Intenta escanear

Backend responde:
  ❌ HTTP 410 Gone
  ❌ "El QR ha expirado. Solicita uno nuevo."

App muestra:
  🔴 Pantalla de error
  💡 "El QR expiró. Genera uno nuevo para ingresar."
  🔄 Botón "Generar nuevo QR"
```

---

### **ESCENARIO 3: Espacio ya fue ocupado por otro estudiante**

```
PASO 1: Estudiante A genera QR para C-01 a las 14:30
PASO 2: Estudiante B genera QR para C-01 a las 14:32 (mismo espacio)
PASO 3: Estudiante B escanea primero a las 14:35
        → ✅ Backend marca C-01 como ocupado para B
PASO 4: Estudiante A intenta escanear a las 14:36

Backend responde:
  ❌ HTTP 409 Conflict
  ❌ "El espacio C-01 ya está ocupado."

App muestra:
  🟠 Pantalla de error
  💡 "Otro estudiante tomó ese espacio. Genera un QR nuevo."
  🔄 Botón "Generar nuevo QR"
```

---

## 🧩 COMPONENTES DEL SISTEMA

### **Seguridad: HMAC-SHA256**

El QR contiene un token firmado que **no puede ser manipulado**:

```python
# Ejemplo de payload firmado
payload_original = {
  "espacio_id": 3,
  "id_usuario": 1,
  "expira_en": "2026-06-18T14:40:00Z"
}

# Backend firma con SECRET_KEY
json_str = json.dumps(payload_original)
signature = hmac.sha256(SECRET_KEY, json_str).hexdigest()

payload_con_firma = {
  ...payload_original,
  "signature": "a7f8b2c3d4e5..."
}

qr_token = base64_encode(payload_con_firma)
# → "eyJlc3BhY2lvX2lkIjozLC..."
```

Si alguien intenta modificar el QR (ej: cambiar `espacio_id` de 3 a 1):
- ❌ La firma ya no coincide
- ❌ Backend rechaza con HTTP 401: "QR inválido o manipulado"

---

### **Expiración: 10 minutos**

```python
QR_EXPIRE_MINUTES = 10

# Al generar
now_utc = datetime.now(timezone.utc)
expira_en = now_utc + timedelta(minutes=10)

# Al escanear
if datetime.now(timezone.utc) > expira_en:
    raise HTTPException(410, "El QR ha expirado")
```

---

### **Actualización en tiempo real**

Cuando se escanea un QR exitosamente:

```python
# services/qr_service.py
from app.mqtt_client import update_slot_status

# Después de crear acceso...
update_slot_status(espacio.slot_id, "ocupado")
```

Esto hace un **broadcast WebSocket** a todos los clientes conectados:
- Frontend Web actualiza el mapa instantáneamente
- Mobile actualiza la grilla de cajones
- Dashboard admin ve el cambio en vivo

---

## ✅ PASO A PASO PARA PROBAR

### **PREREQUISITOS**

Antes de empezar, asegúrate de tener:

```bash
✅ Backend corriendo en http://localhost:8000
✅ Frontend corriendo en http://localhost:3001 (o mobile app instalada)
✅ Base de datos con usuarios y espacios creados (ver INSTRUCCIONES_PRUEBA.md)
```

---

### **🌐 OPCIÓN A: PROBAR DESDE EL FRONTEND WEB**

#### **Paso 1: Login**
```
1. Abre http://localhost:3001
2. Login con: estudiante@ucc.edu.co / estudiante123
3. Verás el dashboard del estudiante
```

#### **Paso 2: Acceder a la pantalla de QR**
```
El componente QRAcceso puede estar integrado en:
- Una pestaña del dashboard
- Un modal
- Una ruta dedicada (ej: /dashboard/qr)

Para probarlo, necesitas que esté renderizado en alguna parte.
Si no está visible, puedes agregarlo temporalmente al dashboard.
```

#### **Paso 3: Generar QR**
```
1. Click en tab "GENERAR QR"
2. Click en botón "Generar QR de Ingreso"
3. Espera 1-2 segundos (loading)
4. ✅ Verás:
   - Badge con espacio asignado (ej: "C-01 - Carro")
   - Imagen QR con animación de línea de escaneo
   - Cuenta regresiva: "10:00" → "09:59" → ...
```

#### **Paso 4: Simular escaneo desde PC (sin cámara)**
```
1. Verás un botón "Simular escaneo en entrada"
2. Click en ese botón
3. El sistema llama automáticamente a /qr/escanear con el token
4. ✅ Verás pantalla de confirmación:
   - ✅ "¡Bienvenido al campus!"
   - 🅿️ Espacio: C-01
   - 🕐 Hora de entrada
```

#### **Paso 5: Verificar en el mapa**
```
1. Abre otra pestaña del navegador
2. Login con admin@ucc.edu.co / admin123
3. Ve al dashboard admin
4. ✅ Deberías ver C-01 marcado como OCUPADO (rojo)
```

---

### **📱 OPCIÓN B: PROBAR DESDE LA APP MÓVIL (Flutter)**

#### **Paso 1: Instalar la app**
```bash
# Desde la carpeta mobile/
flutter pub get
flutter run
```

#### **Paso 2: Login**
```
1. Abre la app en tu dispositivo Android/iOS
2. Login con: estudiante@ucc.edu.co / estudiante123
3. Verás 3 tabs: Mapa | Mi QR | Perfil
```

#### **Paso 3: Generar QR**
```
1. Tap en tab "Mi QR" (ícono QR code)
2. Tap en "Generar mi QR"
3. ✅ La app muestra:
   - Card con la imagen QR
   - "Espacio asignado: C-01"
   - Mensaje con tiempo de validez
```

#### **Paso 4: Escanear con cámara**
```
OPCIÓN 4A: Escanear tu propio QR (necesitas otro dispositivo)
   1. Toma screenshot del QR generado
   2. Ábrelo en otro celular o muéstralo en la pantalla de PC
   3. En la app, tap "Escanear QR en la entrada"
   4. Apunta la cámara al QR
   5. ✅ Se detecta automáticamente

OPCIÓN 4B: Generar QR desde web y escanear desde mobile
   1. Genera QR en http://localhost:3001 desde PC
   2. Muestra el QR en la pantalla
   3. En la app móvil, tap "Escanear QR existente"
   4. Apunta la cámara del celular al QR en la pantalla de PC
   5. ✅ Se detecta automáticamente
```

#### **Paso 5: Ver confirmación**
```
✅ La app muestra:
   - ✅ Ícono de check verde
   - Label del espacio (C-01)
   - "✅ Acceso registrado. Espacio C-01 asignado correctamente."
   - Botón "Nuevo acceso" para reiniciar
```

#### **Paso 6: Verificar en el mapa**
```
1. En la misma app, tap en tab "Mapa"
2. ✅ Deberías ver el cajón C-01 en ROJO (ocupado)
3. El contador de "Ocupados" se incrementó en 1
```

---

### **🧪 PROBAR ESCENARIOS DE ERROR**

#### **Test 1: QR expirado**
```
1. Genera un QR
2. ESPERA 11 minutos (o cambia QR_EXPIRE_MINUTES a 1 en qr_service.py)
3. Intenta escanearlo
4. ✅ Debería mostrar:
   - ❌ "QR Expirado"
   - 💡 "El QR ha expirado. Solicita uno nuevo."
   - 🔄 Botón "Generar nuevo QR"
```

#### **Test 2: Espacio ocupado (race condition)**
```
1. Abre 2 navegadores/dispositivos diferentes
2. Login con 2 usuarios distintos en cada uno
3. Genera QR en AMBOS al mismo tiempo
   → Ambos obtendrán el mismo espacio (C-01)
4. Escanea en el primer dispositivo
   → ✅ Éxito, C-01 queda ocupado
5. Intenta escanear en el segundo dispositivo
   → ❌ Error 409: "El espacio C-01 ya está ocupado"
```

#### **Test 3: QR manipulado**
```
1. Genera un QR y copia el qr_token
2. Modifica manualmente el token (cambia algún carácter)
3. Intenta escanearlo con el token modificado
4. ✅ Debería mostrar:
   - ❌ "QR inválido o manipulado — la firma no coincide"
   - HTTP 401 Unauthorized
```

---

### **🔍 VERIFICAR CON LAS HERRAMIENTAS DE DESARROLLO**

#### **1. Ver las peticiones HTTP**

Abre DevTools (F12) → Network:

```
POST /api/v1/qr/generar
  Request: { "id_usuario": 1, "id_vehiculo": 2 }
  Response: {
    "espacio_id": 3,
    "slot_id": "C-01",
    "label": "C-01",
    "tipo": "carro",
    "qr_token": "eyJlc3BhY2lv...",
    "qr_image_base64": "data:image/png;base64,...",
    "expira_en": "2026-06-18T14:40:00Z",
    "mensaje": "QR generado para el espacio C-01..."
  }

POST /api/v1/qr/escanear
  Request: { "qr_token": "eyJlc3BhY2lv..." }
  Response: {
    "acceso_id": 42,
    "id_usuario": 1,
    "id_vehiculo": 2,
    "espacio_id": 3,
    "slot_id": "C-01",
    "label": "C-01",
    "hora_entrada": "2026-06-18T14:35:00",
    "mensaje": "✅ Acceso registrado. Espacio C-01 asignado."
  }
```

#### **2. Ver WebSocket en tiempo real**

DevTools → Network → WS:

```
ws://localhost:8000/ws/parking

Mensaje recibido después de escanear:
{
  "C-01": "ocupado",
  "C-02": "libre",
  "C-03": "libre",
  ...
}
```

#### **3. Verificar en la base de datos**

```bash
# Si usas SQLite
sqlite3 backend/smartparku.db

# O si usas PostgreSQL
psql -d smartparku
```

```sql
-- Ver espacios ocupados
SELECT * FROM espacios_parqueo WHERE status = 'ocupado';

-- Ver accesos registrados por QR
SELECT * FROM accesos WHERE metodo = 'qr' ORDER BY hora_entrada DESC;

-- Resultado esperado:
-- id_acceso | id_usuario | id_vehiculo | id_espacio | hora_entrada        | metodo
-- 42        | 1          | 2           | 3          | 2026-06-18 14:35:00 | qr
```

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### **❌ Error: "No hay espacios disponibles"**

**Causa:** Todos los espacios están ocupados en la BD.

**Solución:**
```bash
# Opción 1: Liberar todos los espacios
sqlite3 backend/smartparku.db
UPDATE espacios_parqueo SET status = 'libre';

# Opción 2: Recrear la base de datos
cd backend
rm smartparku.db
python seed_users.py
```

---

### **❌ Error: "QR inválido o manipulado"**

**Causa:** El SECRET_KEY del backend no coincide entre generar y escanear.

**Verificar:**
```bash
# backend/.env
SECRET_KEY=smartparku_secret_key_2024_super_segura_cambiar_en_produccion
```

**Solución:**
1. Asegúrate de que el archivo `.env` existe
2. Reinicia el backend: `uvicorn main:app --reload`
3. Genera un QR nuevo

---

### **❌ Error: Cámara no funciona en la app móvil**

**Causa:** Permisos de cámara no otorgados.

**Solución Android:**
```xml
<!-- mobile/android/app/src/main/AndroidManifest.xml -->
<uses-permission android:name="android.permission.CAMERA" />
```

**Solución iOS:**
```xml
<!-- mobile/ios/Runner/Info.plist -->
<key>NSCameraUsageDescription</key>
<string>SmartParkU necesita acceso a la cámara para escanear códigos QR</string>
```

Reinstalar la app:
```bash
flutter clean
flutter pub get
flutter run
```

---

### **❌ Error: El mapa no se actualiza en tiempo real**

**Causa:** WebSocket no está conectado.

**Verificar:**
```javascript
// DevTools → Console
const ws = new WebSocket('ws://localhost:8000/ws/parking');
ws.onopen = () => console.log('✅ Conectado');
ws.onerror = (e) => console.error('❌ Error:', e);
```

**Solución:**
1. Verifica que el backend esté corriendo
2. Revisa que no haya firewall bloqueando WebSocket
3. En mobile, verifica que `parking.connect(token)` se llame en `initState`

---

### **❌ Error: "Failed to decode image" en Flutter**

**Causa:** El base64 del QR está mal formateado.

**Solución:**
```dart
// Quitar el prefijo data:image/png;base64,
final b64 = (qrData['qr_image_base64'] as String?)
    ?.replaceFirst('data:image/png;base64,', '');

Image.memory(base64Decode(b64))
```

---

## 📊 CHECKLIST FINAL DE PRUEBAS

### ✅ Funcionalidades básicas
- [ ] Generar QR desde frontend web
- [ ] Generar QR desde app móvil
- [ ] Imagen QR se muestra correctamente
- [ ] Cuenta regresiva funciona (10 min → 0)
- [ ] Escanear con cámara desde web (si hay cámara)
- [ ] Escanear con cámara desde mobile
- [ ] Botón "Simular escaneo" funciona en web
- [ ] Pantalla de confirmación muestra espacio correcto
- [ ] Hora de entrada se registra correctamente

### ✅ Seguridad
- [ ] QR expirado (>10 min) es rechazado con HTTP 410
- [ ] QR manipulado es rechazado con HTTP 401
- [ ] Espacio ocupado por otro es rechazado con HTTP 409
- [ ] Firma HMAC se valida correctamente

### ✅ Integración
- [ ] Espacio se marca como ocupado en la BD
- [ ] Registro se crea en tabla `accesos`
- [ ] Mapa en tiempo real se actualiza (WebSocket)
- [ ] Otros usuarios ven el cajón ocupado inmediatamente

### ✅ Manejo de errores
- [ ] Pantalla de error muestra mensaje claro
- [ ] Botón "Generar nuevo QR" reinicia el flujo
- [ ] Errores HTTP se mapean a mensajes amigables
- [ ] Cámara no disponible muestra mensaje de error

---

## 🎯 PRÓXIMOS PASOS DESPUÉS DE LAS PRUEBAS

Una vez que todo funcione correctamente:

### **1. Registro de salida**
Implementar el flujo de salida:
```
POST /api/v1/qr/salida
- Escanear QR al salir
- Marcar espacio como libre
- Registrar hora_salida en accesos
- Calcular tiempo de permanencia
```

### **2. Historial de accesos**
```
GET /api/v1/accesos/usuario/{id}
- Ver historial de entradas/salidas
- Estadísticas de uso
- CO₂ ahorrado por usar bicicleta
```

### **3. Notificaciones push**
```
- QR próximo a expirar (2 min antes)
- Espacio asignado exitosamente
- Recordatorio de salida (después de X horas)
```

### **4. Lector físico en la entrada**
```
- Raspberry Pi con cámara
- Lee QR automáticamente
- LED verde = acceso OK
- LED rojo = acceso denegado
- Pantalla LCD con mensaje
```

---

## 📞 SOPORTE

Si tienes problemas:

1. Revisa los logs del backend:
   ```bash
   cd backend
   uvicorn main:app --reload
   # Ver errores en la consola
   ```

2. Revisa la documentación interactiva:
   ```
   http://localhost:8000/docs
   ```

3. Verifica la configuración:
   ```bash
   cat backend/.env
   ```

---

**¡Listo para probar! 🚀**

Si encuentras algún error o tienes dudas, revisa la sección de "Solución de problemas" arriba.
