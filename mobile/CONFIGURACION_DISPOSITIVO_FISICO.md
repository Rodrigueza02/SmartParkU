# 📱 Configuración para Dispositivo Físico - SmartParkU Mobile

Esta guía te ayudará a configurar la aplicación móvil de SmartParkU para ejecutarla en un dispositivo físico Android o iOS.

---

## 🔧 Requisitos Previos

- Flutter SDK instalado (versión 3.x o superior)
- Dispositivo físico Android o iOS
- Cable USB para conectar el dispositivo
- Backend de SmartParkU corriendo en tu máquina local

---

## 📍 PASO 1: Obtener la IP de tu Computadora

### En Windows:
1. Abre el **Símbolo del sistema** (CMD) o **PowerShell**
2. Ejecuta:
   ```bash
   ipconfig
   ```
3. Busca la sección **Adaptador de LAN inalámbrica Wi-Fi** o **Adaptador de Ethernet**
4. Anota la dirección **IPv4**. Ejemplo: `192.168.1.100`

### En macOS/Linux:
1. Abre la **Terminal**
2. Ejecuta:
   ```bash
   ifconfig
   ```
   O:
   ```bash
   ip addr show
   ```
3. Busca la interfaz activa (generalmente `en0` para Wi-Fi o `eth0` para Ethernet)
4. Anota la dirección **inet**. Ejemplo: `192.168.1.100`

### Verificación:
⚠️ **IMPORTANTE**: Tu dispositivo móvil debe estar en la **misma red Wi-Fi** que tu computadora.

---

## 🌐 PASO 2: Configurar las URLs del Backend

Edita el archivo de configuración de la API:

**Archivo**: `mobile/lib/core/constants/api.dart`

### Configuración actual (para emulador):
```dart
class ApiConstants {
  // Emulador Android apunta a localhost del host
  static const String baseUrl = 'http://10.0.2.2:8000';
  static const String wsUrl = 'ws://10.0.2.2:8000';
}
```

### Configuración para dispositivo físico:
```dart
class ApiConstants {
  // Reemplaza 192.168.1.100 con la IP de tu computadora
  static const String baseUrl = 'http://192.168.1.100:8000';
  static const String wsUrl = 'ws://192.168.1.100:8000';
}
```

### Ejemplo completo del archivo actualizado:
```dart
class ApiConstants {
  // IMPORTANTE: Cambia esta IP por la de tu computadora
  static const String baseUrl = 'http://192.168.1.100:8000';
  static const String wsUrl = 'ws://192.168.1.100:8000';
  
  // Endpoints de autenticación
  static const String loginEndpoint = '/api/v1/auth/login';
  static const String forgotPasswordEndpoint = '/api/v1/auth/forgot-password';
  static const String resetPasswordEndpoint = '/api/v1/auth/reset-password';
  
  // Endpoints de parqueadero
  static const String parkingSlotsEndpoint = '/api/v1/parking/slots';
  static const String parkingWebSocket = '/api/v1/parking/ws/parking';
  
  // Endpoints de QR
  static const String generateQREndpoint = '/api/v1/qr/generar';
  static const String scanQREndpoint = '/api/v1/qr/escanear';
  
  // Endpoints de accesos
  static const String accesosByUserEndpoint = '/api/v1/accesos/usuario';
  static const String registrarSalidaEndpoint = '/api/v1/accesos';
}
```

---

## 📱 PASO 3: Configurar el Dispositivo Android

### Habilitar modo desarrollador:
1. Ve a **Configuración** → **Acerca del teléfono**
2. Toca **Número de compilación** 7 veces
3. Aparecerá el mensaje "Ahora eres desarrollador"

### Habilitar depuración USB:
1. Ve a **Configuración** → **Opciones de desarrollador**
2. Activa **Depuración USB**
3. Activa **Instalar aplicaciones via USB** (si está disponible)

### Conectar el dispositivo:
1. Conecta el dispositivo a la computadora con el cable USB
2. En el dispositivo, acepta el mensaje "¿Permitir depuración USB?"
3. Marca la opción "Permitir siempre desde este equipo"

### Verificar conexión:
```bash
flutter devices
```

Deberías ver tu dispositivo en la lista:
```
Android SDK built for x86 (mobile) • emulator-5554 • android-x86 • Android 11 (API 30)
SM-G991B (mobile) • RFCR12345AB • android-arm64 • Android 13 (API 33)
```

---

## 🍎 PASO 4: Configurar el Dispositivo iOS (macOS solamente)

### Requisitos:
- Xcode instalado
- Cuenta de desarrollador de Apple (gratuita o de pago)
- Cable Lightning/USB-C para conectar el iPhone

