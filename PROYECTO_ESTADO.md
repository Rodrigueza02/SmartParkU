# SmartParkU — Documento de Estado del Proyecto
**Universidad Cooperativa de Colombia — Pasto · 2026**
**Última revisión: 18 de junio de 2026 (rama: feature/juliana-backend-10slots)**

---

## ¿De qué trata el proyecto?

SmartParkU es un sistema de gestión de parqueadero inteligente para la UCC Pasto. Combina hardware IoT (Raspberry Pi con sensores ultrasónicos HC-SR04 y un servo SG90 para la talanquera), comunicación MQTT en la nube (HiveMQ), un backend en FastAPI con PostgreSQL, y una interfaz web en Next.js que muestra el estado del parqueadero **en tiempo real**.

El flujo principal es:

```
Raspberry Pi (sensores HC-SR04)
        │
        │  MQTT sobre TLS (puerto 8883)
        ▼
  HiveMQ Cloud (broker)
        │
        │  paho-mqtt
        ▼
  Backend FastAPI  ◄──── PostgreSQL (datos persistentes)
        │
        │  WebSocket
        ▼
  Frontend Next.js (mapa en tiempo real)
        │
        │  (en desarrollo)
        ▼
  App móvil Flutter
```

**El estudiante puede:**
1. Iniciar sesión con correo y contraseña institucional
2. Ver el mapa del parqueadero en tiempo real
3. Generar un código QR para reservar un espacio
4. Mostrar el QR en la entrada → el sistema registra su ingreso y marca el cajón como ocupado
5. Registrar su salida del parqueadero (libera el espacio automáticamente)
6. Recuperar su contraseña si la olvida

**El administrador puede:**
1. Acceder al dashboard de administración
2. Ver el mapa en tiempo real
3. Controlar la talanquera (abrir/cerrar) desde la web
4. Ver el historial completo de accesos

---

## Estructura del repositorio

```
SmartParkU/
├── backend/                        ← FastAPI + MQTT + PostgreSQL
│   ├── app/
│   │   ├── api/                    ← Endpoints REST + guards JWT por rol
│   │   │   ├── auth.py             ← login, forgot-password, reset-password
│   │   │   ├── parking.py          ← estado, slots, servo (admin), WebSocket
│   │   │   ├── vehiculos.py        ← CRUD vehículos
│   │   │   ├── accesos.py          ← CRUD accesos + endpoint /salida
│   │   │   └── qr.py               ← generar QR, escanear QR
│   │   ├── core/
│   │   │   ├── security.py         ← JWT: get_current_user, require_roles, Bearer
│   │   │   └── config.py           ← Settings desde .env
│   │   ├── db/                     ← Sesión SQLAlchemy
│   │   ├── models/                 ← 4 tablas: Usuario, Vehiculo, EspacioParqueo, Acceso
│   │   ├── schemas/                ← Pydantic: request/response + auth forgot/reset
│   │   ├── services/               ← Lógica de negocio (incluye registrar_salida)
│   │   ├── repositories/           ← Acceso a datos
│   │   ├── utils/qr_utils.py       ← Firma HMAC-SHA256 para QR
│   │   ├── main.py                 ← Arranque + MQTT lifespan
│   │   ├── mqtt_client.py          ← Cliente MQTT + WebSocket broadcast
│   │   └── initial_data.py         ← Seed de usuarios y espacios
│   ├── alembic/versions/           ← 4 migraciones (todas idempotentes)
│   ├── simulador_raspberry.py      ← Simula la Raspberry Pi sin hardware
│   ├── test_pub.py                 ← Prueba rápida de publicación MQTT
│   ├── dashboard_mqtt.py           ← Monitor de mensajes MQTT en consola
│   ├── servo_control.py            ← Control manual de la talanquera por CLI
│   ├── .env                        ← Variables reales (NO subir a git)
│   └── requirements.txt
├── frontend/                       ← Next.js 14 + TypeScript + Tailwind CSS
│   └── src/
│       ├── app/
│       │   ├── page.tsx            ← Login (extrae id_usuario del response)
│       │   ├── dashboard/          ← Dashboard estudiante
│       │   ├── admin/dashboard/    ← Dashboard admin
│       │   ├── parking-map/        ← Mapa dedicado
│       │   └── comparison/         ← Página de comparación
│       ├── components/             ← ParkingMap, StudentDashboard, StudentProfile, etc.
│       └── store/
│           ├── authStore.ts        ← v2: persiste token + id_usuario en localStorage
│           └── parkingStore.ts     ← WebSocket + controlServo con Bearer token
├── mobile/                         ← Flutter (base funcional)
│   ├── pubspec.yaml                ← Dependencias: http, provider, mobile_scanner, etc.
│   └── lib/
│       ├── main.dart               ← AuthGate: splash → login / dashboard
│       ├── core/
│       │   ├── constants/api.dart  ← URLs del backend y WebSocket
│       │   ├── models/             ← UserModel, ParkingSlot
│       │   ├── services/           ← AuthService, ParkingService
│       │   └── providers/          ← AuthProvider, ParkingProvider
│       └── features/
│           ├── auth/presentation/  ← LoginPage, ForgotPasswordPage
│           └── parking/presentation/ ← StudentDashboardPage (mapa + QR + perfil)
└── PROYECTO_ESTADO.md              ← Este archivo
```

