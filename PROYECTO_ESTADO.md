# SmartParkU — Documento de Estado del Proyecto
**Universidad Cooperativa de Colombia — Pasto · 2026**
**Última revisión: 18 de junio de 2026**

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
```

El estudiante puede:
1. Iniciar sesión con correo y contraseña institucional
2. Ver el mapa del parqueadero en tiempo real (qué cajones están libres u ocupados)
3. Generar un código QR para reservar un espacio
4. Mostrar el QR en la entrada física → el sistema registra su ingreso y marca el cajón como ocupado

El administrador puede:
1. Acceder al dashboard de administración
2. Ver el mapa en tiempo real
3. Controlar la talanquera (abrir/cerrar) desde la web

---

## Estructura del repositorio

```
SmartParkU/
├── backend/                  ← FastAPI + MQTT + PostgreSQL
│   ├── app/
│   │   ├── api/              ← Endpoints REST (auth, parking, vehiculos, accesos, qr)
│   │   ├── core/             ← Configuración, seguridad JWT
│   │   ├── db/               ← Sesión y base SQLAlchemy
│   │   ├── models/           ← Tablas de la BD (4 modelos)
│   │   ├── schemas/          ← Validación Pydantic (request/response)
│   │   ├── services/         ← Lógica de negocio
│   │   ├── repositories/     ← Acceso a datos
│   │   ├── utils/            ← Utilidades (firma HMAC para QR)
│   │   ├── main.py           ← Arranque de la app + MQTT
│   │   ├── mqtt_client.py    ← Cliente MQTT en tiempo real + WebSocket broadcast
│   │   └── initial_data.py   ← Seed de usuarios y espacios
│   ├── alembic/              ← Migraciones de base de datos (3 versiones)
│   ├── simulador_raspberry.py← Simula la Raspberry Pi (usar sin hardware)
│   ├── test_pub.py           ← Prueba rápida de publicación MQTT
│   ├── dashboard_mqtt.py     ← Monitor de mensajes MQTT en consola
│   ├── servo_control.py      ← Control manual de la talanquera por CLI
│   ├── .env                  ← Variables de entorno reales (NO subir a git)
│   └── requirements.txt
├── frontend/                 ← Next.js 14 + TypeScript + Tailwind
│   └── src/
│       ├── app/              ← Páginas (App Router)
│       │   ├── page.tsx      ← Login
│       │   ├── dashboard/    ← Dashboard estudiante
│       │   ├── admin/dashboard/ ← Dashboard admin
│       │   ├── parking-map/  ← Mapa dedicado
│       │   └── comparison/   ← Página de comparación
│       ├── components/       ← Componentes React
│       └── store/            ← Estado global Zustand
└── mobile/                   ← Flutter (solo esqueleto, sin funcionalidad)
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

Los 10 espacios fijos son:
- C-01, C-02, C-03, C-04 → carros
- M-01, M-02, M-03 → motos
- B-01, B-02 → bicicletas
- V-01 → VIP

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
| hora_salida | DateTime | nullable — flujo de salida pendiente |
| metodo | String(50) | `qr` o manual |

---

## API — Endpoints disponibles

Base URL: `http://localhost:8000`

### Autenticación
| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/v1/auth/login` | Login → devuelve JWT + datos del usuario |

### Parqueadero / Tiempo real
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/v1/parking/estado` | Estado raw en memoria (actualizado por MQTT) |
| GET | `/api/v1/parking/slots` | Estado mezclado BD + memoria |
| POST | `/api/v1/parking/servo?accion=abrir` | Abre la talanquera |
| POST | `/api/v1/parking/servo?accion=cerrar` | Cierra la talanquera |
| WS | `/api/v1/parking/ws/parking` | WebSocket — recibe actualizaciones en tiempo real |

