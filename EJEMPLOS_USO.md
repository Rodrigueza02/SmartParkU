# 📖 Ejemplos de Uso - SmartParkU

## 🎬 Casos de Uso Implementados

### 1. Registro de Usuario Estudiante con Vehículo

**Flujo:**
```
1. Usuario abre la app en localhost:3001 o producción
2. Ve la pantalla de login
3. Hace clic en "Crear cuenta" (botón verde al final)
4. Completa el formulario:
   - Nombre: "Juan Pérez García"
   - Correo: "juan.perez@ucc.edu.co"
   - Documento: "1234567890" (opcional)
   - Contraseña: "miPassword123"
   - Rol: Selecciona "Estudiante" (ya está por defecto)
   - Tipo Vehículo: Selecciona "Motocicleta"
   - Placa: "ABC123"
5. Hace clic en "Crear Cuenta"
6. Backend crea:
   - Usuario con rol "Estudiante"
   - Vehículo tipo "moto" con placa "ABC123"
7. Mensaje de éxito y redirección a login
```

**Request Backend:**
```json
POST /api/v1/auth/register
{
  "nombre": "Juan Pérez García",
  "correo": "juan.perez@ucc.edu.co",
  "carnet_id": "1234567890",
  "password": "miPassword123",
  "rol": "Estudiante",
  "tipo_vehiculo": "moto",
  "placa_vehiculo": "ABC123"
}
```

**Response:**
```json
{
  "mensaje": "Cuenta creada exitosamente. Ya puedes iniciar sesión.",
  "id_usuario": 42,
  "correo": "juan.perez@ucc.edu.co",
  "rol": "Estudiante",
  "vehiculo_registrado": true
}
```

---

### 2. Registro de Docente sin Vehículo

**Flujo:**
```
1. Clic en "Crear cuenta"
2. Completa:
   - Nombre: "María González"
   - Correo: "maria.gonzalez@ucc.edu.co"
   - Contraseña: "docente2026"
   - Rol: Selecciona "Docente"
   - Tipo Vehículo: NO selecciona (deja en blanco)
3. Clic en "Crear Cuenta"
4. Backend crea solo el usuario
```

**Request:**
```json
POST /api/v1/auth/register
{
  "nombre": "María González",
  "correo": "maria.gonzalez@ucc.edu.co",
  "password": "docente2026",
  "rol": "Docente"
}
```

**Response:**
```json
{
  "mensaje": "Cuenta creada exitosamente. Ya puedes iniciar sesión.",
  "id_usuario": 43,
  "correo": "maria.gonzalez@ucc.edu.co",
  "rol": "Docente",
  "vehiculo_registrado": false
}
```

---

### 3. Generación de QR con Tipo de Vehículo

**Flujo:**
```
1. Usuario (Juan Pérez) inicia sesión
2. Ve el dashboard de estudiante
3. Navega a la pestaña "QR"
4. Ve el selector de tipo de vehículo
5. Selecciona "Motocicleta" (icono de Bike)
6. El botón "Generar QR de Ingreso" se activa
7. Hace clic
8. Backend busca un espacio tipo "moto" libre
9. Genera QR válido por 10 minutos
10. Muestra:
    - Badge: "M-01" (Motocicleta)
    - Imagen QR con animación de escaneo
    - Contador: 09:59, 09:58, 09:57...
```

**Request:**
```json
POST /api/v1/qr/generar
Authorization: Bearer {jwt_token}
{
  "id_usuario": 42,
  "tipo_vehiculo": "moto"
}
```

**Response:**
```json
{
  "espacio_id": 6,
  "slot_id": "slot_06",
  "label": "M-02",
  "tipo": "moto",
  "qr_token": "eyJhbGc...base64_encoded_token",
  "qr_image_base64": "data:image/png;base64,iVBORw0KG...",
  "expira_en": "2026-09-23T15:30:00Z",
  "mensaje": "QR generado para el espacio M-02. Escanéalo en la entrada. Válido por 10 minutos."
}
```

---

### 4. Generación de QR para Carro (sin espacios de carro disponibles)

**Flujo:**
```
1. Usuario selecciona "Carro"
2. Hace clic en "Generar QR"
3. Backend busca espacios tipo "carro"
4. NO encuentra espacios "carro" libres
5. Fallback: busca CUALQUIER espacio libre
6. Encuentra espacio tipo "moto" libre
7. Asigna ese espacio
8. Usuario recibe QR para espacio M-03
```

**Request:**
```json
POST /api/v1/qr/generar
{
  "id_usuario": 42,
  "tipo_vehiculo": "carro"
}
```

**Response:**
```json
{
  "espacio_id": 7,
  "slot_id": "slot_07",
  "label": "M-03",
  "tipo": "moto",  // ⚠️ Nota: asignó moto porque no había carro
  "qr_token": "...",
  "qr_image_base64": "...",
  "expira_en": "2026-09-23T15:30:00Z",
  "mensaje": "QR generado para el espacio M-03. Escanéalo en la entrada. Válido por 10 minutos."
}
```

---

### 5. Error: Generar QR sin Seleccionar Tipo