---

## Base de datos — Tablas

### `usuarios`
| Campo | Tipo | Notas |
|---|---|---|
| id_usuario | Integer PK | autoincrement |
| nombre | String(100) | |
| correo | String(100) | único, indexado |
| password | String(100) | hash bcrypt |
| rol | String(50) | `SuperAdmin` / `Administrativo` / `Estudiante` / `Visitante` |
| estado | String(50) | `Activo` / `Inactivo` |

### `espacios_parqueo`
| Campo | Tipo | Notas |
|---|---|---|
| id | Integer PK | |
| slot_id | String(20) | único — `slot_01` … `slot_10` |
| label | String(20) | `C-01`, `M-01`, `B-01`, `V-01`, etc. |
| tipo | String(20) | `carro` / `moto` / `bicicleta` / `vip` |
| status | String(20) | `libre` / `ocupado` |
| distancia_cm | Float | nullable, viene del sensor |
| updated_at | DateTime | se actualiza automáticamente |

Los 10 espacios fijos UCC Pasto: C-01, C-02, C-03, C-04 (carros) · M-01, M-02, M-03 (motos) · B-01, B-02 (bicicletas) · V-01 (VIP)

### `vehiculos`
| Campo | Tipo | Notas |
|---|---|---|
| id_vehiculo | Integer PK | |
| placa | String(20) | nullable |
| tipo | String(20) | carro / moto / bicicleta / vip |
| id_usuario | Integer FK → usuarios | nullable |

### `accesos`
| Campo | Tipo | Notas |
|---|---|---|
| id_acceso | Integer PK | |
| id_usuario | Integer FK → usuarios | nullable |
| id_vehiculo | Integer FK → vehiculos | nullable |
| id_espacio | Integer FK → espacios_parqueo | nullable |
| hora_entrada | DateTime | se pone al escanear el QR |
| hora_salida | DateTime | nullable — se pone al registrar la salida |
| metodo | String(50) | `qr` o manual |

---

## Migraciones Alembic (4 versiones — todas idempotentes)

| Versión | Archivo | Qué hace |
|---|---|---|
| `000000000001` | `20260609_0930_initial.py` | Crea `usuarios` y `espacios_parqueo` |
| `000000000002` | `20260610_1100_sync_indexes_fix_fk_accesos.py` | Agrega índices y corrige FK. **Ahora idempotente** con `IF NOT EXISTS` |
| `000000000003` | `20260618_1000_add_qr_metodo_index.py` | Índice en `accesos.metodo`. **Ahora condicional** |
| `000000000004` | `20260618_1200_create_vehiculos_accesos.py` | **NUEVA** — Crea `vehiculos` y `accesos` en entornos nuevos |

> Correr `alembic upgrade head` en un entorno limpio ahora funciona correctamente desde cero.

---

## API — Endpoints y autenticación

Base URL: `http://localhost:8000` · Docs: `http://localhost:8000/docs`