### Pasos:
1. Abre Xcode
2. Ve a **Preferences** → **Accounts**
3. Agrega tu Apple ID
4. Conecta el iPhone a la Mac
5. En el iPhone, ve a **Configuración** → **General** → **Gestión de dispositivos**
6. Confía en tu certificado de desarrollador

### Verificar conexión:
```bash
flutter devices
```

---

## 🚀 PASO 5: Ejecutar la Aplicación

### Iniciar el backend:
Asegúrate de que el backend esté corriendo:
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

⚠️ **IMPORTANTE**: Usa `--host 0.0.0.0` para que el backend sea accesible desde otros dispositivos en la red.

### Compilar y ejecutar:
```bash
cd mobile
flutter pub get
flutter run
```

Si tienes múltiples dispositivos conectados:
```bash
flutter run -d <device-id>
```

Para ver los dispositivos disponibles:
```bash
flutter devices
```

---

## 🧪 PASO 6: Probar la Conexión

### Test de conectividad:

1. **Abrir la app** en el dispositivo físico
2. **Intentar login**:
   - Email: `estudiante@ucc.edu.co`
   - Password: `estudiante123`

3. **Si no conecta**, verifica:
   - ✅ Backend corriendo con `--host 0.0.0.0`
   - ✅ Ambos dispositivos en la misma red Wi-Fi
   - ✅ IP correcta en `api.dart`
   - ✅ Firewall no bloquea el puerto 8000

### Probar desde el navegador del móvil:
Abre el navegador en tu dispositivo y visita:
```
http://192.168.1.100:8000/docs
```
(Reemplaza con tu IP)

Si ves la documentación de FastAPI, la conexión funciona correctamente.

---

## 🛠 Solución de Problemas

### Error: "Network unreachable" o "Connection refused"

**Solución 1**: Verifica el firewall
- Windows: Permite el puerto 8000 en el Firewall de Windows
- macOS: Ve a **Preferencias del Sistema** → **Seguridad y Privacidad** → **Cortafuegos**

**Solución 2**: Verifica que ambos dispositivos estén en la misma red
```bash
# En tu computadora, verifica la IP
ipconfig   # Windows
ifconfig   # macOS/Linux

# Debe coincidir con la red Wi-Fi de tu móvil
```

**Solución 3**: Prueba con la IP externa
Si estás en una red corporativa o universitaria, es posible que necesites usar la IP externa o configurar port forwarding.

---

### Error: "Certificate verify failed" (iOS)

**Solución**: El WebSocket usa `ws://` (no seguro). Para desarrollo, esto está bien. En producción, usa `wss://` con certificados SSL.

---

### Error: "Clear text traffic not permitted" (Android 9+)

Ya está configurado en el proyecto. Si aún aparece el error, verifica que `android/app/src/main/AndroidManifest.xml` contenga:

```xml
<application
    android:usesCleartextTraffic="true"
    ...>
```

---

## 📝 Configuración para Producción

Cuando despliegues a producción, actualiza las URLs:

```dart
class ApiConstants {
  static const String baseUrl = 'https://api.smartparku.ucc.edu.co';
  static const String wsUrl = 'wss://api.smartparku.ucc.edu.co';
}
```

Y asegúrate de:
- ✅ Usar HTTPS/WSS
- ✅ Certificados SSL válidos
- ✅ Quitar `usesCleartextTraffic` en Android
- ✅ Configurar App Transport Security en iOS

---

## ✅ Checklist Final

- [ ] Backend corriendo con `--host 0.0.0.0`
- [ ] IP de tu computadora obtenida
- [ ] Archivo `api.dart` actualizado con la IP correcta
- [ ] Dispositivo y computadora en la misma red Wi-Fi
- [ ] Depuración USB habilitada (Android) o certificado confiado (iOS)
- [ ] App compilada y ejecutada con `flutter run`
- [ ] Login funciona correctamente
- [ ] Mapa se actualiza en tiempo real

---

## 🎯 Comandos Útiles

```bash
# Ver todos los dispositivos
flutter devices

# Ejecutar en un dispositivo específico
flutter run -d <device-id>

# Ver logs en tiempo real
flutter logs

# Limpiar caché y reconstruir
flutter clean
flutter pub get
flutter run

# Construir APK para Android (release)
flutter build apk --release

# Construir para iOS (requiere macOS)
flutter build ios --release
```

---

## 📞 Soporte

Si encuentras problemas:

1. Revisa los logs del backend: verifica que las peticiones lleguen
2. Revisa los logs de Flutter: `flutter logs`
3. Prueba primero en el emulador con `10.0.2.2`
4. Verifica que los endpoints del backend funcionen desde Postman o el navegador

---

**¡Listo!** Ahora puedes probar SmartParkU en tu dispositivo físico. 🚀
