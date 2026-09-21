# 🚂 Guía de Juliana — Backend en Railway

> Tiempo estimado: **1.5 – 2 horas**
> Prerequisito: tener el repositorio en GitHub (si no está, ver el paso 0)

---

## PASO 0 — Subir el código a GitHub (si no lo han hecho)

En la carpeta `SmartParkU/SmartParkU` (la que tiene el `.git`), ejecutar en la terminal:

```bash
git add .
git commit -m "chore: preparar proyecto para deploy en Railway y Vercel"
git push origin main
```

> ⚠️ Verificar que el `.gitignore` del backend excluya `.env` y la carpeta `venv/`.
> Las credenciales reales NO deben subirse al repo.

---

## PASO 1 — Crear cuenta en Railway

1. Ir a **https://railway.app**
2. Clic en **"Start a New Project"** → **"Login with GitHub"**
3. Autorizar Railway en tu cuenta de GitHub
4. Railway ofrece **$5 de crédito gratis al mes** (Hobby plan) — suficiente para el proyecto
5. No es necesaria tarjeta de crédito para empezar (pero si piden verificación de email, confirmarla)

---

## PASO 2 — Crear la base de datos PostgreSQL

1. En el dashboard de Railway, clic en **"New Project"**
2. Seleccionar **"Deploy PostgreSQL"** (template oficial)
3. Railway crea automáticamente la instancia. Esperar ~30 segundos.
4. Clic en el servicio PostgreSQL creado → pestaña **"Variables"**
5. Copiar el valor de **`DATABASE_URL`** — lo vas a necesitar en el paso 4.
   Tiene este formato:
   ```
   postgresql://postgres:PASSWORD@HOST.railway.internal:5432/railway
   ```

> ⚠️ El `DATABASE_URL` de Railway usa el driver `postgresql://` estándar.
> El backend usa `psycopg` (v3), así que hay que cambiar el prefijo a:
> ```
> postgresql+psycopg://postgres:PASSWORD@HOST.railway.internal:5432/railway
> ```
> Solo agregarle `+psycopg` después de `postgresql`.

---

## PASO 3 — Agregar el backend al proyecto

1. En el mismo proyecto de Railway (el que ya tiene la BD), clic en **"New Service"**
2. Seleccionar **"GitHub Repo"**
3. Buscar el repositorio `SmartParkU` y seleccionarlo
4. Railway va a detectar el `Dockerfile` automáticamente.
   Cuando pregunte la **carpeta raíz del servicio**, escribir: `SmartParkU/backend`
   (o la ruta relativa donde está el `Dockerfile` del backend dentro del repo)
5. **NO hacer deploy todavía** — primero configurar las variables de entorno (paso 4)

---

## PASO 4 — Configurar variables de entorno del backend

En el servicio del backend → pestaña **"Variables"**, agregar cada una:

| Variable | Valor |
|---|---|
| `DATABASE_URL` | El que copiaste en el paso 2, con `+psycopg` |
| `SECRET_KEY` | Una clave larga y aleatoria (ver abajo cómo generarla) |
| `ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` |
| `MQTT_BROKER` | `7de2fa1d05f84c5c8f2fcacca06d98da.s1.eu.hivemq.cloud` |
| `MQTT_PORT` | `8883` |
| `MQTT_USERNAME` | `Juliana` |
| `MQTT_PASSWORD` | La contraseña real de HiveMQ |
| `PORT` | `8000` |

**Cómo generar SECRET_KEY** — ejecutar esto en tu terminal local:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Copiar el resultado y pegarlo como valor de `SECRET_KEY`.

---

## PASO 5 — Hacer el primer deploy

1. Con todas las variables configuradas, ir a la pestaña **"Deployments"** del backend
2. Clic en **"Deploy"** (o hacer un `git push` al repo)
3. Abrir el log en tiempo real — vas a ver:
   ```
   ▶ Corriendo migraciones de base de datos...
   ▶ Poblando datos iniciales...
   ▶ Iniciando servidor FastAPI...
   INFO: Application startup complete.
   ```
4. Si el deploy falla, revisar los logs — el error más común es `DATABASE_URL` mal formado

---

## PASO 6 — Verificar que el backend funciona

1. En Railway, el servicio backend tiene una URL pública automática.
   Tiene este formato: `https://smartparku-backend-xxxx.railway.app`
2. Abrir esa URL en el navegador y agregar `/docs` al final:
   `https://smartparku-backend-xxxx.railway.app/docs`
3. Deberías ver el Swagger UI de FastAPI con todos los endpoints
4. Probar el endpoint `POST /api/v1/auth/login` con:
   - email: `admin@ucc.edu.co`
   - password: `admin123`
5. Si responde con un token JWT, ¡el backend está funcionando perfectamente! ✅

---

## PASO 7 — Darle la URL a Helen

Una vez verificado el paso 6, compartir con Helen:
- La URL del backend: `https://smartparku-backend-xxxx.railway.app`
- La URL del WebSocket: `wss://smartparku-backend-xxxx.railway.app/api/v1/parking/ws/parking`

> ⚠️ Notar que el WebSocket en producción usa `wss://` (con SSL), no `ws://`

---

## Errores comunes y soluciones

| Error en el log | Causa | Solución |
|---|---|---|
| `could not connect to server` | DATABASE_URL incorrecto | Verificar que tiene `+psycopg` y que copiaste bien el host |
| `ModuleNotFoundError` | Dependencia faltante en requirements.txt | Verificar que requirements.txt está completo |
| `Address already in use` | Railway ya asigna PORT automáticamente | Verificar que el start command usa `${PORT:-8000}` |
| Build muy lento (10+ min) | Primera vez, descargando dependencias | Normal, esperar |

---

## Credenciales de prueba (seeded automáticamente)

| Usuario | Contraseña | Rol |
|---|---|---|
| admin@ucc.edu.co | admin123 | SuperAdmin |
| estudiante@ucc.edu.co | estudiante123 | Estudiante |
| admin.campus@ucc.edu.co | admincampus123 | Administrativo |
| visitante@gmail.com | visitante123 | Visitante |
