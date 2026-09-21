# 🎉 Nuevas Funcionalidades SmartParkU

## ✅ Implementaciones Completadas

### 1. 👥 Registro de Estudiantes
Los estudiantes ahora pueden crear sus propias cuentas sin necesidad de un administrador.

### 2. 🚨 Sistema de Alertas  
Los estudiantes pueden reportar situaciones inusuales en el parqueadero, incluyendo fotos y videos.

---

## 🚀 Cómo Iniciar el Sistema

### Paso 1: Reiniciar Docker Compose
```bash
docker-compose down
docker-compose up -d
```

El sistema ahora:
- ✅ Aplica automáticamente las migraciones de base de datos
- ✅ Crea la tabla de alertas
- ✅ Configura el directorio para archivos multimedia

### Paso 2: Verificar que todo esté corriendo
```bash
docker-compose ps
```

Deberías ver todos los servicios en estado "Up":
- smartparku_db
- smartparku_backend
- smartparku_frontend
- smartparku_pgadmin
- smartparku_mqtt

### Paso 3: Verificar los logs
```bash
docker-compose logs -f backend
```

Deberías ver:
```
✅ Base de datos conectada!
🔄 Aplicando migraciones de Alembic...
✅ Migraciones aplicadas correctamente
🚀 Iniciando servidor FastAPI...
```

---

## 📱 Cómo Usar las Nuevas Funciones

### FUNCIÓN 1: Crear Cuenta de Estudiante

#### Para el Estudiante:

1. **Acceder al Login**
   - Ir a: http://localhost:3001
   - En la página de inicio de sesión

2. **Crear Cuenta**
   - Hacer clic en "Crear cuenta" (al final del formulario)
   - Completar los datos:
     - **Nombre Completo**: Ej. "María Pérez García"
     - **Correo Institucional**: Ej. "maria.perez@ucc.edu.co"
     - **Contraseña**: Mínimo 6 caracteres
     - **Carnet Universitario** (opcional): Ej. "123456789"
   
3. **Confirmar Registro**
   - Hacer clic en "Crear Cuenta"
   - Esperar mensaje de confirmación
   - Serás redirigido automáticamente al login

4. **Iniciar Sesión**
   - Usar el correo y contraseña que registraste
   - Hacer clic en "Entrar al Campus"

#### Validaciones Automáticas:
- ✅ El correo no puede estar duplicado
- ✅ El carnet no puede estar duplicado (si se proporciona)
- ✅ La contraseña debe tener mínimo 6 caracteres
- ✅ El rol "Estudiante" se asigna automáticamente
- ✅ La cuenta se activa inmediatamente

---

### FUNCIÓN 2: Sistema de Alertas

#### Para el Estudiante:

1. **Acceder al Sistema de Alertas**
   
   Hay 2 formas:
   
   **Opción A - Botón Flotante:**
   - En el dashboard del estudiante
   - Busca el **botón rojo flotante** en la esquina inferior derecha
   - Tiene el ícono de ⚠️
   - Hacer clic en él

   **Opción B - Menú de Navegación:**
   - En la barra inferior
   - Hacer clic en "PÁNICO" (ícono de escudo)

2. **Generar una Alerta**
   
   - Hacer clic en **"GENERAR ALERTA"**

3. **Completar el Formulario**

   **a) Tipo de Alerta:**
   - 🔵 **Seguridad**: Para situaciones sospechosas
     - Ej: "Persona merodeando entre los vehículos"
   - 🔴 **Emergencia**: Para situaciones urgentes
     - Ej: "Accidente en el parqueadero"
   - 🟢 **Reporte**: Para incidentes generales
     - Ej: "Vehículo mal estacionado bloqueando la salida"

   **b) Descripción:** (OBLIGATORIO - mínimo 10 caracteres)
   - Describe qué está ocurriendo
   - Ej: "Observé a una persona intentando abrir las puertas de varios carros en la zona A"

   **c) Ubicación:** (OPCIONAL)
   - Indica dónde está ocurriendo
   - Ej: "Zona A, cerca del puesto M-03"

   **d) Adjuntar Evidencia:** (OPCIONAL)
   - **Foto**: Haz clic en el botón "Foto" 📷
     - Selecciona una imagen de tu dispositivo
     - Verás una vista previa
   - **Video**: Haz clic en el botón "Video" 🎥
     - Selecciona un video de tu dispositivo
     - Verás una vista previa
   - Puedes **eliminar** el archivo con el botón ❌ y seleccionar otro

4. **Enviar la Alerta**
   - Hacer clic en **"Enviar Alerta"**
   - Esperar confirmación
   - La alerta se envía inmediatamente a los administradores

5. **Confirmación**
   - Verás un mensaje: "Alerta Enviada"
   - Tu reporte queda registrado con estado "pendiente"
   - Los administradores serán notificados

---

### Para el Administrador:

#### Ver Todas las Alertas

**Usando la API directamente:**

