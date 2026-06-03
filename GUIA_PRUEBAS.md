# 🚀 Guía de Pruebas - SmartParkU

## 📋 Requisitos Previos

- ✅ Node.js (v18 o superior)
- ✅ Python 3.10+
- ✅ PostgreSQL instalado y corriendo
- ✅ Git

---

## 🗄️ PASO 1: Configurar Base de Datos PostgreSQL

### 1.1 Crear la base de datos
Abre tu cliente PostgreSQL (pgAdmin o terminal) y ejecuta:

```sql
CREATE DATABASE smartparku;
```

### 1.2 Crear un usuario (opcional, puedes usar el usuario postgres por defecto)
```sql
CREATE USER smartpark_user WITH PASSWORD 'tu_password_seguro';
GRANT ALL PRIVILEGES ON DATABASE smartparku TO smartpark_user;
```

---

## ⚙️ PASO 2: Configurar Backend (Python/FastAPI)

### 2.1 Navegar a la carpeta backend
```bash
cd backend
```

### 2.2 Crear archivo `.env`
Copia el archivo de ejemplo y edítalo:

**Para Windows PowerShell:**
```powershell
Copy-Item .env.example .env
```

**O manualmente:** Crea un archivo llamado `.env` en la carpeta `backend` con este contenido:

```env
# Base de Datos (PostgreSQL)
DATABASE_URL=postgresql+psycopg://postgres:tu_password@localhost:5432/smartparku

# Seguridad JWT
SECRET_KEY=smartparku_secret_key_2024_super_segura_cambiar_en_produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# MQTT - HiveMQ Cloud (opcional por ahora, para IoT real)
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=
```

**IMPORTANTE:** Reemplaza `tu_password` con tu contraseña real de PostgreSQL.

### 2.3 Instalar dependencias de Python
```bash
pip install -r requirements.txt
```

### 2.4 Crear las tablas e insertar usuarios de prueba
```bash
python seed_users.py
```

**Esto creará automáticamente:**
- ✅ Tabla de usuarios
- ✅ Tabla de espacios de parqueo (10 slots)
- ✅ Usuarios de prueba

### 2.5 Iniciar el servidor backend
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**✅ Backend corriendo en:** http://localhost:8000
**📚 Documentación API:** http://localhost:8000/docs

---

## 🎨 PASO 3: Configurar Frontend (Next.js)

### 3.1 Volver a la raíz del proyecto
```bash
cd ..
```

### 3.2 Instalar dependencias de Node.js
```bash
npm install
```

### 3.3 Crear archivo `.env.local` (opcional, ya tiene defaults)
Si necesitas cambiar las URLs del backend, crea `.env.local` en la raíz:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws/parking
```

### 3.4 Iniciar el servidor de desarrollo
```bash
npm run dev
```

**✅ Frontend corriendo en:** http://localhost:3000

---

## 🧪 PASO 4: Probar con los Usuarios

### 👤 Usuario 1: **ESTUDIANTE**

**Credenciales:**
- 📧 Email: `estudiante@ucc.edu.co`
- 🔑 Password: `estudiante123`

**Funcionalidades a probar:**
1. **Login** → http://localhost:3000
2. **Dashboard Estudiante** → Ver el mapa IoT en tiempo real
3. **Filtrar espacios** → Por tipo de vehículo (Carro, Moto, Bicicleta)
4. **Seleccionar slot VIP** → Debería permitir reservar
5. **Seleccionar slot normal** → Solo info, no reservable
6. **Widget Green Impact** → Ver CO₂ ahorrado
7. **Navegación** → Probar las pestañas (Mapa, Reservas, Green, Perfil)

---

### 👨‍💼 Usuario 2: **ADMINISTRADOR**

**Credenciales:**
- 📧 Email: `admin@ucc.edu.co`
- 🔑 Password: `admin123`

**Funcionalidades a probar:**
1. **Login** → http://localhost:3000
2. **Dashboard Admin** → Ver panel de gestión
3. **Mapa de gestión** → Ver los 10 slots del parqueadero
4. **Análisis de uso** → Gráfico circular con porcentajes
5. **Alertas del sistema** → Ver notificaciones de seguridad
6. **Gestión de slots** → Click en slots para ver opciones
7. **Ceder cupos Admin** → (Si aplica para slots tipo Admin)

---

## 🔍 PASO 5: Verificar que Todo Funciona

### ✅ Checklist Backend
- [ ] Backend responde en http://localhost:8000
- [ ] `/docs` muestra la documentación de FastAPI
- [ ] Puedes hacer login en `/api/v1/auth/login`
- [ ] El endpoint `/api/v1/parking/espacios` devuelve los 10 slots

### ✅ Checklist Frontend
- [ ] Frontend carga en http://localhost:3000
- [ ] Página de login se muestra correctamente
- [ ] Puedes hacer login con estudiante@ucc.edu.co
- [ ] Puedes hacer login con admin@ucc.edu.co
- [ ] El mapa muestra los 10 slots del parqueadero
- [ ] Los colores UCC se muestran correctamente

### ✅ Checklist WebSocket (Tiempo Real)
- [ ] Abre las DevTools del navegador (F12) → Pestaña Network → WS
- [ ] Deberías ver una conexión WebSocket a `ws://localhost:8000/ws/parking`
- [ ] El estado debe ser "En vivo" (icono verde)