### Vehículos
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/v1/vehiculos/` | Lista todos |
| GET | `/api/v1/vehiculos/{id}` | Por ID |
| GET | `/api/v1/vehiculos/usuario/{id_usuario}` | Por usuario |
| POST | `/api/v1/vehiculos/` | Crear vehículo |
| PUT | `/api/v1/vehiculos/{id}` | Actualizar |
| DELETE | `/api/v1/vehiculos/{id}` | Eliminar |

### Accesos / Historial
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/v1/accesos/` | Lista todos |
| GET | `/api/v1/accesos/{id}` | Por ID |
| GET | `/api/v1/accesos/usuario/{id_usuario}` | Por usuario |
| GET | `/api/v1/accesos/vehiculo/{id_vehiculo}` | Por vehículo |
| POST | `/api/v1/accesos/` | Crear manualmente |
| PUT | `/api/v1/accesos/{id}` | Actualizar (incluye `hora_salida`) |
| DELETE | `/api/v1/accesos/{id}` | Eliminar |

### QR de acceso
| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/v1/qr/generar` | Genera QR firmado + imagen PNG base64, válido 10 min |
| POST | `/api/v1/qr/escanear` | Valida QR → marca espacio ocupado → crea acceso → notifica WebSocket |
| GET | `/api/v1/qr/acceso/{id_acceso}` | Consulta acceso creado por QR |

La documentación interactiva completa está en **`http://localhost:8000/docs`** (Swagger UI) cuando el backend está corriendo.

---

## Tópicos MQTT

El backend **escucha** estos tópicos (los publica la Raspberry Pi):

| Tópico | Qué envía la Raspberry | Ejemplo de payload |
|---|---|---|
| `sensores/ultrasonico` | Lectura de un sensor para un cajón | `{"slot":"slot_01","distancia":8,"tipo":"carro","label":"C-01"}` |
| `sensores/estado` | Estado directo de un cajón | `{"slot":"slot_01","status":"ocupado","tipo":"carro"}` |
| `parqueadero/entrada` | Si la entrada está libre | `{"libre": true}` |
| `parqueadero/espacios` | Estado masivo de todos los cajones | `{"espacios":[...]}` |

**Regla de umbral para sensores:**
- Distancia `< 15 cm` → cajón **OCUPADO**
- Distancia `≥ 15 cm` → cajón **LIBRE**
- Distancia `> 400 cm` → lectura ignorada (error del sensor)

El backend **publica** en:

| Tópico | Cuándo | Payload |
|---|---|---|
| `talanquera/control` | Al llamar `/api/v1/parking/servo` | `{"angulo": 90, "accion": "abrir"}` |

---

## ⚠️ AVISO IMPORTANTE — Raspberry Pi

> **Helen, lee esto antes de tocar cualquier cosa relacionada con la Raspberry Pi o MQTT.**

La Raspberry Pi real está conectada al parqueadero físico. Publicar mensajes MQTT incorrectos puede:
- Abrir o cerrar la talanquera inesperadamente
- Confundir el estado del mapa para todos los usuarios

**Para desarrollo y pruebas SIN hardware:**

```bash
# Desde la carpeta backend/, activa el venv primero:
.venv\Scripts\activate   (Windows)

# Simulador completo de la Raspberry (cambia estados cada 5 segundos):
python simulador_raspberry.py

# Monitor de todos los mensajes MQTT en tiempo real:
python dashboard_mqtt.py

# Prueba rápida de 5 mensajes y desconecta:
python test_pub.py

# Control manual de la talanquera desde consola:
python servo_control.py            # abre
python servo_control.py --cerrar   # cierra
```

**Nunca ejecutes `simulador_raspberry.py` si la Raspberry Pi real está conectada al broker**, porque ambos publicarían al mismo tiempo y los estados se mezclarían. El simulador usa paho-mqtt v1 (sin `CallbackAPIVersion`) — si da error de versión, es porque el venv usa paho v2; actualiza el import o usa `test_pub.py` en su lugar.