```bash
# Ver todas las alertas con estadísticas
curl -X GET "http://localhost:8000/api/v1/alertas" \
  -H "Authorization: Bearer TU_TOKEN_DE_ADMIN"

# Filtrar solo alertas pendientes
curl -X GET "http://localhost:8000/api/v1/alertas?estado=pendiente" \
  -H "Authorization: Bearer TU_TOKEN_DE_ADMIN"

# Ver una alerta específica
curl -X GET "http://localhost:8000/api/v1/alertas/1" \
  -H "Authorization: Bearer TU_TOKEN_DE_ADMIN"
```

#### Actualizar Estado de una Alerta

```bash
# Marcar como revisada
curl -X PATCH "http://localhost:8000/api/v1/alertas/1/estado" \
  -H "Authorization: Bearer TU_TOKEN_DE_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{"estado": "revisada"}'

# Marcar como resuelta
curl -X PATCH "http://localhost:8000/api/v1/alertas/1/estado" \
  -H "Authorization: Bearer TU_TOKEN_DE_ADMIN" \
  -H "Content-Type: application/json" \
  -d '{"estado": "resuelta"}'
```

#### Ver Archivos Multimedia

Los archivos se guardan en:
```
backend/data/alertas/
```

Puedes acceder a ellos directamente desde el servidor o implementar un endpoint para servirlos.

---

## 🔍 Endpoints API Disponibles

### Registro
```
POST /api/v1/auth/register
Body: {
  "nombre": "María Pérez",
  "correo": "maria.perez@ucc.edu.co",
  "password": "mi_contraseña_segura",
  "carnet_id": "123456789"  // Opcional
}
```

### Alertas (Estudiantes)
```
# Crear alerta
POST /api/v1/alertas
Headers: Authorization: Bearer <token>
Form-Data:
  - tipo: "seguridad" | "emergencia" | "reporte"
  - mensaje: "Descripción de la situación"
  - ubicacion: "Zona A" (opcional)
  - media_type: "foto" | "video" (opcional)
  - media_file: <archivo> (opcional)

# Ver mis alertas
GET /api/v1/alertas/mis-alertas
Headers: Authorization: Bearer <token>
```

### Alertas (Administradores)
```
# Listar todas con estadísticas
GET /api/v1/alertas
Headers: Authorization: Bearer <token_admin>
Query: ?estado=pendiente (opcional)

# Ver alerta específica
GET /api/v1/alertas/{id}
Headers: Authorization: Bearer <token_admin>

# Actualizar estado
PATCH /api/v1/alertas/{id}/estado
Headers: Authorization: Bearer <token_admin>
Body: { "estado": "revisada" | "resuelta" }
```

---

## 🎨 Capturas de Pantalla

### Registro de Estudiante
```
┌─────────────────────────────────────────┐
│  🎓 SmartParkU                          │
│                                         │
│  Crear Cuenta                          │
│  ──────────────────────────────────    │
│                                         │
│  👤 Nombre Completo                    │
│  ┌─────────────────────────────────┐   │
│  │ María Pérez García              │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ✉️ Correo Institucional               │
│  ┌─────────────────────────────────┐   │
│  │ maria.perez@ucc.edu.co          │   │
│  └─────────────────────────────────┘   │
│                                         │
│  🔒 Contraseña                         │
│  ┌─────────────────────────────────┐   │
│  │ ••••••                           │   │
│  └─────────────────────────────────┘   │
│                                         │
│  🎫 Carnet Universitario (Opcional)    │
│  ┌─────────────────────────────────┐   │
│  │ 123456789                        │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │    ✓ Crear Cuenta               │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ¿Ya tienes cuenta? Inicia sesión     │
└─────────────────────────────────────────┘
```

### Sistema de Alertas
```
┌─────────────────────────────────────────┐
│  ⚠️ Reportar Alerta                     │
│  ──────────────────────────────────    │
│                                         │
│  Tipo de Alerta:                       │
│  [Seguridad] [Emergencia] [Reporte]   │
│                                         │
│  📝 Descripción *                       │
│  ┌─────────────────────────────────┐   │
│  │ Vi a alguien intentando abrir   │   │
│  │ puertas de carros en zona A     │   │
│  │                                  │   │
│  └─────────────────────────────────┘   │
│  35 / 500 caracteres                   │
│                                         │
│  📍 Ubicación (Opcional)               │
│  ┌─────────────────────────────────┐   │
│  │ Zona A, cerca puesto M-03       │   │
│  └─────────────────────────────────┘   │
│                                         │
│  📸 Adjuntar Evidencia                 │
│  [  📷 Foto  ] [  🎥 Video  ]         │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │    📤 Enviar Alerta             │   │
│  └─────────────────────────────────┘   │
│                                         │
│  Tu reporte será enviado al admin      │
└─────────────────────────────────────────┘
```

---

## 🧪 Pruebas Sugeridas

### Test 1: Registro de Estudiante
1. Ir a http://localhost:3001
2. Clic en "Crear cuenta"
3. Registrar datos de prueba:
   - Nombre: Test Student
   - Correo: test.student@ucc.edu.co
   - Password: test123
4. Verificar redirección al login
5. Iniciar sesión con las credenciales creadas

