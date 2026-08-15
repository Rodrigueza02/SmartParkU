# -*- coding: utf-8 -*-
"""
SmartParkU - servo_adapter_v2.py
Script corregido para Raspberry Pi 3B con paho-mqtt >= 2.0
Escucha el topico talanquera/control y mueve el servo SG90

Correr en la Raspi con:
    sudo python3 servo_adapter_v2.py
"""
import time
import json
import ssl
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
import RPi.GPIO as GPIO

# ── Configuración MQTT ────────────────────────────────────────────────────────
BROKER   = "7de2fa1d05f84c5c8f2fcacca06d98da.s1.eu.hivemq.cloud"
PORT     = 8883
USERNAME = "Juliana"
PASSWORD = "1138524566Juli*"
TOPIC_SERVO = "talanquera/control"

# ── Configuración GPIO ────────────────────────────────────────────────────────
SERVO_PIN = 12  # GPIO 12 / Pin físico 32
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)

servo_pwm = GPIO.PWM(SERVO_PIN, 50)  # 50Hz para SG90
servo_pwm.start(0)


def set_angulo(angulo: int):
    """Mueve el servo al ángulo indicado (0 = cerrado, 90 = abierto)."""
    duty = 2 + (angulo / 18)
    servo_pwm.ChangeDutyCycle(duty)
    time.sleep(0.8)
    servo_pwm.ChangeDutyCycle(0)  # apagar señal para evitar temblor
    print(f"[servo] Movido a {angulo} grados")


# ── Callbacks MQTT ────────────────────────────────────────────────────────────
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("[OK] Conectado a HiveMQ. Esperando comandos en talanquera/control ...")
        client.subscribe(TOPIC_SERVO)
        print(f"[OK] Suscrito a: {TOPIC_SERVO}")
    else:
        print(f"[ERROR] Conexion rechazada, codigo: {reason_code}")


def on_disconnect(client, userdata, flags, reason_code, properties):
    if reason_code != 0:
        print(f"[WARN] Desconectado inesperadamente (codigo {reason_code}), reconectando...")


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        print(f"\n[MQTT] Comando recibido en {msg.topic}: {data}")
        accion = data.get("accion", "")
        if accion == "abrir":
            print("[->] Abriendo talanquera...")
            set_angulo(90)
            print("[OK] Talanquera ABIERTA")
            client.publish("servo/estado", json.dumps({"estado": "abierta", "angulo": 90}))
        elif accion == "cerrar":
            print("[->] Cerrando talanquera...")
            set_angulo(0)
            print("[OK] Talanquera CERRADA")
            client.publish("servo/estado", json.dumps({"estado": "cerrada", "angulo": 0}))
        else:
            print(f"[WARN] Accion desconocida: {accion}")
    except Exception as e:
        print(f"[ERROR] {e}")


# ── Conexión MQTT ─────────────────────────────────────────────────────────────
client = mqtt.Client(
    callback_api_version=CallbackAPIVersion.VERSION2,
    client_id="smartparku-servo-raspi",
    protocol=mqtt.MQTTv311,
)
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set(cert_reqs=ssl.CERT_NONE)
client.tls_insecure_set(True)
client.on_connect    = on_connect
client.on_disconnect = on_disconnect
client.on_message    = on_message

try:
    print(f"[...] Conectando a {BROKER}:{PORT} ...")
    client.connect(BROKER, PORT, keepalive=60)
    client.loop_forever()
except KeyboardInterrupt:
    print("\n[--] Detenido por usuario")
finally:
    servo_pwm.ChangeDutyCycle(0)
    servo_pwm.stop()
    GPIO.cleanup()
    print("[OK] GPIO liberado correctamente")
