# -*- coding: utf-8 -*-
"""
SmartParkU - Suscriptor MQTT (paho-mqtt 2.x)
Escucha todos los topicos de sensores y los imprime en consola.

Modos de uso:
  - HiveMQ Cloud (produccion):  python dashboard_mqtt.py
  - Mosquitto local (Docker):   python dashboard_mqtt.py --local
"""
import ssl
import sys
import json
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
from dotenv import load_dotenv
import os

load_dotenv()

# Detectar si se pasa --local para usar Mosquitto del docker-compose
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
        print(f"[OK] Conectado al broker HiveMQ")
        # Suscribirse a TODO para ver que topicos usa la Raspberry
        client.subscribe("#")
        print("[OK] Escuchando TODOS los topicos (#)\n")
    else:
        print(f"[ERROR] Conexion rechazada, codigo: {reason_code}")


def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    try:
        data = json.loads(payload)
        print(f"[{msg.topic}]  {json.dumps(data, ensure_ascii=False)}")
    except ValueError:
        print(f"[{msg.topic}]  {payload}")


def on_disconnect(client, userdata, flags, reason_code, properties):
    if reason_code != 0:
        print(f"[WARN] Desconectado inesperadamente (codigo {reason_code})")


# API version 2 (paho-mqtt >= 2.0)
client = mqtt.Client(
    callback_api_version=CallbackAPIVersion.VERSION2,
    client_id="smartparku-dashboard-pc",
    protocol=mqtt.MQTTv311,
)

if not USE_LOCAL:
    client.username_pw_set(USERNAME, PASSWORD)
    client.tls_set(cert_reqs=ssl.CERT_NONE)
    client.tls_insecure_set(True)

client.on_connect    = on_connect
client.on_message    = on_message
client.on_disconnect = on_disconnect

print(f"[...] Conectando a {BROKER}:{PORT} ...")
if not USE_LOCAL:
    print(f"      Usuario: {USERNAME}")
print(f"      Puerto:  {PORT}\n")

try:
    client.connect(BROKER, PORT, keepalive=60)
    client.loop_forever()
except Exception as e:
    print(f"\n[ERROR] No se pudo conectar: {e}")
    if USE_LOCAL:
        print("\nVerifica que el docker-compose esté corriendo: docker compose ps")
    else:
        print("\nPosibles causas:")
        print("  1. Sin conexion a internet")
        print("  2. Puerto 8883 bloqueado por firewall/antivirus")
        print("  3. Credenciales incorrectas en el .env")
        print("\nVerifica con: ping 7de2fa1d05f84c5c8f2fcacca06d98da.s1.eu.hivemq.cloud")