> **Todos los endpoints (excepto `/login`, `/forgot-password`, `/reset-password` y el WebSocket) requieren `Authorization: Bearer <token>` en el header.**

### Autenticación — sin token requerido
| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/v1/auth/login` | Login → JWT + nombre, rol, estado, **id_usuario** |
| POST | `/api/v1/auth/forgot-password` | Solicita reseteo de contraseña (token 30 min) |
| POST | `/api/v1/auth/reset-password` | Valida token y actualiza contraseña |

### Parqueadero — requiere token
| Método | Ruta | Roles | Descripción |
|---|---|---|---|
| GET | `/api/v1/parking/estado` | Cualquiera | Estado raw en memoria (MQTT) |
| GET | `/api/v1/parking/slots` | Cualquiera | BD + memoria mezclados |
| POST | `/api/v1/parking/servo?accion=abrir` | **Admin/SuperAdmin** | Abre la talanquera |
| POST | `/api/v1/parking/servo?accion=cerrar` | **Admin/SuperAdmin** | Cierra la talanquera |
| WS | `/api/v1/parking/ws/parking` | Público | Actualizaciones en tiempo real |

### Vehículos — requiere token
| Método | Ruta | Roles | Descripción |
|---|---|---|---|
| GET | `/api/v1/vehiculos/` | **Admin/SuperAdmin** | Lista todos |
| GET | `/api/v1/vehiculos/{id}` | Cualquiera | Por ID |
| GET | `/api/v1/vehiculos/usuario/{id_usuario}` | Cualquiera | Por usuario |
| POST | `/api/v1/vehiculos/` | Cualquiera | Crear vehículo |
| PUT | `/api/v1/vehiculos/{id}` | Cualquiera | Actualizar |
| DELETE | `/api/v1/vehiculos/{id}` | **Admin/SuperAdmin** | Eliminar |

### Accesos / Historial — requiere token
| Método | Ruta | Roles | Descripción |
|---|---|---|---|
| GET | `/api/v1/accesos/` | **Admin/SuperAdmin** | Lista todos los accesos |
| GET | `/api/v1/accesos/{id}` | Cualquiera | Por ID |
| GET | `/api/v1/accesos/usuario/{id_usuario}` | Cualquiera | Por usuario |
| GET | `/api/v1/accesos/vehiculo/{id_vehiculo}` | Cualquiera | Por vehículo |
| POST | `/api/v1/accesos/` | **Admin/SuperAdmin** | Crear manualmente |
| POST | `/api/v1/accesos/{id}/salida` | Cualquiera | **Registra salida + libera espacio** |
| PUT | `/api/v1/accesos/{id}` | **Admin/SuperAdmin** | Actualizar campos |
| DELETE | `/api/v1/accesos/{id}` | **Admin/SuperAdmin** | Eliminar |

### QR de acceso — requiere token
| Método | Ruta | Roles | Descripción |
|---|---|---|---|
| POST | `/api/v1/qr/generar` | Cualquier rol activo | QR firmado + PNG base64, válido 10 min |
| POST | `/api/v1/qr/escanear` | Cualquiera | Valida QR → ocupa espacio → crea acceso → broadcast WS |
| GET | `/api/v1/qr/acceso/{id_acceso}` | Cualquiera | Detalle del acceso creado |

### Cómo enviar el token (frontend / mobile)
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Flujo completo de entrada y salida

```
ENTRADA:
  Estudiante → POST /qr/generar → recibe imagen QR + qr_token
  Escaneo en entrada → POST /qr/escanear → espacio marcado "ocupado" → mapa actualizado

SALIDA:
  Estudiante (o admin) → POST /accesos/{id}/salida
    → hora_salida guardada en BD
    → EspacioParqueo.status = "libre"
    → update_slot_status() → broadcast WebSocket → mapa actualizado en tiempo real
