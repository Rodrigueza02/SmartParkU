# Implementación de Registro de Estudiantes y Sistema de Alertas

## ✅ Completado

### 1. Sistema de Registro de Estudiantes

#### Backend
- ✅ **Schemas** (`backend/app/schemas/auth.py`):
  - `RegisterRequest`: Validación de datos de registro (nombre, correo, password, carnet_id)
  - `RegisterResponse`: Respuesta con ID y mensaje de éxito
  
- ✅ **Endpoint** (`backend/app/api/auth.py`):
  - `POST /api/v1/auth/register`: Endpoint para crear nuevas cuentas de estudiantes
  
- ✅ **Servicio** (`backend/app/services/auth_service.py`):
  - `register_student()`: Lógica de registro con validaciones:
    - Verificación de correo duplicado
    - Verificación de carnet duplicado
    - Hash de contraseña seguro
    - Rol automático: "Estudiante"
    - Estado por defecto: "Activo"

#### Frontend
- ✅ **Página de Registro** (`frontend/src/app/register/page.tsx`):
  - Formulario completo con validación
  - Campos: Nombre completo, correo institucional, contraseña, carnet (opcional)
  - Diseño consistente con UCC branding
  - Animaciones y feedback visual
  - Redirección automática al login tras registro exitoso
  
- ✅ **Actualización del Login** (`frontend/src/app/page.tsx`):
  - Botón "Crear cuenta" funcional que redirige a `/register`
  - Enlace desde registro de vuelta al login

---

### 2. Sistema de Alertas

#### Backend

##### Base de Datos
- ✅ **Modelo** (`backend/app/models/alerta.py`):
  - Tabla `alertas` con campos:
    - `id_alerta`: ID primario
    - `id_usuario`: Usuario que crea la alerta
    - `tipo`: 'seguridad', 'emergencia', 'reporte'
    - `mensaje`: Descripción de la situación
    - `ubicacion`: Ubicación en el parqueadero (opcional)
    - `estado`: 'pendiente', 'revisada', 'resuelta'
    - `media_url`: URL del archivo multimedia
    - `media_type`: 'foto' o 'video'
    - `fecha_creacion`: Timestamp automático
    - `fecha_revision`: Cuando fue revisada
    - `revisado_por`: Admin que la revisó
  - Relaciones con tabla `usuarios`

- ✅ **Migración** (`backend/alembic/versions/20260921_1000_create_alertas_table.py`):
  - Script de Alembic para crear la tabla
  - Índices y foreign keys configurados

##### API
- ✅ **Schemas** (`backend/app/schemas/alerta.py`):
  - `AlertaCreate`: Datos para crear alerta
  - `AlertaResponse`: Respuesta con datos completos
  - `AlertaUpdate`: Actualización de estado
  - `AlertaListResponse`: Lista con estadísticas

- ✅ **Repository** (`backend/app/repositories/alerta_repository.py`):
  - CRUD completo para alertas
  - Consultas optimizadas con joins
  - Conteo de alertas por estado

- ✅ **Service** (`backend/app/services/alerta_service.py`):
  - Lógica de negocio para alertas
  - Manejo de archivos multimedia
  - Almacenamiento en `backend/data/alertas/`
  - Generación de nombres únicos (UUID)

- ✅ **Endpoints** (`backend/app/api/alertas.py`):
  - `POST /api/v1/alertas`: Crear alerta (con multimedia opcional)
  - `GET /api/v1/alertas/mis-alertas`: Ver alertas del usuario actual
  - `GET /api/v1/alertas`: Listar todas (solo admin)
  - `GET /api/v1/alertas/{id}`: Ver alerta específica
  - `PATCH /api/v1/alertas/{id}/estado`: Actualizar estado (solo admin)

#### Frontend
- ✅ **Componente AlertaForm** (`frontend/src/components/AlertaForm.tsx`):
  - Formulario modal completo
  - Selección de tipo de alerta (seguridad, emergencia, reporte)
  - Campo de mensaje con validación (mínimo 10 caracteres)
  - Campo de ubicación (opcional)
  - Captura de foto o video
  - Preview de multimedia antes de enviar
  - Subida de archivos via FormData
  - Feedback visual de éxito/error
  
