# -*- coding: utf-8 -*-
"""
SmartParkU - Test rapido de publicacion MQTT (paho-mqtt 2.x)
Ejecutar: python test_pub.py
"""
import ssl
import json
import time
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
from dotenv import load_dotenv
import os

load_dotenv()

BROKER   = os.getenv("MQTT_BROKER",   "7de2fa1d05f84c5c8f2fcacca06d98da.s1.eu.hivemq.cloud")
PORT     = int(os.getenv("MQTT_PORT", "8883"))
USERNAME = os.getenv("MQTT_USERNAME", "Juliana")
PASSWORD = os.getenv("MQTT_PASSWORD", "1138524566Juli*")


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print(f"[OK] Conectado a {BROKER}")
        print("[...] Enviando mensajes de prueba...\n")

        # slot_01 ocupado (8 cm = vehiculo presente) — C-01 carro
        client.publish("sensores/ultrasonico", json.dumps(
            {"slot": "slot_01", "distancia": 8, "tipo": "carro", "label": "C-01"}
        ))
        print("[->] slot_01 (C-01)  distancia=8cm   tipo=carro  -> OCUPADO")
        time.sleep(0.4)

        # slot_02 libre (60 cm) — C-02 carro
        client.publish("sensores/ultrasonico", json.dumps(
            {"slot": "slot_02", "distancia": 60, "tipo": "carro", "label": "C-02"}
        ))
        print("[->] slot_02 (C-02)  distancia=60cm  tipo=carro  -> LIBRE")
        time.sleep(0.4)

        # slot_05 moto ocupado — M-01
        client.publish("sensores/ultrasonico", json.dumps(
            {"slot": "slot_05", "distancia": 5, "tipo": "moto", "label": "M-01"}
        ))
        print("[->] slot_05 (M-01)  distancia=5cm   tipo=moto   -> OCUPADO")
        time.sleep(0.4)

        # slot_08 bicicleta libre — B-01
        client.publish("sensores/ultrasonico", json.dumps(
            {"slot": "slot_08", "distancia": 45, "tipo": "bicicleta", "label": "B-01"}
        ))
        print("[->] slot_08 (B-01)  distancia=45cm  tipo=bici   -> LIBRE")
        time.sleep(0.4)

        # slot_10 VIP libre — V-01
        client.publish("sensores/ultrasonico", json.dumps(
            {"slot": "slot_10", "distancia": 70, "tipo": "vip", "label": "V-01"}
        ))
        print("[->] slot_10 (V-01)  distancia=70cm  tipo=vip    -> LIBRE")
        time.sleep(0.4)

        # Estado barrera abierta
        client.publish("parqueadero/entrada", json.dumps({"libre": True}))
        print("[->] parqueadero/entrada  libre=true  -> BARRERA ABIERTA")

        print("\n[OK] Mensajes enviados. Mira el dashboard_mqtt.py en la otra terminal.")
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
    print(f"[--] Desconectado")


client = mqtt.Client(
    callback_api_version=CallbackAPIVersion.VERSION2,
    client_id="smartparku-test-pub",
    protocol=mqtt.MQTTv311,
)
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
    print("\nVerifica con: ping 7de2fa1d05f84c5c8f2fcacca06d98da.s1.eu.hivemq.cloud")
