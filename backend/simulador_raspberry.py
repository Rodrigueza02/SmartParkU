# -*- coding: utf-8 -*-
"""
SmartParkU - Simulador de Raspberry Pi (Solo talanquera / servo)

Escucha el tópico MQTT de control de la talanquera y simula la respuesta
del hardware (servo SG90). Ya NO simula sensores de ocupación de celda —
el estado de cada puesto se gestiona mediante escaneo de QR desde la app.

Ejecutar con:
    python simulador_raspberry.py

Tópicos que escucha:
    talanquera/control   → comando de abrir/cerrar (publicado por el backend)

Tópicos que publica:
    servo/estado         → confirmación de la acción ejecutada
    parqueadero/entrada  → estado de la barrera principal (libre/cerrada)
"""
import ssl
import json
import time
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os

load_dotenv()

BROKER   = os.getenv("MQTT_BROKER",   "7de2fa1d05f84c5c8f2fcacca06d98da.s1.eu.hivemq.cloud")
PORT     = int(os.getenv("MQTT_PORT", "8883"))
USERNAME = os.getenv("MQTT_USERNAME", "Juliana")
PASSWORD = os.getenv("MQTT_PASSWORD", "1138524566Juli*")


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[OK] Simulador conectado al broker HiveMQ")
        client.subscribe("talanquera/control")
        print("[OK] Escuchando talanquera/control ...\n")
        # Publicar estado inicial: barrera cerrada
        client.publish("parqueadero/entrada", json.dumps({"libre": False}))
        print("[INFO] Estado inicial publicado → barrera CERRADA")
    else:
        print(f"[ERROR] Error de conexion: {rc}")


def on_message(client, userdata, msg):
    """Simula la respuesta del servo al recibir un comando del backend."""
    payload = msg.payload.decode()
    try:
        data = json.loads(payload)
    except ValueError:
        data = {"raw": payload}

    angulo = data.get("angulo", 90)
    accion = data.get("accion", "abrir" if angulo >= 90 else "cerrar")

    estado_barrera = accion == "abrir"
    estado_str = "ABIERTA" if estado_barrera else "CERRADA"
    print(f"\n[talanquera/control] Comando recibido: angulo={angulo}, accion={accion}")
    print(f"    → Barrera simulada: {estado_str}")

    # Confirmar al backend
    client.publish("servo/estado", json.dumps({
        "angulo": angulo,
        "estado": "ok",
        "accion": accion,
    }))
    # Actualizar estado de la barrera
    client.publish("parqueadero/entrada", json.dumps({"libre": estado_barrera}))

    if estado_barrera:
        # Simular que la barrera se cierra automáticamente después de 5 segundos
        time.sleep(5)
        client.publish("talanquera/control", json.dumps({"angulo": 0, "accion": "cerrar"}))


client = mqtt.Client(client_id="smartparku-simulador-rpi")
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set(cert_reqs=ssl.CERT_NONE)
client.tls_insecure_set(True)
client.on_connect = on_connect
client.on_message = on_message

print(f"[...] Conectando a {BROKER}:{PORT} ...")
client.connect(BROKER, PORT)
client.loop_forever()