El broker es **HiveMQ Cloud** (en internet). Las credenciales están en `backend/.env`. **No compartas ese archivo ni lo subas al repositorio.** El `.gitignore` ya lo excluye.

---

## Cómo arrancar el proyecto localmente

### Prerrequisitos
- Python 3.11+
- Node.js 18+
- PostgreSQL corriendo en `localhost:5432`
- La base de datos `smartparku` creada

### Backend

```bash
cd SmartParkU/backend

# 1. Crear y activar entorno virtual (si no existe)
python -m venv venv
venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Copiar y llenar variables de entorno
copy .env.example .env
# Editar .env con tu DATABASE_URL, SECRET_KEY, etc.

# 4. Correr migraciones
alembic upgrade head

# 5. Poblar datos iniciales (solo la primera vez)
python app/initial_data.py

# 6. Arrancar el servidor
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd SmartParkU/frontend

# 1. Instalar dependencias
npm install

# 2. Arrancar en desarrollo
npm run dev
# → abre http://localhost:3000
```

### Usuarios de prueba (del seeder)

| Correo | Contraseña | Rol |
|---|---|---|
| admin@ucc.edu.co | admin123 | SuperAdmin |
| estudiante@ucc.edu.co | estudiante123 | Estudiante |
| admin.campus@ucc.edu.co | admincampus123 | Administrativo |
| visitante@gmail.com | visitante123 | Visitante |
| inactivo@ucc.edu.co | password123 | Inactivo |

---

## Estado actual — ¿Qué está hecho?

### ✅ Completo y funcionando

**Backend:**
- Autenticación con JWT (login, hash bcrypt, generación de token)
- CRUD completo de vehículos y accesos
- Sistema QR de punta a punta: generación de imagen PNG base64, firma HMAC-SHA256, validación de firma y expiración, asignación de espacio, creación de registro de acceso
- Cliente MQTT conectado a HiveMQ Cloud con TLS, auto-reconexión y gestión de estado en memoria
- WebSocket que hace broadcast a todos los clientes conectados en tiempo real
- Integración QR → WebSocket (al escanear el QR, el mapa se actualiza inmediatamente sin esperar al sensor)
- Migraciones Alembic (3 versiones)
- Seeder de datos iniciales
- Herramientas de desarrollo: simulador de Raspberry, monitor MQTT, script de servo

**Frontend:**
- Página de login con diseño UCC (colores institucionales: azul `#1E3A5F`, cyan `#00AEEF`, verde `#6AB023`)
- Enrutamiento por rol: Estudiante → `StudentDashboard` inline, Admin/SuperAdmin → `/admin/dashboard`
- Estado global persistido con Zustand (token + usuario en `localStorage`)
- `parkingStore`: WebSocket con reconexión exponencial (3s → 30s máx), fallback de 10 slots para que la UI nunca quede en blanco
- `qrStore`: máquina de estados del flujo QR (`idle → generating → show_qr → camera → scanning → success/error`), cuenta regresiva, manejo de errores 409/410/401 en español
- `authStore`: persistencia en localStorage, migración automática v2 (invalida caché vieja sin `id_usuario`)
- Componentes: mapa de parqueadero, generador de QR, escáner por cámara (`html5-qrcode`), perfil de estudiante, ilustraciones

### 🔄 Parcialmente hecho / pendiente

