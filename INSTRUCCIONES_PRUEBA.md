# 🚀 SmartParkU - INSTRUCCIONES DE PRUEBA

## ✅ ESTADO ACTUAL DEL PROYECTO

### 🟢 Backend (FastAPI)
- ✅ **Corriendo en:** http://localhost:8000
- 📚 **Documentación:** http://localhost:8000/docs
- 💾 **Base de datos:** SQLite (smartparku.db) con 10 slots y usuarios creados

### 🟢 Frontend (Next.js)
- ✅ **Corriendo en:** http://localhost:3001 ⚠️ (Puerto 3001, no 3000)
- 🔌 **WebSocket:** ws://localhost:8000/ws/parking

---

## 👥 USUARIOS DE PRUEBA

### 🎓 Usuario 1: ESTUDIANTE
```
📧 Email:    estudiante@ucc.edu.co
🔑 Password: estudiante123
```

**Rol:** Estudiante  
**Acceso a:**
- ✅ Dashboard con mapa IoT en tiempo real
- ✅ Filtro por tipo de vehículo (Carros, Motos, Bicicletas)
- ✅ Visualización de 10 slots del parqueadero
- ✅ Reserva de slots VIP (V-01)
- ✅ Widget Green Impact (CO₂ ahorrado)
- ✅ Secciones: Mapa, Reservas, Historial Green, Perfil

---

### 👨‍💼 Usuario 2: ADMINISTRADOR
```
📧 Email:    admin@ucc.edu.co
🔑 Password: admin123
```

**Rol:** SuperAdmin  
**Acceso a:**
- ✅ Dashboard administrativo
- ✅ Gestión de 10 slots del parqueadero UCC
- ✅ Análisis de uso (gráfico circular por tipo de vehículo)
- ✅ Panel de alertas del sistema
- ✅ Gestión de cupos (ceder, ocupar, liberar)
- ✅ Estadísticas en tiempo real

---

## 🧪 PASOS PARA PROBAR

### PASO 1: Acceder al Sistema
1. Abre tu navegador en: **http://localhost:3001**
2. Deberías ver la página de Login con el logo UCC

### PASO 2: Probar Usuario Estudiante
1. **Login:**
   - Email: `estudiante@ucc.edu.co`
   - Password: `estudiante123`
   - Click en "Iniciar sesión"

2. **Explorar Dashboard:**
   - ✅ Verifica que aparezca "Bienvenido Estudiante Prueba"
   - ✅ Verifica el widget Green Impact con CO₂ ahorrado
   - ✅ Verifica que se muestre el mapa del parqueadero

3. **Probar Mapa IoT:**
   - ✅ Click en "Carros" para filtrar solo carros (C-01 a C-04)
   - ✅ Click en "Motos" para filtrar solo motos (M-01 a M-03)
   - ✅ Click en "Bicicletas" para filtrar bicicletas (B-01, B-02)
   - ✅ Click en "Todos" para ver los 10 slots

4. **Interactuar con Slots:**
   - ✅ Click en el slot VIP (V-01, color amarillo/lima)
   - ✅ Debería abrir un modal con información
   - ✅ Verifica que diga "VIP Reservable"
   - ✅ Click en "Reservar Cupo VIP"

5. **Probar Navegación:**
   - ✅ Click en "MAPA" (abajo) → Ver mapa
   - ✅ Click en "RESERVAS" → Ver "No tienes reservas activas"
   - ✅ Click en "GREEN" → Ver historial de CO₂
   - ✅ Click en "PERFIL" → Ver información del usuario

6. **Cerrar Sesión:**
   - ✅ Click en el botón rojo de Logout (arriba derecha)

### PASO 3: Probar Usuario Admin
1. **Login:**
   - Email: `admin@ucc.edu.co`
   - Password: `admin123`
   - Click en "Iniciar sesión"

2. **Explorar Dashboard Admin:**
   - ✅ Verifica que aparezca "Hola, Admin Jiliana"
   - ✅ Verifica el mensaje "Panel de Gestión"
   - ✅ Verifica que aparezca rol "Mantenimiento / Gestión"

3. **Revisar Análisis de Uso:**
   - ✅ Busca el widget "Análisis de Uso"
   - ✅ Verifica el gráfico circular con porcentajes
   - ✅ Verifica las barras: Autos 65%, Motos 25%, Scooters 10%

4. **Revisar Alertas:**
   - ✅ Busca el widget "Alertas del Sistema"
   - ✅ Verifica que muestre "2 ACTIVAS"
   - ✅ Lee las alertas de seguridad y tiempo

5. **Gestionar Slots:**
   - ✅ Busca "Mapa de Gestión de Cupos"
   - ✅ Verifica que muestre los 10 slots
   - ✅ Click en cualquier slot (C-01, C-02, etc.)
   - ✅ Verifica que se abra un panel con información
   - ✅ Si es un slot Admin tipo "Fixed", verifica opción "Ceder Cupo"

