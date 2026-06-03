@echo off
REM SmartParkU - Simula un sensor HC-SR04 enviando distancias via MQTT
REM Ejecutar en DOS/CMD con Mosquitto instalado en C:\Program Files\mosquitto\

SET BROKER=7de2fa1d05f84c5c8f2fcacca06d98da.s1.eu.hivemq.cloud
SET USUARIO=Juliana
SET PASSWORD=1138524566Juli*

echo === SmartParkU - Simulador de sensor ===
echo.

REM Vehículo detectado en cajón 1 (distancia 8 cm = ocupado)
echo [1/3] Publicando: Cajón 1 OCUPADO (8 cm)...
"C:\Program Files\mosquitto\mosquitto_pub.exe" -h %BROKER% -p 8883 -u %USUARIO% -P "%PASSWORD%" -t "sensores/ultrasonico" -m "{\"slot\":\"1\",\"distancia\":8,\"tipo\":\"carro\"}" --insecure

timeout /t 2 >nul

REM Cajón 5 libre (50 cm)
echo [2/3] Publicando: Cajón 5 LIBRE (50 cm)...
"C:\Program Files\mosquitto\mosquitto_pub.exe" -h %BROKER% -p 8883 -u %USUARIO% -P "%PASSWORD%" -t "sensores/ultrasonico" -m "{\"slot\":\"5\",\"distancia\":50,\"tipo\":\"carro\"}" --insecure

timeout /t 2 >nul

REM Estado de la barrera
echo [3/3] Publicando: Barrera ABIERTA...
"C:\Program Files\mosquitto\mosquitto_pub.exe" -h %BROKER% -p 8883 -u %USUARIO% -P "%PASSWORD%" -t "parqueadero/entrada" -m "{\"libre\":true}" --insecure

echo.
echo === Datos enviados. Verifica el dashboard en http://localhost:3000 ===
pause