| Qué | Estado | Notas |
|---|---|---|
| Protección de rutas con JWT | ⚠️ Pendiente | El token se genera y guarda pero ningún endpoint del backend valida el `Bearer` token. Cualquiera puede llamar la API sin autenticarse. Hay que agregar `Depends(get_current_user)` en los routers. |
| Flujo de salida del parqueadero | ⚠️ Pendiente | `hora_salida` existe en el modelo y el schema, pero no hay endpoint de "checkout" ni lógica que libere el espacio automáticamente al salir. |
| Dashboard de administrador | 🔄 Parcial | La página existe en `/admin/dashboard/` pero no se revisó en detalle. |
| Página de comparación | 🔄 Sin revisar | Existe en `/comparison/`. |
| Recuperación de contraseña | ❌ Solo UI | El botón "¿Olvidaste tu clave?" está en la pantalla de login pero no hace nada. No existe endpoint de backend. |
| App móvil Flutter | ❌ Solo esqueleto | Solo tiene la estructura de carpetas y el `pubspec.yaml`. Sin pantallas ni lógica. |
| Migración de tablas `vehiculos` y `accesos` | ⚠️ Revisar | Las tablas existen en los modelos y funcionan, pero la migración inicial de Alembic solo crea `usuarios` y `espacios_parqueo`. Las otras tablas parecen haberse creado manualmente. Verificar que `alembic upgrade head` las cree correctamente en un entorno nuevo. |

---

## Dependencias principales

### Backend (`requirements.txt`)
```
fastapi>=0.115.0
uvicorn[standard]>=0.30.1
sqlalchemy>=2.0.35
psycopg[binary]>=3.2.1         ← driver PostgreSQL v3
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
bcrypt==4.0.1                   ← fijado para evitar incompatibilidades
pydantic[email]>=2.9.2
pydantic-settings>=2.5.2
paho-mqtt>=2.0.0                ← v2.x — importante, usa CallbackAPIVersion.VERSION2
websockets>=12.0
qrcode[pil]>=7.4.2
alembic>=1.13.0
python-dotenv>=1.0.1
```

### Frontend
```
Next.js 14 (App Router)
React 18
TypeScript
Tailwind CSS
Zustand (estado global + persistencia)
Framer Motion (animaciones)
html5-qrcode (escáner de cámara)
Lucide React (íconos)
```

---

## Variables de entorno necesarias (`backend/.env`)

```env
# Base de datos
DATABASE_URL=postgresql+psycopg://usuario:password@localhost:5432/smartparku

# Seguridad
SECRET_KEY=una_clave_larga_y_aleatoria_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# MQTT — HiveMQ Cloud
MQTT_BROKER=7de2fa1d05f84c5c8f2fcacca06d98da.s1.eu.hivemq.cloud
MQTT_PORT=8883
MQTT_USERNAME=Juliana
MQTT_PASSWORD=<la contraseña real>
```

---

## Decisiones técnicas importantes (para contexto)

- **paho-mqtt v2**: El cliente usa `CallbackAPIVersion.VERSION2` obligatorio desde paho-mqtt 2.0. Si ves `TypeError` al conectar, es incompatibilidad de versión.
- **`simulador_raspberry.py` usa API vieja de paho**: Ese archivo usa `mqtt.Client` sin `CallbackAPIVersion` (API v1 implícita). Funciona con paho < 2.0. Si el venv tiene paho v2, el simulador lanzará un warning pero seguirá funcionando.
- **Estado en memoria vs BD**: `parking_state` en `mqtt_client.py` es el estado vivo en RAM, actualizado por los sensores. La BD (`espacios_parqueo`) es la fuente de verdad persistente. El endpoint `/parking/slots` mezcla ambos (la RAM tiene prioridad para el `status`).
- **HMAC para QR**: El QR no usa JWT sino HMAC-SHA256 con la misma `SECRET_KEY`. El payload va codificado en base64 URL-safe. No es cifrado, es una firma — cualquiera puede decodificar el base64, pero no puede falsificar la firma sin conocer la `SECRET_KEY`.
- **WebSocket con colas async**: Cada cliente WebSocket conectado tiene su propia `asyncio.Queue`. El broadcast es `put_nowait` (no bloquea). Si la cola está llena (20 mensajes), se descarta el mensaje para no bloquear al MQTT.
- **Reconexión exponencial en el frontend**: El `parkingStore` de Zustand reconecta el WebSocket con backoff 3s → 6s → 12s → 24s → 30s (máximo). Mientras está desconectado, la UI muestra los 10 slots en "libre" como fallback visual.
