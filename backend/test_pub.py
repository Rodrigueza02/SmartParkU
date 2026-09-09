# -*- coding: utf-8 -*-
"""
SmartParkU - Test rápido de publicación MQTT (paho-mqtt 2.x)

Prueba la integración con el broker enviando comandos de talanquera
y actualizaciones de estado de la barrera.

Ya NO publica mensajes de sensores de ocupación de celda — eso se
gestiona exclusivamente vía API REST (escaneo QR desde la app).

Modos de uso:
  - HiveMQ Cloud (produccion):  python test_pub.py
  - Mosquitto local (Docker):   python test_pub.py --local
"""
import ssl
import sys
import json
import time
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
from dotenv import load_dotenv
import os

load_dotenv()

USE_LOCAL = "--local" in sys.argv

if USE_LOCAL:
    BROKER   = "localhost"
    PORT     = 1883
    USERNAME = ""
    PASSWORD = ""
    print("[INFO] Modo LOCAL — conectando a Mosquitto en localhost:1883 (sin TLS)\n")
else:
    BROKER   = os.getenv("MQTT_BROKER",   "7de2fa1d05f84c5c8f2fcacca06d98da.s1.eu.hivemq.cloud")
    PORT     = int(os.getenv("MQTT_PORT", "8883"))
    USERNAME = os.getenv("MQTT_USERNAME", "Juliana")
    PASSWORD = os.getenv("MQTT_PASSWORD", "1138524566Juli*")
    print("[INFO] Modo CLOUD — conectando a HiveMQ en puerto 8883 (TLS)\n")


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print(f"[OK] Conectado a {BROKER}")
        print("[...] Enviando mensajes de prueba...\n")

        # Test 1: Abrir talanquera
        client.publish("talanquera/control", json.dumps({"angulo": 90, "accion": "abrir"}))
        print("[->] talanquera/control  angulo=90  accion=abrir  → BARRERA ABIERTA")
        time.sleep(1)

        # Test 2: Barrera principal marcada como libre (abierta)
        client.publish("parqueadero/entrada", json.dumps({"libre": True}))
        print("[->] parqueadero/entrada  libre=true  → BARRERA ABIERTA")
        time.sleep(1)

        # Test 3: Cerrar talanquera
        client.publish("talanquera/control", json.dumps({"angulo": 0, "accion": "cerrar"}))
        print("[->] talanquera/control  angulo=0   accion=cerrar → BARRERA CERRADA")
        time.sleep(1)

        # Test 4: Barrera cerrada
        client.publish("parqueadero/entrada", json.dumps({"libre": False}))
        print("[->] parqueadero/entrada  libre=false → BARRERA CERRADA")

        print("\n[OK] Mensajes de prueba enviados.")
        print("     Nota: el estado de ocupación de celdas se gestiona via API REST (QR).")
        client.disconnect()
    else:
        codigos = {
            1: "Version de protocolo incorrecta",
            2: "Identificador de cliente rechazado",
            3: "Servidor no disponible",
            4: "Usuario o contrasena incorrectos",
            5: "No autorizado",
        }
        print(f"[ERROR] {codigos.get(int(str(reason_code)), str(reason_code))}")
        client.disconnect()


def on_disconnect(client, userdata, flags, reason_code, properties):
    print("[--] Desconectado")


client = mqtt.Client(
    callback_api_version=CallbackAPIVersion.VERSION2,
    client_id="smartparku-test-pub",
    protocol=mqtt.MQTTv311,
)

if not USE_LOCAL:
    client.username_pw_set(USERNAME, PASSWORD)
    client.tls_set(cert_reqs=ssl.CERT_NONE)
    client.tls_insecure_set(True)

client.on_connect    = on_connect
client.on_disconnect = on_disconnect

print(f"[...] Conectando a {BROKER}:{PORT} ...")
try:
    client.connect(BROKER, PORT, keepalive=60)
    client.loop_forever()
except Exception as e:
    print(f"[ERROR] {e}")
    if USE_LOCAL:
        print("\nVerifica que el docker-compose esté corriendo: docker compose ps")
    else:
        print("\nVerifica con: ping 7de2fa1d05f84c5c8f2fcacca06d98da.s1.eu.hivemq.cloud")