```

---

## Tópicos MQTT

El backend **escucha** (publica la Raspberry Pi):

| Tópico | Payload | Qué hace |
|---|---|---|
| `sensores/ultrasonico` | `{"slot":"slot_01","distancia":8,"tipo":"carro","label":"C-01"}` | Actualiza status del cajón |
| `sensores/estado` | `{"slot":"slot_01","status":"ocupado","tipo":"carro"}` | Estado directo de un cajón |
| `parqueadero/entrada` | `{"libre": true}` | Estado de la barrera |
| `parqueadero/espacios` | `{"espacios":[...]}` | Actualización masiva |

**Umbral de los sensores:** `< 15 cm` → OCUPADO · `≥ 15 cm` → LIBRE · `> 400 cm` → ignorado (error)

El backend **publica** (recibe la Raspberry Pi):

| Tópico | Cuándo | Payload |
|---|---|---|
| `talanquera/control` | Al llamar `/parking/servo` | `{"angulo": 90, "accion": "abrir"}` |

---

## ⚠️ AVISO IMPORTANTE — Raspberry Pi

> **Helen, lee esto antes de tocar cualquier cosa relacionada con la Raspberry Pi o MQTT.**

La Raspberry Pi real está conectada al parqueadero físico. Publicar mensajes MQTT incorrectos puede abrir/cerrar la talanquera inesperadamente o confundir el estado del mapa.

**Para desarrollo y pruebas SIN hardware:**

```bash
# Desde la carpeta backend/, activa el venv primero:
venv\Scripts\activate      ← Windows

# Simulador completo (cambia estados cada 5 segundos):
python simulador_raspberry.py

# Monitor de todos los mensajes MQTT en consola:
python dashboard_mqtt.py

# Prueba rápida de 5 mensajes:
python test_pub.py

# Control manual de la talanquera:
python servo_control.py             # abre
python servo_control.py --cerrar    # cierra
```

**NUNCA ejecutes `simulador_raspberry.py` si la Raspberry real está conectada al broker.** Ambos publicarían al mismo tiempo y los estados se mezclarían.

El broker es **HiveMQ Cloud** (en internet). Credenciales en `backend/.env`. **No compartas ese archivo ni lo subas al repositorio.** El `.gitignore` ya lo excluye.

---

## Cómo arrancar el proyecto

### Prerrequisitos
- Python 3.11+
- Node.js 18+
- Flutter SDK 3.x (para la app móvil)
- PostgreSQL en `localhost:5432` con BD `smartparku` creada

### Backend

```bash
cd SmartParkU/backend

python -m venv venv
venv\Scripts\activate          # Windows

pip install -r requirements.txt

copy .env.example .env         # Editar con DATABASE_URL, SECRET_KEY, etc.

alembic upgrade head           # Crea las 4 tablas + índices
python app/initial_data.py     # Solo la primera vez (seed de usuarios y espacios)

uvicorn app.main:app --reload --port 8000
# → API en http://localhost:8000
# → Docs en http://localhost:8000/docs
```

### Frontend

```bash
cd SmartParkU/frontend

npm install
npm run dev
# → http://localhost:3000
```

### App móvil Flutter

```bash
cd SmartParkU/mobile

flutter pub get

# Emulador Android (apunta a 10.0.2.2 = localhost del host)
flutter run

# Dispositivo físico: editar lib/core/constants/api.dart
# Cambiar 10.0.2.2 por la IP de tu PC en la red local
```

### Usuarios de prueba

| Correo | Contraseña | Rol |
|---|---|---|
| admin@ucc.edu.co | admin123 | SuperAdmin |
| estudiante@ucc.edu.co | estudiante123 | Estudiante |
| admin.campus@ucc.edu.co | admincampus123 | Administrativo |
| visitante@gmail.com | visitante123 | Visitante |
| inactivo@ucc.edu.co | password123 | Estudiante (Inactivo) |

---

## Estado actual — ¿Qué está hecho? ¿Qué falta?

### ✅ Completado y funcionando

#### Backend
- JWT completo: login genera token, **todos los endpoints validan Bearer token**
- Guards por rol con `require_roles`: admins vs usuarios normales vs público
- **Flujo de salida**: `POST /accesos/{id}/salida` registra hora_salida, libera el espacio en BD y hace broadcast WebSocket al mapa
- **Forgot / Reset password**: dos endpoints funcionales con token de 30 min firmado con HMAC
- `TokenResponse` devuelve `id_usuario` para que el frontend lo guarde
- Sistema QR de punta a punta (genera imagen, firma HMAC-SHA256, valida, ocupa espacio, broadcast)
- Cliente MQTT HiveMQ Cloud con TLS y auto-reconexión
- WebSocket tiempo real con colas async y broadcast
- CRUD completo de vehículos y accesos
- **4 migraciones Alembic, todas idempotentes** — `alembic upgrade head` funciona en entorno nuevo
- Seeder con 5 usuarios + 10 espacios

#### Frontend
- Login con diseño UCC (azul `#1E3A5F`, cyan `#00AEEF`, verde `#6AB023`)
- Enrutamiento por rol: Estudiante → dashboard inline · Admin → `/admin/dashboard`
- `authStore v2`: persiste token + usuario + **id_usuario** en localStorage, invalida caché vieja automáticamente
- `parkingStore`: WebSocket con reconexión exponencial (3s→30s), fallback de 10 slots, **`controlServo` envía `Authorization: Bearer token`**
- URL del WebSocket corregida a `/api/v1/parking/ws/parking`
- Componentes: ParkingMap, StudentDashboard, StudentProfile, ParkingIllustration, UCCSwitch