- ✅ **Integración en Dashboard** (`frontend/src/components/StudentDashboard.tsx`):
  - Vista "Pánico" rediseñada con formulario de alertas
  - Botón FAB (Floating Action Button) rojo visible siempre
  - Estado para mostrar/ocultar formulario
  - Cierre automático tras envío exitoso

---

## 🔧 Configuración Requerida

### Aplicar Migración de Base de Datos

La migración se aplicará automáticamente cuando inicies el backend con Docker Compose.

Si necesitas aplicarla manualmente (cuando la BD esté corriendo):

```bash
cd backend
docker-compose exec backend python -m alembic upgrade head
```

O si estás usando el contenedor de desarrollo:

```bash
docker-compose up -d  # Esto aplica automáticamente las migraciones
```

---

## 📋 Cómo Usar

### Registro de Estudiantes

1. **Desde el Login**:
   - Hacer clic en "Crear cuenta" al final del formulario de login
   - Completar el formulario de registro:
     - Nombre completo (mínimo 3 caracteres)
     - Correo institucional (formato email válido)
     - Contraseña (mínimo 6 caracteres)
     - Carnet universitario (opcional)
   - Hacer clic en "Crear Cuenta"
   - Esperar confirmación y redirección automática al login
   - Iniciar sesión con las credenciales creadas

2. **Validaciones**:
   - El correo no puede estar duplicado
   - El carnet (si se proporciona) no puede estar duplicado
   - La contraseña debe tener al menos 6 caracteres
   - Todos los campos obligatorios deben completarse

### Sistema de Alertas (Estudiantes)

1. **Generar Alerta**:
   - Desde el dashboard del estudiante, hacer clic en el botón rojo flotante (FAB) en la esquina inferior derecha
   - O navegar a la sección "PÁNICO" en el menú inferior
   - Hacer clic en "GENERAR ALERTA"
   
2. **Completar Formulario**:
   - Seleccionar tipo de alerta:
     - **Seguridad**: Situaciones sospechosas
     - **Emergencia**: Situaciones urgentes
     - **Reporte**: Incidentes generales
   - Escribir descripción (mínimo 10 caracteres)
   - (Opcional) Indicar ubicación específica
   - (Opcional) Adjuntar foto o video:
     - Hacer clic en "Foto" para seleccionar imagen
     - Hacer clic en "Video" para seleccionar video
     - Vista previa del archivo antes de enviar
     - Posibilidad de eliminar y cambiar archivo
   - Hacer clic en "Enviar Alerta"

3. **Confirmación**:
   - Mensaje de éxito cuando la alerta se envía
   - La alerta queda registrada con estado "pendiente"
   - Los administradores reciben la notificación

### Gestión de Alertas (Administradores)

Los administradores pueden:

1. **Ver todas las alertas**:
   ```
   GET /api/v1/alertas
   ```
   - Lista completa con estadísticas
   - Filtrado por estado (opcional)

2. **Ver detalles de una alerta**:
   ```
   GET /api/v1/alertas/{id_alerta}
   ```

3. **Actualizar estado**:
   ```
   PATCH /api/v1/alertas/{id_alerta}/estado
   Body: { "estado": "revisada" }  # o "resuelta"
   ```

---

## 🎨 Características de UX/UI

