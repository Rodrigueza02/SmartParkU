# ☁️ Guía de Juliana — Backend en AWS EC2

> Tiempo estimado: **2 – 2.5 horas**
> Estrategia: una sola VM EC2 t2.micro (Free Tier) con Docker Compose
> No se necesita tarjeta de crédito si la cuenta es nueva (12 meses Free Tier)

---

## PASO 0 — Subir el código a GitHub

Antes de tocar AWS, asegurarse de que el repo está actualizado:

```
git add .
git commit -m "chore: agregar archivos de deploy AWS"
git push origin main
```

---

## PASO 1 — Crear cuenta AWS (si no tienen)

1. Ir a **https://aws.amazon.com** → clic en **"Crear una cuenta de AWS"**
2. Necesitan: email, contraseña, número de teléfono, tarjeta de crédito (para verificación — no cobran si usan Free Tier)
3. Seleccionar el plan **"Basic Support - Free"**
4. Una vez dentro, ir a la consola: **https://console.aws.amazon.com**

> ⚠️ Activar alertas de billing AHORA para evitar sorpresas:
> - Ir a **Account → Billing Dashboard → Billing preferences**
> - Activar "Receive Free Tier usage alerts" con tu email
> - Activar "Receive billing alerts" → ir a CloudWatch → Alarms → crear alarma en $1

---

## PASO 2 — Lanzar la instancia EC2

1. En la consola AWS, buscar **EC2** en la barra de búsqueda
2. Clic en **"Launch Instance"**
3. Configurar así:

   **Name:** `SmartParkU-Backend`

   **Amazon Machine Image (AMI):**
   Seleccionar **"Amazon Linux 2023 AMI"** — tiene la etiqueta `Free tier eligible`

   **Instance type:**
   Seleccionar **`t2.micro`** — etiqueta `Free tier eligible` ✅

   **Key pair (login):**
   - Clic en **"Create new key pair"**
   - Name: `smartparku-key`
   - Type: RSA
   - Format: `.pem`
   - Clic **"Create key pair"** — se descarga `smartparku-key.pem` automáticamente
   - **Guardar este archivo en un lugar seguro, no se puede descargar de nuevo**

   **Network settings — Firewall (Security Group):**
   Clic en **"Edit"** y agregar estas reglas:

   | Type | Protocol | Port | Source |
   |---|---|---|---|
   | SSH | TCP | 22 | My IP (se llena automático) |
   | Custom TCP | TCP | 8000 | Anywhere (0.0.0.0/0) |
   | HTTP | TCP | 80 | Anywhere (0.0.0.0/0) |

   **Storage:** dejar el default (8 GB gp3) — suficiente

4. Clic en **"Launch instance"**
5. Esperar ~1 minuto hasta que el estado diga "Running"

---

## PASO 3 — Conectarse a la VM por SSH

1. En la lista de instancias EC2, copiar la **"Public IPv4 address"** (ej: `54.123.45.67`)
2. En tu computadora local, abrir una terminal y ejecutar:

```bash
# Primero dar permisos al archivo de la llave (solo en Mac/Linux)
chmod 400 ~/Downloads/smartparku-key.pem

# Conectarse (reemplazar con tu IP real)
ssh -i ~/Downloads/smartparku-key.pem ec2-user@54.123.45.67
```

> En **Windows**, usar PowerShell:
> ```powershell
> ssh -i "C:\Users\jiliana rodriguez\Downloads\smartparku-key.pem" ec2-user@54.123.45.67
> ```
> Si da error de permisos en Windows, clic derecho en el .pem → Properties → Security → Advanced → quitar herencia → agregar solo tu usuario con Full Control

3. La primera vez pregunta "Are you sure you want to continue connecting?" → escribir `yes`

---

## PASO 4 — Instalar Docker en la VM

Una vez dentro de la VM por SSH, ejecutar estos comandos uno por uno:

```bash
# Descargar el script de instalación desde el repo
curl -o install.sh https://raw.githubusercontent.com/TU_USUARIO/SmartParkU/main/install.sh
bash install.sh
```

**Si no funciona el curl**, copiar y pegar manualmente:

