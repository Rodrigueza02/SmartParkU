# -*- coding: utf-8 -*-
"""
SmartParkU - Simulador de Raspberry Pi (HC-SR04 + Servo)
Simula los sensores y la barrera para probar el sistema completo sin hardware.

Ejecutar con: python simulador_raspberry.py

Topicos que publica:
  sensores/ultrasonico  -> distancia de cada cajon
  parqueadero/espacios  -> estado masivo de todos los espacios
  parqueadero/entrada   -> estado de la barrera

Topicos que escucha:
  servo/control         -> imprime comandos recibidos del backend/PC
"""
import ssl
import json
import time
import random
import threading
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
import os

load_dotenv()

BROKER   = os.getenv("MQTT_BROKER",   "7de2fa1d05f84c5c8f2fcacca06d98da.s1.eu.hivemq.cloud")
PORT     = int(os.getenv("MQTT_PORT", "8883"))
USERNAME = os.getenv("MQTT_USERNAME", "Juliana")
PASSWORD = os.getenv("MQTT_PASSWORD", "1138524566Juli*")

# Cajones del parqueadero UCC Pasto
SLOTS = (
    [{"slot": str(i), "tipo": "carro"}     for i in range(1, 23)] +
    [{"slot": str(i), "tipo": "moto"}      for i in range(23, 33)] +
    [{"slot": str(i), "tipo": "bicicleta"} for i in range(33, 41)]
)

# Estado interno del simulador
estado_slots = {
    s["slot"]: {
        "status":       random.choice(["libre", "libre", "ocupado"]),
        "tipo":         s["tipo"],
        "distancia_cm": random.uniform(20, 80),
    }
    for s in SLOTS
}


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[OK] Simulador conectado al broker HiveMQ")
        client.subscribe("servo/control")
        print("[OK] Escuchando servo/control ...\n")
        publicar_estado_masivo(client)
    else:
        print(f"[ERROR] Error de conexion: {rc}")


def on_message(client, userdata, msg):
    """Recibe comandos del servo desde el PC o backend."""
    payload = msg.payload.decode()
    try:
        data = json.loads(payload)
    except ValueError:
        data = {"raw": payload}
    print(f"\n[servo/control] Comando recibido: {data}")
    angulo = data.get("angulo", 90)
    accion = "ABIERTA" if angulo >= 90 else "CERRADA"
    print(f"    -> Barrera {accion} (angulo={angulo} grados)")
    client.publish("servo/estado", json.dumps({
        "angulo": angulo,
        "estado": "ok",
        "accion": accion.lower(),
    }))


def publicar_estado_masivo(client):
    espacios = []
    for slot_id, info in estado_slots.items():
        espacios.append({
            "slot":         slot_id,
            "status":       info["status"],
            "tipo":         info["tipo"],
            "distancia_cm": round(info["distancia_cm"], 1),
        })
    client.publish("parqueadero/espacios", json.dumps({"espacios": espacios}))
    libres   = sum(1 for s in estado_slots.values() if s["status"] == "libre")
    ocupados = len(estado_slots) - libres
    print(f"[INFO] Estado publicado -> Libres: {libres}  Ocupados: {ocupados}")


def loop_sensores(client):
    """Simula los sensores cambiando aleatoriamente el estado de los cajones."""
    while True:
        time.sleep(5)

        # Cambiar 1-3 cajones aleatoriamente
        slots_cambiados = random.sample(list(estado_slots.keys()), k=random.randint(1, 3))
        for slot_id in slots_cambiados:
            info = estado_slots[slot_id]
            if info["status"] == "libre":
                info["status"]       = "ocupado"
                info["distancia_cm"] = round(random.uniform(3, 12), 1)
            else:
                info["status"]       = "libre"
                info["distancia_cm"] = round(random.uniform(25, 90), 1)

            payload = {
                "slot":      slot_id,
                "distancia": info["distancia_cm"],
                "tipo":      info["tipo"],
            }
            client.publish("sensores/ultrasonico", json.dumps(payload))
            print(f"[sensor] cajon {slot_id:>3} {info['tipo']:10s} -> {info['distancia_cm']:5.1f} cm  ({info['status']})")

        publicar_estado_masivo(client)


client = mqtt.Client(client_id="smartparku-simulador-rpi")
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set(cert_reqs=ssl.CERT_NONE)
client.tls_insecure_set(True)
client.on_connect = on_connect
client.on_message = on_message

print(f"[...] Conectando a {BROKER}:{PORT} ...")
client.connect(BROKER, PORT)

# Iniciar loop de sensores en hilo aparte
threading.Thread(target=loop_sensores, args=(client,), daemon=True).start()

client.loop_forever()