---

## 🐛 Solución de Problemas Comunes

### ❌ Error: "DATABASE_URL not found"
**Solución:** Verifica que el archivo `.env` esté en la carpeta `backend` y tenga la variable `DATABASE_URL`

### ❌ Error: "Connection refused" en PostgreSQL
**Solución:** 
1. Verifica que PostgreSQL esté corriendo
2. Verifica el puerto (por defecto 5432)
3. Verifica la contraseña en el archivo `.env`

### ❌ Error: "WebSocket connection failed"
**Solución:** Asegúrate de que el backend esté corriendo en el puerto 8000

### ❌ Los slots no aparecen en el mapa
**Solución:** 
1. Verifica que corriste `python seed_users.py`
2. Revisa la consola del navegador (F12) para errores
3. Verifica que el backend responda en `/api/v1/parking/espacios`

---

## 📊 Estructura de los 10 Slots del Parqueadero

```
┌─────────────────────────────────────────────┐
│  VIP          MOTOS         BICICLETAS      │
│  V-01       M-01 M-02 M-03    B-01 B-02     │
│   ⭐         🏍️  🏍️  🏍️       🚲  🚲       │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│              CARROS (4 espacios)            │
│                                             │
│    C-01  C-02    │    C-03  C-04           │
│     🚗   🚗      │     🚗   🚗             │
│                  │                          │
│                ENTRADA                      │
└─────────────────────────────────────────────┘
```

---

## 🎯 Flujo Completo de Prueba

### Escenario 1: Estudiante busca parqueadero
1. Login como estudiante
2. Ver mapa en tiempo real
3. Filtrar por "Carros"
4. Seleccionar slot VIP (V-01)
5. Ver información de reserva
6. Revisar Green Impact acumulado

### Escenario 2: Admin gestiona el parqueadero
1. Login como admin
2. Ver dashboard con estadísticas
3. Revisar alertas activas
4. Click en un slot del mapa
5. Ver análisis de uso por tipo de vehículo
6. Revisar reportes (si aplica)

---

## 📝 Notas Adicionales

- **Sin MQTT real:** El proyecto mostrará los 10 slots predefinidos en estado "libre"
- **Con simulador:** Puedes ejecutar `backend/simulador_raspberry.py` para simular sensores IoT
- **Passwords de prueba:** Todos usan el formato `{rol}123` para facilitar las pruebas
- **Base de datos:** Los datos se persisten en PostgreSQL, no se pierden al reiniciar

---

## 🚀 ¡Listo para Probar!

1. Terminal 1: `cd backend && uvicorn main:app --reload`
2. Terminal 2: `npm run dev`
3. Navegador: http://localhost:3000
4. Login: `estudiante@ucc.edu.co` / `estudiante123`

---

**¿Dudas o errores?** Revisa la sección de "Solución de Problemas" arriba. 🔧