6. **Navegación Admin:**
   - ✅ Click en "Dashboard" (abajo)
   - ✅ Click en "Mapa Total"
   - ✅ Click en "Reportes"
   - ✅ Click en "Usuarios"

---

## 🎯 CHECKLIST DE VERIFICACIÓN

### ✅ Backend
- [ ] Backend responde en http://localhost:8000/docs
- [ ] La documentación de FastAPI se ve correctamente
- [ ] Puedes expandir los endpoints en /docs

### ✅ Frontend
- [ ] Frontend carga en http://localhost:3001
- [ ] Página de login aparece correctamente
- [ ] Los colores UCC están aplicados (verde, azul, lima)

### ✅ Autenticación
- [ ] Puedes hacer login con estudiante@ucc.edu.co
- [ ] Puedes hacer login con admin@ucc.edu.co
- [ ] El botón de logout funciona
- [ ] Al hacer logout vuelves al login

### ✅ Mapa de Parqueadero (10 Slots)
- [ ] Se muestran los 10 slots del parqueadero
- [ ] Carros: C-01, C-02, C-03, C-04 (4 slots)
- [ ] Motos: M-01, M-02, M-03 (3 slots)
- [ ] Bicicletas: B-01, B-02 (2 slots)
- [ ] VIP: V-01 (1 slot, color diferente)

### ✅ Funcionalidades Estudiante
- [ ] Widget Green Impact muestra CO₂ ahorrado
- [ ] Filtros de vehículos funcionan
- [ ] Click en slots muestra información
- [ ] Slot VIP permite reservar
- [ ] Navegación inferior funciona

### ✅ Funcionalidades Admin
- [ ] Dashboard admin carga correctamente
- [ ] Análisis de uso muestra gráfico
- [ ] Alertas del sistema aparecen
- [ ] Mapa de gestión muestra 10 slots
- [ ] Click en slots muestra opciones de gestión

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### ❌ "Cannot GET /" o página en blanco
**Solución:** Usa el puerto correcto → http://localhost:3001 (no 3000)

### ❌ "Login failed" o "401 Unauthorized"
**Solución:** 
1. Verifica que escribiste bien el email y password
2. Asegúrate de que el backend esté corriendo (http://localhost:8000/docs)
3. Revisa que la base de datos se haya creado (debería existir `backend/smartparku.db`)

### ❌ Los slots no aparecen en el mapa
**Solución:**
1. Abre la consola del navegador (F12)
2. Ve a la pestaña "Network" → "WS" (WebSockets)
3. Verifica que haya una conexión a ws://localhost:8000/ws/parking
4. Si hay error, verifica que el backend esté corriendo

### ❌ "WebSocket connection failed"
**Solución:** El backend debe estar corriendo. Verifica en http://localhost:8000/docs

### ❌ Error de base de datos
**Solución:** Si hay algún problema, puedes reiniciar la base de datos:
```bash
# Eliminar la base de datos actual
rm backend/smartparku.db

# Volver a crear usuarios y slots
python backend/seed_users.py
```

---

## 📊 ESTRUCTURA DEL PARQUEADERO (10 Slots)

```
┌─────────────────────────────────────────────────────┐
│                 ZONA SUPERIOR                       │
│  ┌────────┐  ┌──────────────────┐  ┌────────────┐ │
│  │  VIP   │  │      MOTOS       │  │ BICICLETAS │ │
│  │  V-01  │  │  M-01 M-02 M-03  │  │  B-01 B-02 │ │
│  │   ⭐   │  │   🏍️  🏍️  🏍️   │  │   🚲  🚲  │ │
│  └────────┘  └──────────────────┘  └────────────┘ │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                 ZONA CARROS                         │
│                                                     │
│      C-01    C-02     │     C-03    C-04          │
│       🚗     🚗       │      🚗     🚗            │
│                       │                            │
│                   ENTRADA ↓                        │
└─────────────────────────────────────────────────────┘
```

---

## 🎨 COLORES UCC APLICADOS

- **Verde Libre:** #6AB023 (slots disponibles normales)
- **Lima VIP:** #B5D334 (slot VIP V-01 disponible)
- **Rojo Ocupado:** #ef4444 (slots ocupados)
- **Azul UCC:** #00AEEF (botones y acciones)
- **Navy UCC:** #1E3A5F (textos y headers)

---

## ✅ ¡TODO LISTO!

**URLs Finales:**
- 🎨 Frontend: **http://localhost:3001**
- 🔧 Backend: **http://localhost:8000/docs**

**Usuarios:**
- 🎓 Estudiante: `estudiante@ucc.edu.co` / `estudiante123`
- 👨‍💼 Admin: `admin@ucc.edu.co` / `admin123`

---

**¡Empieza probando con el usuario estudiante! 🚀**
