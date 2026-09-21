# ⚙️ Variables de Entorno — Referencia de Producción

> Este archivo es solo referencia. Los valores reales se configuran en los paneles
> de Railway y Vercel, NO en archivos del repositorio.

---

## Backend (Railway)

| Variable | Ejemplo / Valor fijo | Quién la configura |
|---|---|---|
| `DATABASE_URL` | `postgresql+psycopg://postgres:PASS@HOST.railway.internal:5432/railway` | Juliana — Railway lo genera |
| `SECRET_KEY` | (generar con `python -c "import secrets; print(secrets.token_hex(32))"`) | Juliana |
| `ALGORITHM` | `HS256` | Juliana |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Juliana |
| `MQTT_BROKER` | `7de2fa1d05f84c5c8f2fcacca06d98da.s1.eu.hivemq.cloud` | Juliana |
| `MQTT_PORT` | `8883` | Juliana |
| `MQTT_USERNAME` | `Juliana` | Juliana |
| `MQTT_PASSWORD` | (contraseña real de HiveMQ) | Juliana |
| `PORT` | `8000` | Juliana |

---

## Frontend (Vercel)

| Variable | Valor | Quién la configura |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `https://[url-del-backend].railway.app` | Helen — esperar URL de Juliana |
| `NEXT_PUBLIC_WS_URL` | `wss://[url-del-backend].railway.app/api/v1/parking/ws/parking` | Helen — esperar URL de Juliana |

---

## URLs finales (llenar cuando estén disponibles)

Una vez completado el deploy, anotar aquí las URLs definitivas:

```
Backend (Railway):  https://_________________________________.railway.app
Swagger UI:         https://_________________________________.railway.app/docs
Frontend (Vercel):  https://_________________________________.vercel.app
```

---

## Notas de seguridad importantes

1. **Nunca subir `.env` al repositorio** — el `.gitignore` ya lo excluye, pero verificar antes de cada push
2. **El `SECRET_KEY` generado para producción** debe ser diferente al de desarrollo local
3. **La contraseña de HiveMQ** solo va en las variables de Railway, nunca en el código
4. **Las variables `NEXT_PUBLIC_*`** se embeben en el bundle de JavaScript del frontend —
   son visibles para cualquier usuario del navegador. Solo poner valores que puedan ser públicos
   (URLs del backend están bien, contraseñas nunca)

---

## Checklist de verificación final

### Juliana (Railway)
- [ ] Servicio PostgreSQL creado y running en Railway
- [ ] Backend desplegado y en estado "Active" en Railway
- [ ] `/docs` responde correctamente con Swagger UI
- [ ] Login con `admin@ucc.edu.co` / `admin123` devuelve token JWT
- [ ] URL del backend compartida con Helen

### Helen (Vercel)
- [ ] Proyecto importado con Root Directory = `SmartParkU/frontend`
- [ ] Variables de entorno `NEXT_PUBLIC_API_URL` y `NEXT_PUBLIC_WS_URL` configuradas
- [ ] Deploy exitoso en Vercel
- [ ] Login funciona desde la URL de Vercel
- [ ] Dashboard del parqueadero carga correctamente
- [ ] WebSocket conecta (indicador verde en la UI)

### Prueba conjunta final
- [ ] Desde la app en Vercel, hacer login como admin
- [ ] Simular un evento MQTT desde la Raspberry Pi (o usar `simulador_raspberry.py` en local)
- [ ] Verificar que el estado de los slots se actualiza en tiempo real en el frontend
- [ ] Probar flujo completo de acceso por QR

---

## Costo estimado

| Servicio | Costo mensual |
|---|---|
| Railway Backend | ~$1-2 USD (dentro del crédito gratuito de $5/mes) |
| Railway PostgreSQL | ~$0.50 USD (incluido en el crédito) |
| Vercel Frontend | $0 (plan Hobby gratuito) |
| HiveMQ Cloud | $0 (plan gratuito ya activo) |
| **Total** | **~$0 con los créditos de Railway** |

> Railway da $5 de crédito mensual gratis con solo verificar el email.
> El proyecto debería mantenerse dentro del crédito gratuito con uso normal.
