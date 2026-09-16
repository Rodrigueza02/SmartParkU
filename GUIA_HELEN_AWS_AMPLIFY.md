# ☁️ Guía de Helen — Frontend en AWS Amplify

> Tiempo estimado: **30 – 45 minutos**
> Prerequisito: que Juliana haya terminado su guía y te haya pasado la IP de la EC2

---

## PASO 1 — Entrar a AWS con cuenta de Juliana

Usar las credenciales de AWS de Juliana (la misma cuenta).

1. Ir a **https://console.aws.amazon.com**
2. Iniciar sesión con el email y contraseña de la cuenta AWS

> Si Juliana quiere darte acceso independiente, puede crear un usuario IAM:
> IAM → Users → Add user → nombre: "helen" → attach policy: "AdministratorAccess"
> Te manda el link de login y las credenciales por separado.
> Para la demo, también pueden trabajar desde la misma cuenta.

---

## PASO 2 — Abrir AWS Amplify

1. En la barra de búsqueda de la consola AWS, buscar **"Amplify"**
2. Clic en **"AWS Amplify"**
3. Asegurarse de estar en la región correcta (arriba a la derecha) — usar la misma que usó Juliana para la EC2 (ej: `us-east-1`)

---

## PASO 3 — Crear la app en Amplify

1. Clic en **"Create new app"**
2. Seleccionar **"GitHub"** como fuente del código
3. Clic en **"Next"** → autorizar AWS Amplify en GitHub si es la primera vez
4. Seleccionar el repositorio `SmartParkU`
5. Seleccionar la rama `main`
6. Clic en **"Next"**

---

## PASO 4 — Configurar el build

Amplify detecta Next.js automáticamente. Pero hay que ajustar la carpeta raíz:

1. En la pantalla "App settings", buscar **"App root"** o **"Monorepo root"**
2. Escribir: `SmartParkU/frontend`
   (es la carpeta donde está el `package.json` del frontend)
3. El `amplify.yml` que genera automáticamente debería verse así:

```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - npm install
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: .next
    files:
      - '**/*'
  cache:
    paths:
      - node_modules/**/*
```

Si no lo genera solo, puedes pegarlo manualmente en el editor que aparece.

---

## PASO 5 — Agregar las variables de entorno

En la misma pantalla de configuración, buscar **"Advanced settings"** o **"Environment variables"**:

Agregar estas dos variables:

| Variable | Valor |
|---|---|
| `NEXT_PUBLIC_API_URL` | `http://IP_DE_EC2_DE_JULIANA:8000` |
| `NEXT_PUBLIC_WS_URL` | `ws://IP_DE_EC2_DE_JULIANA:8000/api/v1/parking/ws/parking` |

> Reemplazar `IP_DE_EC2_DE_JULIANA` con la IP real que te pasó Juliana.
> Ejemplo: `http://54.123.45.67:8000`

---

## PASO 6 — Primer deploy

1. Clic en **"Save and deploy"**
2. Amplify inicia el build automáticamente. Verás las etapas:
   - Provision → Build → Deploy → Verify
3. Tarda ~3-5 minutos
4. Al terminar, Amplify da una URL tipo:
   `https://main.d1abc123.amplifyapp.com`

---

## PASO 7 — Verificar que funciona

1. Abrir la URL de Amplify en el navegador
2. Debería aparecer la pantalla de login de SmartParkU
3. Iniciar sesión con:
   - Email: `admin@ucc.edu.co`
   - Contraseña: `admin123`
4. Verificar:
   - [ ] Login funciona y muestra el dashboard
   - [ ] El mapa del parqueadero carga con los 10 slots
   - [ ] No hay errores en `F12` → Console

---

## Si el build falla en Amplify

El error más común es que Amplify no encuentra la carpeta raíz correcta.

**Solución:**
1. Ir a la app en Amplify → **App settings** → **Build settings**
2. Verificar que "App root directory" dice `SmartParkU/frontend`
3. Si no, editarlo y hacer **"Redeploy this version"**

Otro error común es que TypeScript o ESLint fallan. El `next.config.js` ya tiene:
```js
typescript: { ignoreBuildErrors: true }
eslint: { ignoreDuringBuilds: true }
```
Así que esto no debería ser un problema.

---

## PASO 8 — Re-deploy automático

A partir de ahora, cada `git push` al repositorio hace un re-deploy automático del frontend. No hay que hacer nada manual.

---

## Cambiar la URL del backend

Si Juliana reinicia la EC2, la IP pública puede cambiar (AWS asigna IPs dinámicas).

Si eso pasa:
1. Amplify → App → **Environment variables**
2. Editar `NEXT_PUBLIC_API_URL` y `NEXT_PUBLIC_WS_URL` con la nueva IP
3. Amplify → **Deployments** → clic en el último deploy → **"Redeploy"**

> Para evitar que la IP cambie, Juliana puede asignar una **Elastic IP** a la EC2
> (es gratis mientras la instancia esté corriendo).
> EC2 → Elastic IPs → Allocate → Associate con la instancia.

---

## Costo de Amplify

AWS Amplify tiene capa gratuita:
- **1,000 minutos de build** por mes (gratis)
- **15 GB de almacenamiento** (gratis)
- **15 GB de transferencia** (gratis)

Para un proyecto académico, esto es más que suficiente y no genera cobros.