**Flujo:**
```
1. Usuario está en la pantalla de QR
2. NO selecciona ningún tipo de vehículo
3. Intenta hacer clic en "Generar QR de Ingreso"
4. El botón está DESACTIVADO (opacity: 40%, cursor: not-allowed)
5. No pasa nada
6. Usuario debe seleccionar un tipo primero
```

---

### 6. Error: Registro con Placa sin Tipo

**Flujo:**
```
1. Usuario completa el registro
2. NO selecciona tipo de vehículo
3. Ingresa placa "XYZ789"
4. Clic en "Crear Cuenta"
5. Frontend no envía la placa (validación local)
6. Se crea solo el usuario sin vehículo
```

---

### 7. Error: Registro con Tipo sin Placa

**Flujo:**
```
1. Usuario selecciona tipo "Bicicleta"
2. Campo "Placa del Vehículo" aparece
3. NO ingresa placa
4. Clic en "Crear Cuenta"
5. Frontend muestra error:
   "Si seleccionas un tipo de vehículo, debes ingresar la placa"
6. No envía el request
```

---

### 8. Registro VIP

**Flujo:**
```
1. Usuario crea cuenta
2. Selecciona rol "VIP"
3. Selecciona tipo vehículo "VIP"
4. Ingresa placa "VIP001"
5. Crea cuenta exitosamente
6. Al generar QR:
   - Selecciona tipo "VIP"
   - Backend busca espacios tipo "vip"
   - Asigna espacio V-01
```

**Request:**
```json
POST /api/v1/auth/register
{
  "nombre": "Carlos Empresario",
  "correo": "carlos@empresa.com",
  "password": "vip2026",
  "rol": "VIP",
  "tipo_vehiculo": "vip",
  "placa_vehiculo": "VIP001"
}
```

---

## 🎨 Ejemplos Visuales

### Selector de Tipo en QR

```
┌─────────────────────────────────────┐
│  [ 🚗 ]        [ 🏍️ ]              │
│   Carro      Motocicleta            │
│  (Azul)       (Verde)               │
│                                     │
│  [ 🚲 ]        [ 🚗 ]              │
│ Bicicleta       VIP                 │
│  (Lima)        (Navy)               │
└─────────────────────────────────────┘
```

### Selector de Rol en Registro

```
┌──────────────────────────────────────┐
│  [ 👤 ]    [ 💼 ]    [ 👥 ]        │
│ Estudiante Docente  Adminis.        │
│                                      │
│  [ 👤 ]    [ 💳 ]                  │
│ Invitado    VIP                     │
└──────────────────────────────────────┘
```

---

## 🔍 Queries SQL Generadas

### Registro con vehículo:

```sql
-- 1. Insertar usuario
INSERT INTO usuarios (nombre, correo, password, rol, estado, carnet_id)
VALUES ('Juan Pérez', 'juan.perez@ucc.edu.co', '$2b$12$...', 'Estudiante', 'Activo', '1234567890');

-- 2. Insertar vehículo
INSERT INTO vehiculos (placa, tipo, id_usuario)
VALUES ('ABC123', 'moto', 42);
```

### Generación de QR:

```sql
-- 1. Buscar espacio del tipo especificado
SELECT * FROM espacios_parqueo 
WHERE status = 'libre' AND tipo = 'moto'
LIMIT 1;

-- Si no encuentra:
SELECT * FROM espacios_parqueo 
WHERE status = 'libre'
LIMIT 1;
```

---

## 🧪 Casos de Prueba Recomendados

### ✅ Casos Positivos

1. ✅ Registro estudiante con carro
2. ✅ Registro docente con moto
3. ✅ Registro administrativo sin vehículo
4. ✅ Registro VIP con vehículo VIP
5. ✅ Generar QR con cada tipo de vehículo
6. ✅ Generar QR cuando hay espacios del tipo
7. ✅ Generar QR cuando NO hay del tipo (fallback)

### ⚠️ Casos Negativos

1. ❌ Registro con correo duplicado → Error 400
2. ❌ Registro con carnet duplicado → Error 400
3. ❌ Generar QR sin token → Error 401
4. ❌ Generar QR sin seleccionar tipo → Botón desactivado
5. ❌ Registro con tipo sin placa → Error frontend

---

## 📱 Compatibilidad

- ✅ Desktop: Chrome, Firefox, Safari, Edge
- ✅ Mobile: iOS Safari, Android Chrome
- ✅ Tablet: iPad, Android tablets
- ✅ Responsive: 320px - 2560px

---

## 🎯 Próximas Mejoras Sugeridas

1. **Múltiples vehículos por usuario**
   - Dropdown para seleccionar vehículo al generar QR
   - CRUD de vehículos en perfil

2. **Validación de placa inteligente**
   - Formato colombiano: ABC-123
   - Validar según tipo de vehículo

3. **Historial de accesos por vehículo**
   - Ver qué vehículo usé cada vez
   - Estadísticas por tipo

4. **Reserva de espacios**
   - Reservar espacio con anticipación
   - Notificación cuando expire la reserva