```bash
sudo dnf update -y
sudo dnf install -y docker git python3
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user

# Instalar Docker Compose
sudo curl -SL https://github.com/docker/compose/releases/download/v2.27.0/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

Luego **cerrar la sesión SSH y volver a entrar** para que los permisos de Docker apliquen:
```bash
exit
ssh -i ~/Downloads/smartparku-key.pem ec2-user@54.123.45.67
```

Verificar:
```bash
docker --version        # debe mostrar Docker version 24.x o superior
docker-compose --version  # debe mostrar Docker Compose version 2.x
```

---

## PASO 5 — Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/SmartParkU.git
cd SmartParkU
```

> Reemplazar `TU_USUARIO` con el usuario de GitHub real del repositorio.
> Si el repo es privado, se necesita un Personal Access Token:
> - Ir a GitHub → Settings → Developer settings → Personal access tokens → Generate new token
> - Scope: solo `repo`
> - Usar el token como contraseña cuando git lo pida

---

## PASO 6 — Configurar las variables de entorno

```bash
# Crear el archivo de variables de producción
cp .env.production.example .env.production

# Editarlo (nano es el editor de texto en la terminal)
nano .env.production
```

En el editor, rellenar los valores reales:
- `POSTGRES_PASSWORD` → inventar una contraseña segura (ej: `SmartPark2026!`)
- `DATABASE_URL` → cambiar `CAMBIAR_POR_PASSWORD_SEGURA` por la misma contraseña de arriba
- `SECRET_KEY` → generar una clave:
  ```bash
  python3 -c "import secrets; print(secrets.token_hex(32))"
  ```
  Copiar el resultado y pegarlo como valor de SECRET_KEY
- `MQTT_PASSWORD` → la contraseña real de HiveMQ Cloud

Guardar con: `Ctrl + X` → `Y` → `Enter`

---

## PASO 7 — Hacer el primer deploy

```bash
bash deploy.sh
```

El script:
1. Construye las imágenes Docker (~5-8 minutos la primera vez)
2. Levanta PostgreSQL y espera que esté sano
3. Corre las migraciones de Alembic
4. Pobla los datos iniciales (usuarios y espacios de parqueo)
5. Inicia el servidor FastAPI

Al finalizar verás:
```
  ✅ Deploy completado
  Backend: http://54.123.45.67:8000
  Swagger: http://54.123.45.67:8000/docs
```

---

## PASO 8 — Verificar que funciona

1. Abrir en el navegador: `http://TU_IP_EC2:8000/docs`
2. Deberías ver el Swagger UI de FastAPI
3. Probar `POST /api/v1/auth/login`:
   - email: `admin@ucc.edu.co`
   - password: `admin123`
4. Si responde con un token JWT → ✅ backend funcionando

---

## PASO 9 — Darle la URL a Helen

Compartir con Helen:
- **URL del backend:** `http://TU_IP_EC2:8000`
- **URL del WebSocket:** `ws://TU_IP_EC2:8000/api/v1/parking/ws/parking`

> Nota: sin dominio propio, la URL usa `http://` y `ws://` (sin SSL).
> Para una demo académica está bien así.

---

## Comandos útiles para el futuro

```bash
# Ver logs del backend en tiempo real
docker-compose -f docker-compose.prod.yml logs -f backend

# Ver logs de la base de datos
docker-compose -f docker-compose.prod.yml logs -f db

# Reiniciar solo el backend (sin bajar la BD)
docker-compose -f docker-compose.prod.yml restart backend

# Actualizar cuando haya cambios en el código
bash deploy.sh

# Parar todo (la VM sigue corriendo, solo los contenedores se detienen)
docker-compose -f docker-compose.prod.yml down

# Ver estado de los contenedores
docker-compose -f docker-compose.prod.yml ps
```

---

## Errores comunes y soluciones

| Error | Causa | Solución |
|---|---|---|
| `Permission denied` al hacer SSH | Permisos del .pem incorrectos | `chmod 400 smartparku-key.pem` |
| `Cannot connect to Docker daemon` | No se cerró y reabrió la sesión SSH | Salir con `exit` y volver a entrar |
| `Error: DATABASE_URL not set` | .env.production no existe o está mal | Verificar con `cat .env.production` |
| Build tarda más de 15 min | t2.micro tiene 1 CPU, es lento | Esperar, es normal la primera vez |
| Puerto 8000 no responde | Security Group mal configurado | Verificar que el SG tiene el puerto 8000 abierto |
| `healthy: false` en la BD | PostgreSQL tarda en arrancar | Esperar 30s y correr `bash deploy.sh` de nuevo |