### Test 2: Alerta Sin Multimedia
1. Login como estudiante
2. Clic en botón rojo flotante
3. Seleccionar tipo: "Seguridad"
4. Escribir mensaje: "Prueba de alerta sin foto"
5. Ubicación: "Zona de prueba"
6. Enviar
7. Verificar confirmación

### Test 3: Alerta Con Foto
1. Login como estudiante
2. Clic en "PÁNICO" en menú inferior
3. Clic en "GENERAR ALERTA"
4. Seleccionar tipo: "Reporte"
5. Mensaje: "Prueba con foto adjunta"
6. Clic en botón "Foto"
7. Seleccionar una imagen
8. Verificar preview
9. Enviar
10. Verificar que el archivo se guardó en `backend/data/alertas/`

### Test 4: Alerta Con Video
1. Repetir proceso con video en lugar de foto
2. Verificar que el video se guarda correctamente

### Test 5: Ver Alertas (Admin)
1. Login como admin (usa Postman o curl)
2. GET /api/v1/alertas
3. Verificar que aparecen todas las alertas de prueba
4. Verificar estadísticas (total, pendientes, etc.)

### Test 6: Actualizar Estado (Admin)
1. Tomar el ID de una alerta
2. PATCH /api/v1/alertas/{id}/estado con body: {"estado": "revisada"}
3. Verificar que el estado cambió
4. Verificar que se guardó la fecha de revisión

---

## 📊 Estructura de Base de Datos

### Tabla: alertas
```sql
CREATE TABLE alertas (
    id_alerta SERIAL PRIMARY KEY,
    id_usuario INTEGER NOT NULL REFERENCES usuarios(id_usuario),
    tipo VARCHAR(50) NOT NULL,  -- 'seguridad', 'emergencia', 'reporte'
    mensaje TEXT NOT NULL,
    ubicacion VARCHAR(200),
    estado VARCHAR(50) DEFAULT 'pendiente',  -- 'pendiente', 'revisada', 'resuelta'
    media_url VARCHAR(500),
    media_type VARCHAR(20),  -- 'foto', 'video'
    fecha_creacion TIMESTAMP NOT NULL DEFAULT NOW(),
    fecha_revision TIMESTAMP,
    revisado_por INTEGER REFERENCES usuarios(id_usuario)
);
```

---

## 🔧 Troubleshooting

### Problema: "Error al crear cuenta - correo duplicado"
**Solución**: El correo ya está registrado. Usa otro correo o inicia sesión con el existente.

### Problema: "Error al enviar alerta"
**Solución**: 
1. Verificar que estás autenticado
2. Verificar que el mensaje tiene al menos 10 caracteres
3. Ver logs del backend: `docker-compose logs -f backend`

### Problema: "No se guardan los archivos multimedia"
**Solución**:
1. Verificar que existe el directorio: `backend/data/alertas/`
2. Verificar permisos de escritura
3. Ver logs del backend para errores específicos

### Problema: "La migración no se aplica"
**Solución**:
```bash
# Entrar al contenedor
docker-compose exec backend bash

# Aplicar manualmente
alembic upgrade head

# Salir
exit
```

### Problema: "Puerto 3001 ocupado"
**Solución**: Cambiar puerto en `docker-compose.yml`:
```yaml
frontend:
  ports:
    - "3002:3000"  # Cambiar 3001 por 3002
```

---

## 📝 Notas Importantes

1. **Seguridad de Archivos**:
   - Los archivos multimedia se guardan con nombres UUID únicos
   - Esto previene colisiones y ataques de path traversal
   - Los archivos NO son públicos por defecto

2. **Tamaño de Archivos**:
   - FastAPI tiene un límite por defecto
   - Para archivos grandes, ajustar en `backend/app/main.py`

3. **Producción**:
   - Cambiar `SECRET_KEY` en variables de entorno
   - Configurar almacenamiento en la nube para archivos (S3, etc.)
   - Implementar sistema de notificaciones en tiempo real

4. **Próximas Mejoras**:
   - Panel de administración para ver alertas en el frontend
   - Notificaciones push a admins
   - Mapa interactivo para ubicar alertas
   - Historial de alertas del usuario

---

## ✅ Checklist de Verificación

- [ ] Docker Compose reiniciado
- [ ] Todos los contenedores corriendo
- [ ] Migraciones aplicadas (ver en logs)
- [ ] Frontend accesible en http://localhost:3001
- [ ] Backend accesible en http://localhost:8000
- [ ] Página de registro funcional
- [ ] Login funcional con nueva cuenta
- [ ] Botón de alertas visible en dashboard
- [ ] Formulario de alertas funcional
- [ ] Subida de fotos funciona
- [ ] Subida de videos funciona
- [ ] Archivos se guardan en `backend/data/alertas/`

---

¡Todo listo para usar! 🎉

Si tienes algún problema, revisa:
1. Los logs: `docker-compose logs -f`
2. El estado de los contenedores: `docker-compose ps`
3. La documentación interactiva de la API: http://localhost:8000/docs