#### App móvil Flutter
- `pubspec.yaml` con todas las dependencias (http, provider, shared_preferences, mobile_scanner, web_socket_channel)
- `main.dart` con `AuthGate`: splash → LoginPage / StudentDashboardPage según sesión guardada
- `LoginPage`: formulario completo con validación, mostrar/ocultar contraseña, botón "¿Olvidaste tu clave?"
- `ForgotPasswordPage`: llama al endpoint real del backend
- `StudentDashboardPage` con 3 pestañas:
  - **Mapa**: grilla de 10 cajones en tiempo real via WebSocket con reconexión automática
  - **Mi QR**: genera QR desde el backend, muestra imagen, escáner por cámara (`mobile_scanner`), confirmación de acceso
  - **Perfil**: datos del usuario + cerrar sesión
- `AuthService`, `ParkingService` (WebSocket + QR + salida), `AuthProvider`, `ParkingProvider`

---

### 🔄 Pendiente / Por terminar

| Qué | Estado | Quién | Notas |
|---|---|---|---|
| Dashboard admin web | 🔄 Parcial | Helen | La página `/admin/dashboard` existe. Conectar a los endpoints protegidos con token |
| Página `/comparison` | 🔄 Sin revisar | Helen | Existe en el frontend, contenido no revisado |
| "¿Olvidaste tu clave?" en el frontend web | ⚠️ Solo botón | Helen | El backend ya tiene los endpoints. Falta crear la UI en Next.js que llame a `/forgot-password` y `/reset-password` |
| Checkout / salida en el frontend web | ⚠️ Sin UI | Helen | El endpoint `POST /accesos/{id}/salida` ya existe. Falta botón en el dashboard del estudiante |
| App Flutter — admin dashboard | ❌ No iniciado | - | Solo existe el dashboard de estudiante. Falta vista para Admin/SuperAdmin |
| App Flutter — dispositivo físico | ⚠️ Pendiente config | - | Cambiar IP en `lib/core/constants/api.dart` de `10.0.2.2` a la IP real del servidor |
| Envío real de email (forgot password) | ⚠️ Pendiente | - | El backend genera el token pero lo devuelve en la respuesta en lugar de enviarlo por correo. Cuando haya servidor SMTP, descomentar la línea del email en `auth_service.py` |
| App Flutter — tests | ❌ No iniciado | - | No hay tests unitarios ni de widget |

---

## Dependencias principales

### Backend (`requirements.txt`)
```
fastapi>=0.115.0
uvicorn[standard]>=0.30.1
sqlalchemy>=2.0.35
psycopg[binary]>=3.2.1         ← driver PostgreSQL v3 (NO psycopg2)
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
bcrypt==4.0.1                   ← fijado para evitar incompatibilidades
pydantic[email]>=2.9.2
pydantic-settings>=2.5.2
paho-mqtt>=2.0.0                ← v2.x, usa CallbackAPIVersion.VERSION2
websockets>=12.0
qrcode[pil]>=7.4.2
alembic>=1.13.0
python-dotenv>=1.0.1
```

