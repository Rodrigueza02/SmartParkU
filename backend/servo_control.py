# -*- coding: utf-8 -*-
"""
SmartParkU - Control de talanquera (servo SG90 en Raspberry Pi)
Publica en el topico que escucha la Raspberry: talanquera/control
Formato: {"accion": "abrir"} o {"accion": "cerrar"}

Uso:
    python servo_control.py             -> abre la talanquera
    python servo_control.py --cerrar    -> cierra la talanquera
"""
import ssl
import json
import argparse
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
from dotenv import load_dotenv
import os

load_dotenv()

BROKER   = os.getenv("MQTT_BROKER",   "7de2fa1d05f84c5c8f2fcacca06d98da.s1.eu.hivemq.cloud")
PORT     = int(os.getenv("MQTT_PORT", "8883"))
USERNAME = os.getenv("MQTT_USERNAME", "Juliana")
PASSWORD = os.getenv("MQTT_PASSWORD", "")

# Topico que escucha el script de la Raspberry
TOPIC_SERVO = "talanquera/control"


def enviar_comando(accion: str):
    """Publica un comando de accion al servo de la Raspberry."""

    def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            print(f"[OK] Conectado al broker")
            mensaje = {"accion": accion, "angulo": 90 if accion == "abrir" else 0}
            client.publish(TOPIC_SERVO, json.dumps(mensaje))
            print(f"[->] Comando enviado a {TOPIC_SERVO}: {json.dumps(mensaje)}")
            print(f"     La Raspberry deberia {accion} la talanquera ahora.")
            client.disconnect()
        else:
            print(f"[ERROR] Conexion rechazada, codigo: {reason_code}")
            client.disconnect()

    def on_disconnect(client, userdata, flags, reason_code, properties):
        print(f"[--] Desconectado")

    client = mqtt.Client(
        callback_api_version=CallbackAPIVersion.VERSION2,
        client_id="smartparku-servo-pc",
        protocol=mqtt.MQTTv311,
    )
    client.username_pw_set(USERNAME, PASSWORD)
    client.tls_set(cert_reqs=ssl.CERT_NONE)
    client.tls_insecure_set(True)
    client.on_connect    = on_connect
    client.on_disconnect = on_disconnect

    try:
        client.connect(BROKER, PORT, keepalive=60)
        client.loop_forever()
    except Exception as e:
        print(f"[ERROR] {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Controla la talanquera de SmartParkU")
    parser.add_argument("--cerrar", action="store_true", help="Cierra la talanquera (default: abre)")
    args = parser.parse_args()

    accion = "cerrar" if args.cerrar else "abrir"
    print(f"[...] Enviando comando: {accion} talanquera...")
    enviar_comando(accion)
