# ▲ Guía de Helen — Frontend en Vercel

> Tiempo estimado: **30 – 45 minutos**
> Prerequisito: que Juliana haya completado su guía y te haya pasado la URL del backend

---

## PASO 1 — Crear cuenta en Vercel

1. Ir a **https://vercel.com**
2. Clic en **"Sign Up"** → **"Continue with GitHub"**
3. Autorizar Vercel en tu cuenta de GitHub
4. El plan **Hobby (gratuito)** es suficiente — no pedir el Pro
5. Confirmar el email si lo solicita

---

## PASO 2 — Importar el proyecto

1. En el dashboard de Vercel, clic en **"Add New..."** → **"Project"**
2. Seleccionar el repositorio `SmartParkU` de la lista
3. Vercel muestra la configuración del proyecto. Ajustar:
   - **Framework Preset**: `Next.js` (se detecta automáticamente ✅)
   - **Root Directory**: clic en **"Edit"** → escribir `SmartParkU/frontend`
     (la carpeta donde está el `package.json` del frontend)
   - **Build Command**: `npm run build` (ya viene por defecto ✅)
   - **Output Directory**: `.next` (ya viene por defecto ✅)

---

## PASO 3 — Configurar variables de entorno

**Antes de hacer el primer deploy**, expandir la sección **"Environment Variables"** y agregar:

| Variable | Valor |
|---|---|
| `NEXT_PUBLIC_API_URL` | `https://URL-DEL-BACKEND-DE-JULIANA.railway.app` |
| `NEXT_PUBLIC_WS_URL` | `wss://URL-DEL-BACKEND-DE-JULIANA.railway.app/api/v1/parking/ws/parking` |

> ⚠️ Importante:
> - La URL del backend usa `https://` (no http)
> - La URL del WebSocket usa `wss://` (no ws) — es el equivalente seguro de WebSocket
> - No poner barra `/` al final de la URL del backend
> - Pedirle a Juliana la URL exacta de Railway antes de continuar

---

## PASO 4 — Hacer el primer deploy

1. Con las variables configuradas, clic en **"Deploy"**
2. Vercel empieza el build automáticamente. Verás los logs en tiempo real.
3. El build tarda ~2-3 minutos la primera vez.
4. Al terminar, Vercel muestra: **"Congratulations! Your project has been successfully deployed"** 🎉
5. La URL del frontend es algo como: `https://smart-park-u-xxxx.vercel.app`

---

## PASO 5 — Verificar que el frontend funciona

1. Abrir la URL de Vercel en el navegador
2. Debería cargar la pantalla de login de SmartParkU
3. Iniciar sesión con:
   - Email: `admin@ucc.edu.co`
   - Contraseña: `admin123`
4. Verificar que:
   - [ ] El login funciona y muestra el dashboard
   - [ ] El mapa del parqueadero carga (aunque los slots estén en estado inicial)
   - [ ] No hay errores en la consola del navegador (`F12` → Console)

---

## PASO 6 — Si el WebSocket no conecta

El WebSocket (`wss://`) puede tardar unos segundos en conectar la primera vez. Si el dashboard muestra "Backend no disponible" pero el login funciona, es normal — esperar 5-10 segundos y recargar.

Si persiste, revisar:
1. Abrir `F12` → Console → buscar errores que digan `WebSocket connection to...`
2. Verificar que `NEXT_PUBLIC_WS_URL` tiene `wss://` y no `ws://`
3. Confirmar con Juliana que el backend en Railway está desplegado correctamente

---

## PASO 7 — Re-deploy cuando haya cambios

Cada vez que hagan `git push` al repositorio, Vercel hace un re-deploy automático del frontend. No hay que hacer nada manual.

---

## Errores comunes y soluciones

| Error | Causa | Solución |
|---|---|---|
| Build falla con error de TypeScript | Hay un error de tipos en el código | El `next.config.js` tiene `ignoreBuildErrors: true`, no debería pasar |
| "Failed to fetch" en login | `NEXT_PUBLIC_API_URL` incorrecto o backend caído | Verificar la URL con Juliana, confirmar que Railway está up |
| Página en blanco | Error de JavaScript | `F12` → Console para ver el error exacto |
| "Root directory not found" | La carpeta raíz está mal configurada | Ir a Settings → General → Root Directory y corregir a `SmartParkU/frontend` |

---

## Cambiar la URL del backend después del deploy

Si Juliana cambia la URL del backend por alguna razón:

1. Ir a Vercel → Proyecto → **Settings** → **Environment Variables**
2. Editar `NEXT_PUBLIC_API_URL` y `NEXT_PUBLIC_WS_URL` con los nuevos valores
3. Ir a **Deployments** → clic en los tres puntos del último deploy → **"Redeploy"**
