# ✅ Configuración Inicial Completada - SmartParkU

## 🎉 Estado del Proyecto

**¡El proyecto está funcionando correctamente!**

---

## 🔗 URLs de Acceso

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Frontend (Web)** | http://localhost:3001 | Interfaz web de usuarios |
| **Backend API** | http://localhost:8000 | API REST del sistema |
| **Documentación API** | http://localhost:8000/docs | Swagger UI - Documentación interactiva |
| **pgAdmin** | http://localhost:8080 | Administrador de base de datos |
| **MQTT Broker** | mqtt://localhost:1883 | Broker MQTT local |
| **MQTT WebSocket** | ws://localhost:9001 | WebSocket MQTT para debug |

---

## 👥 Usuarios de Prueba

La base de datos ya tiene usuarios creados. Puedes usar estos para probar:

| Email | Contraseña | Rol | Descripción |
|-------|-----------|-----|-------------|
| `admin@ucc.edu.co` | `admin123` | SuperAdmin | Acceso total al sistema |
| `estudiante@ucc.edu.co` | `estudiante123` | Estudiante | Usuario estudiante estándar |
| `admin.campus@ucc.edu.co` | `admin123` | Administrativo | Personal administrativo |
| `visitante@gmail.com` | `visitante123` | Visitante | Usuario visitante |
| `inactivo@ucc.edu.co` | `inactivo123` | Estudiante | Usuario inactivo (para pruebas) |

---

## 📊 Base de Datos

### Espacios de Parqueo Creados

El sistema tiene **10 espacios** de parqueo inicializados:

- **Carros**: C-01, C-02, C-03, C-04 (4 espacios)
- **Motos**: M-01, M-02, M-03 (3 espacios)
- **Bicicletas**: B-01, B-02 (2 espacios)
- **VIP**: V-01 (1 espacio)

---

## 🐳 Contenedores Docker

Todos los contenedores están corriendo:

```bash
# Ver estado de contenedores
docker ps

# Ver logs de un contenedor
docker logs smartparku_backend
docker logs smartparku_frontend
docker logs smartparku_db
```

---

## 🚀 Comandos Útiles

### Iniciar el Proyecto
```powershell
docker-compose up -d
```

### Detener el Proyecto
```powershell
docker-compose down
```

### Reiniciar un Servicio
```powershell
docker-compose restart backend
docker-compose restart frontend
```

### Ver Logs en Tiempo Real
```powershell
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Ejecutar Comandos en el Backend
```powershell
# Entrar al contenedor
docker exec -it smartparku_backend bash

# Ejecutar migraciones
docker exec smartparku_backend alembic upgrade head

# Cargar datos iniciales
docker exec smartparku_backend python app/initial_data.py
```

### Ejecutar Comandos en Frontend (Local)
```powershell
cd frontend
npm run dev        # Modo desarrollo
npm run build      # Compilar para producción
npm run lint       # Verificar código
```

---

## 🔧 Configuración Aplicada

### Backend (.env)
- ✅ Base de datos PostgreSQL configurada
- ✅ JWT secret key configurada
- ✅ MQTT HiveMQ Cloud configurado
- ✅ Migraciones ejecutadas
- ✅ Datos iniciales cargados

### Frontend
- ✅ Dependencias instaladas (React 18, Next.js 14)
- ✅ TypeScript configurado
- ✅ TailwindCSS configurado
- ✅ Zustand para gestión de estado
- ✅ API URL configurada

### Base de Datos
- ✅ PostgreSQL 15 corriendo
- ✅ Tablas creadas (usuarios, vehículos, accesos, espacios)
- ✅ Índices optimizados
- ✅ Datos de prueba cargados

---

## 📱 Aplicación Móvil (Opcional)

Si quieres probar la app móvil en Flutter:

```bash
cd mobile
flutter pub get
flutter doctor
flutter run
```

Ver `mobile/CONFIGURACION_DISPOSITIVO_FISICO.md` para más detalles.

---

## ⚠️ Notas Importantes

### Vulnerabilidades de Seguridad
- Hay algunas vulnerabilidades de dependencias reportadas por npm
- Son mayormente en dependencias de desarrollo, no afectan producción
- Para actualizar en el futuro: `npm audit fix`

### MQTT
- El sistema usa **HiveMQ Cloud** para producción
- Broker local **Mosquitto** disponible para desarrollo offline
- Credenciales configuradas en docker-compose.yml y backend/.env

### Puertos
- Si algún puerto está ocupado, puedes cambiarlos en `docker-compose.yml`
- Frontend usa 3001 (en lugar de 3000 por conflicto con otros servicios)

---

## 🧪 Probar el Sistema

### 1. Verificar que todo está corriendo
```powershell
curl http://localhost:8000/docs     # Backend API docs
curl http://localhost:3001          # Frontend
```

### 2. Login en el Frontend
1. Abre http://localhost:3001
2. Usa `admin@ucc.edu.co` / `admin123`
3. Explora el dashboard

### 3. Probar API directamente
1. Abre http://localhost:8000/docs
2. Expande `/api/v1/auth/login`
3. Click en "Try it out"
4. Ingresa credenciales y prueba

---

## 📚 Documentación Adicional

El proyecto incluye guías detalladas:
- `GUIA_COMPLETA_SISTEMA_QR.md` - Sistema de códigos QR
- `GUIA_PRUEBAS.md` - Guía de pruebas
- `INSTRUCCIONES_PRUEBA.md` - Instrucciones de prueba
- `PROYECTO_ESTADO.md` - Estado del proyecto

---

## 🆘 Solución de Problemas

### Los contenedores no inician
```powershell
# Verificar Docker Desktop esté corriendo
docker ps

# Reiniciar Docker Desktop si es necesario
# Luego reiniciar los contenedores
docker-compose down
docker-compose up -d
```

### Error de conexión a base de datos
```powershell
# Verificar que el contenedor db esté healthy
docker ps

# Ver logs
docker logs smartparku_db
```

### Frontend no muestra cambios
```powershell
# Limpiar caché y rebuildir
docker-compose down
docker-compose build --no-cache frontend
docker-compose up -d
```

### Error en TypeScript local
```powershell
cd frontend
npm install --legacy-peer-deps
```

---

## ✅ Checklist de Instalación

- [x] Docker Desktop instalado y corriendo
- [x] Archivo `.env` creado y configurado
- [x] Carpetas de volúmenes creadas
- [x] Contenedores levantados con `docker-compose up -d`
- [x] Migraciones de base de datos ejecutadas
- [x] Datos iniciales cargados
- [x] Dependencias de frontend instaladas localmente
- [x] Backend accesible en http://localhost:8000
- [x] Frontend accesible en http://localhost:3001

---

**¡El proyecto SmartParkU está listo para usar! 🎉**