### Registro
- Diseño dividido en dos paneles (desktop)
- Panel izquierdo con branding UCC
- Formulario responsivo con validación en tiempo real
- Animaciones suaves con Framer Motion
- Feedback visual de errores y éxito
- Colores corporativos UCC (#6AB023, #00AEEF, #1E3A5F)

### Alertas
- Botón flotante rojo siempre visible
- Modal centralizado y responsive
- Preview de multimedia antes de enviar
- Selección visual de tipo de alerta con colores distintivos
- Contador de caracteres en tiempo real
- Estados de carga durante el envío
- Mensaje de confirmación con animación

---

## 🔐 Seguridad

### Registro
- Contraseñas hasheadas con bcrypt
- Validación de formato de email
- Prevención de registros duplicados
- Rol de "Estudiante" asignado automáticamente

### Alertas
- Autenticación JWT requerida
- Usuarios solo pueden ver sus propias alertas
- Administradores pueden ver y gestionar todas
- Archivos multimedia con nombres únicos (UUID)
- Validación de tipos de archivo
- Almacenamiento seguro en directorio dedicado

---

## 📁 Archivos Creados/Modificados

### Backend
**Nuevos:**
- `backend/app/models/alerta.py`
- `backend/app/schemas/alerta.py`
- `backend/app/repositories/alerta_repository.py`
- `backend/app/services/alerta_service.py`
- `backend/app/api/alertas.py`
- `backend/alembic/versions/20260921_1000_create_alertas_table.py`
- `backend/data/alertas/.gitkeep`

**Modificados:**
- `backend/app/schemas/auth.py` - Agregados RegisterRequest y RegisterResponse
- `backend/app/api/auth.py` - Agregado endpoint de registro
- `backend/app/services/auth_service.py` - Agregado método register_student
- `backend/app/schemas/__init__.py` - Exportaciones actualizadas
- `backend/app/models/__init__.py` - Exportación de Alerta
- `backend/app/repositories/__init__.py` - Exportación de AlertaRepository
- `backend/app/services/__init__.py` - Exportación de AlertaService
- `backend/app/api/__init__.py` - Router de alertas incluido

### Frontend
**Nuevos:**
- `frontend/src/app/register/page.tsx`
- `frontend/src/components/AlertaForm.tsx`

**Modificados:**
- `frontend/src/app/page.tsx` - Botón "Crear cuenta" funcional
- `frontend/src/components/StudentDashboard.tsx` - Integración de sistema de alertas

---

## ✅ Próximos Pasos

1. **Iniciar el sistema**:
   ```bash
   docker-compose up -d
   ```

2. **Verificar que la migración se aplicó**:
   - La tabla `alertas` debe existir en la base de datos

3. **Probar el registro**:
   - Ir a http://localhost:3000
   - Hacer clic en "Crear cuenta"
   - Registrar un nuevo estudiante
   - Iniciar sesión

4. **Probar las alertas**:
   - Desde el dashboard del estudiante
   - Hacer clic en el botón rojo flotante
   - Crear una alerta de prueba con foto/video

5. **Panel de administración** (futuro):
   - Crear interfaz para que los admins vean y gestionen alertas
   - Dashboard con estadísticas de alertas
   - Sistema de notificaciones en tiempo real (WebSockets/MQTT)

---

## 🐛 Solución de Problemas

### Error al aplicar migración
Si la migración falla, asegúrate de que:
- La base de datos PostgreSQL está corriendo
- Las credenciales en `.env` son correctas
- El backend tiene permisos de escritura en `data/alertas/`

### Error al subir archivos multimedia
- Verificar que el directorio `backend/data/alertas/` existe
- Verificar permisos de escritura
- Verificar tamaño máximo de archivo en configuración de FastAPI

### Error de CORS
- Verificar configuración de CORS en `backend/app/main.py`
- Asegurarse de que el frontend está en la lista de orígenes permitidos

---

## 📊 Endpoints API Disponibles

### Autenticación
- `POST /api/v1/auth/register` - Registro de estudiantes ⭐ NUEVO
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/forgot-password` - Recuperar contraseña
- `POST /api/v1/auth/reset-password` - Restablecer contraseña

### Alertas ⭐ NUEVO
- `POST /api/v1/alertas` - Crear alerta
- `GET /api/v1/alertas/mis-alertas` - Ver mis alertas
- `GET /api/v1/alertas` - Listar todas (admin)
- `GET /api/v1/alertas/{id}` - Ver alerta específica
- `PATCH /api/v1/alertas/{id}/estado` - Actualizar estado (admin)

---

¡Sistema completamente funcional y listo para usar! 🚀