### Frontend (`package.json`)
```
next 14 (App Router)
react 18 + typescript
tailwindcss
zustand + persist middleware    ← estado global y localStorage
framer-motion                   ← animaciones
html5-qrcode                    ← escáner de cámara en el browser
lucide-react                    ← íconos
axios                           ← también disponible (se usa fetch nativo)
```

### App móvil Flutter (`pubspec.yaml`)
```yaml
http: ^1.2.1                    ← llamadas HTTP al backend
provider: ^6.1.2                ← gestión de estado
shared_preferences: ^2.3.2      ← sesión persistida (token JWT)
mobile_scanner: ^5.2.3          ← escáner QR por cámara
web_socket_channel: ^3.0.1      ← mapa en tiempo real
```

---

## Variables de entorno (`backend/.env`)

```env
# Base de datos
DATABASE_URL=postgresql+psycopg://usuario:password@localhost:5432/smartparku

# Seguridad JWT y QR
SECRET_KEY=una_clave_larga_y_aleatoria_minimo_32_caracteres
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# MQTT — HiveMQ Cloud
MQTT_BROKER=7de2fa1d05f84c5c8f2fcacca06d98da.s1.eu.hivemq.cloud
MQTT_PORT=8883
MQTT_USERNAME=Juliana
MQTT_PASSWORD=<la contraseña real — no la pongas aquí>
```

---

## Decisiones técnicas importantes

- **JWT Bearer en todos los endpoints**: `get_current_user` usa `HTTPBearer`. El token expira en 60 min. Para el reset de contraseña se genera un token separado con `"type": "reset"` que expira en 30 min.
- **require_roles**: fábrica de dependencias. `require_roles("SuperAdmin", "Administrativo")` bloquea con 403 a cualquier otro rol. Se puede combinar libremente en cualquier endpoint.
- **Flujo de salida**: `POST /accesos/{id}/salida` devuelve 409 si el acceso ya tiene `hora_salida`. Libera el espacio en BD y llama a `update_slot_status()` para que el mapa se actualice sin esperar al sensor.
- **paho-mqtt v2**: Usa `CallbackAPIVersion.VERSION2`. Si ves `TypeError` al conectar, hay incompatibilidad de versión del paho instalado.
- **simulador_raspberry.py usa API vieja de paho (v1)**: Funciona con warning en paho v2. Si falla, usa `test_pub.py` en su lugar.
- **Estado en memoria vs BD**: `parking_state` en `mqtt_client.py` es RAM viva actualizada por MQTT. La BD es la fuente de verdad persistente. `/parking/slots` mezcla ambos (RAM tiene prioridad para `status`).
- **HMAC para QR**: No es JWT, es HMAC-SHA256 con la misma `SECRET_KEY`. El payload va en base64 URL-safe. Cualquiera puede decodificarlo pero no puede falsificar la firma.
- **WebSocket con colas async**: cada cliente tiene su propia `asyncio.Queue(maxsize=20)`. El broadcast es `put_nowait` — si la cola está llena, el mensaje se descarta para no bloquear al MQTT.
- **authStore v2**: el nombre del storage cambió de `smartparku-auth` a `smartparku-auth-v2`. Esto invalida automáticamente cualquier sesión guardada con la versión vieja que no tuviera `id_usuario`.
- **Flutter IP**: en emulador Android usar `10.0.2.2` (apunta al localhost del host). En dispositivo físico o red real, cambiar por la IP de la máquina donde corre el backend (`lib/core/constants/api.dart`).

---

## Historial de cambios

| Fecha | Qué se hizo |
|---|---|
| 2026-06-09 | Migración inicial: tablas `usuarios` y `espacios_parqueo` |
| 2026-06-10 | Migración 2: índices faltantes + corrección FK `accesos → espacios_parqueo` |
| 2026-06-18 (mañana) | Migración 3: índice en `accesos.metodo`. Sistema QR completo |
| 2026-06-18 (tarde) | **JWT guards en todos los endpoints**, flujo de salida, forgot/reset password, migración 4 para `vehiculos` y `accesos`, Flutter base funcional, frontend authStore v2 + parkingStore corregido |
