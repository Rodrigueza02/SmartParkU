# -*- coding: utf-8 -*-
"""
SmartParkU - Script principal Raspberry Pi 3B
Maneja: 8 sensores IR FC-51 + 8 LEDs + Servo SG90 + LCD I2C
Publica estado a HiveMQ Cloud en tiempo real

Correr con:
    sudo python3 smartparku_main.py
"""

import time
import json
import ssl
import threading
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

# ── Intentar importar LCD I2C (opcional) ─────────────────────────────────────
try:
    from RPLCD.i2c import CharLCD
    lcd = CharLCD('PCF8574', 0x27, port=1, cols=16, rows=2)
    LCD_DISPONIBLE = True
    print("[OK] LCD I2C inicializada")
except Exception as e:
    LCD_DISPONIBLE = False
    print(f"[WARN] LCD no disponible: {e} — continuando sin LCD")

# ── Configuración MQTT ────────────────────────────────────────────────────────
BROKER   = "7de2fa1d05f84c5c8f2fcacca06d98da.s1.eu.hivemq.cloud"
PORT     = 8883
USERNAME = "Juliana"
PASSWORD = "1138524566Juli*"

# ── Definición de slots (debe coincidir con el backend) ───────────────────────
SLOTS = [
    {"slot_id": "slot_01", "label": "C-01", "tipo": "carro",     "ir_pin": 17, "led_pin": 16},
    {"slot_id": "slot_02", "label": "C-02", "tipo": "carro",     "ir_pin": 27, "led_pin": 20},
    {"slot_id": "slot_03", "label": "C-03", "tipo": "carro",     "ir_pin": 22, "led_pin": 4},
    {"slot_id": "slot_04", "label": "C-04", "tipo": "carro",     "ir_pin": 5,  "led_pin": 14},
    {"slot_id": "slot_05", "label": "M-01", "tipo": "moto",      "ir_pin": 6,  "led_pin": 15},
    {"slot_id": "slot_06", "label": "M-02", "tipo": "moto",      "ir_pin": 13, "led_pin": 11},
    {"slot_id": "slot_07", "label": "M-03", "tipo": "moto",      "ir_pin": 19, "led_pin": 21},
    {"slot_id": "slot_08", "label": "B-01", "tipo": "bicicleta", "ir_pin": 26, "led_pin": 7},
]

# ── Configuración Servo ───────────────────────────────────────────────────────
SERVO_PIN     = 12
TOPIC_SERVO   = "talanquera/control"
TOPIC_SENSORES = "sensores/ultrasonico"
TOPIC_ESPACIOS = "parqueadero/espacios"

# ── Setup GPIO ────────────────────────────────────────────────────────────────
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# IR como entradas
for slot in SLOTS:
    GPIO.setup(slot["ir_pin"], GPIO.IN)

# LEDs como salidas
for slot in SLOTS:
    GPIO.setup(slot["led_pin"], GPIO.OUT)
    GPIO.output(slot["led_pin"], GPIO.LOW)

# Servo PWM
GPIO.setup(SERVO_PIN, GPIO.OUT)
servo_pwm = GPIO.PWM(SERVO_PIN, 50)
servo_pwm.start(0)

# Estado actual de cada slot
estado_slots = {s["slot_id"]: "libre" for s in SLOTS}

# ── LCD helper ────────────────────────────────────────────────────────────────
def lcd_mostrar(linea1: str, linea2: str = ""):
    if not LCD_DISPONIBLE:
        return
    try:
        lcd.clear()
        lcd.write_string(linea1[:16])
        lcd.cursor_pos = (1, 0)
        lcd.write_string(linea2[:16])
    except Exception:
        pass

# ── Servo helper ──────────────────────────────────────────────────────────────
def set_angulo(angulo: int):
    duty = 2 + (angulo / 18)
    servo_pwm.ChangeDutyCycle(duty)
    time.sleep(0.8)
    servo_pwm.ChangeDutyCycle(0)

# ── MQTT callbacks ────────────────────────────────────────────────────────────
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("[OK] Conectado a HiveMQ Cloud")
        client.subscribe(TOPIC_SERVO)
        print(f"[OK] Suscrito a: {TOPIC_SERVO}")
        lcd_mostrar("SmartParkU", "Conectado!")
        # Publicar estado inicial
        publicar_estado_masivo(client)
    else:
        print(f"[ERROR] Conexion rechazada: {reason_code}")
        lcd_mostrar("Error MQTT", f"Cod: {reason_code}")

def on_disconnect(client, userdata, flags, reason_code, properties):
    if reason_code != 0:
        print(f"[WARN] Desconectado ({reason_code}), reconectando...")
        lcd_mostrar("Desconectado", "Reconectando...")

def on_message(client, userdata, msg):
    """Recibe comandos del servo desde el backend."""
    try:
        data = json.loads(msg.payload.decode())
        print(f"\n[MQTT] Comando servo: {data}")
        accion = data.get("accion", "")
        if accion == "abrir":
            print("[->] Abriendo talanquera...")
            set_angulo(90)
            print("[OK] Talanquera ABIERTA")
            lcd_mostrar("Talanquera", "ABIERTA")
            client.publish("servo/estado", json.dumps({"estado": "abierta", "angulo": 90}))
        elif accion == "cerrar":
            print("[->] Cerrando talanquera...")
            set_angulo(0)
            print("[OK] Talanquera CERRADA")
            lcd_mostrar("Talanquera", "CERRADA")
            client.publish("servo/estado", json.dumps({"estado": "cerrada", "angulo": 0}))
    except Exception as e:
        print(f"[ERROR] on_message: {e}")

# ── Publicar estado masivo ────────────────────────────────────────────────────
def publicar_estado_masivo(client):
    espacios = []
    for slot in SLOTS:
        sid = slot["slot_id"]
        espacios.append({
            "slot":   sid,
            "label":  slot["label"],
            "status": estado_slots[sid],
            "tipo":   slot["tipo"],
        })
    payload = json.dumps({"espacios": espacios})
    client.publish(TOPIC_ESPACIOS, payload)
    libres   = sum(1 for v in estado_slots.values() if v == "libre")
    ocupados = sum(1 for v in estado_slots.values() if v == "ocupado")
    print(f"[INFO] Estado publicado → Libres: {libres}  Ocupados: {ocupados}")

# ── Loop principal de sensores ────────────────────────────────────────────────
def loop_sensores(client):
    """Lee los 8 IR cada 0.3s, actualiza LEDs y publica cambios."""
    print("[OK] Loop de sensores iniciado")
    while True:
        cambio = False
        for slot in SLOTS:
            sid     = slot["slot_id"]
            ir_pin  = slot["ir_pin"]
            led_pin = slot["led_pin"]

            # FC-51: LOW = obstáculo detectado (ocupado), HIGH = libre
            lectura = GPIO.input(ir_pin)
            nuevo_estado = "ocupado" if lectura == GPIO.LOW else "libre"

            if nuevo_estado != estado_slots[sid]:
                estado_slots[sid] = nuevo_estado
                cambio = True

                # Actualizar LED
                GPIO.output(led_pin, GPIO.HIGH if nuevo_estado == "ocupado" else GPIO.LOW)

                # Publicar cambio individual
                payload = json.dumps({
                    "slot":   sid,
                    "label":  slot["label"],
                    "tipo":   slot["tipo"],
                    "status": nuevo_estado,
                    "distancia": 5 if nuevo_estado == "ocupado" else 50,
                })
                client.publish(TOPIC_SENSORES, payload)
                print(f"[sensor] {sid} ({slot['label']}) → {nuevo_estado.upper()}")

                # Actualizar LCD con resumen
                libres   = sum(1 for v in estado_slots.values() if v == "libre")
                ocupados = sum(1 for v in estado_slots.values() if v == "ocupado")
                lcd_mostrar(f"Libres:   {libres}/8", f"Ocupados: {ocupados}/8")

        # Si hubo cambio, publicar estado masivo también
        if cambio:
            publicar_estado_masivo(client)

        time.sleep(0.3)

# ── Inicializar MQTT ──────────────────────────────────────────────────────────
client = mqtt.Client(
    callback_api_version=CallbackAPIVersion.VERSION2,
    client_id="smartparku-raspi-main",
    protocol=mqtt.MQTTv311,
)
client.username_pw_set(USERNAME, PASSWORD)
client.tls_set(cert_reqs=ssl.CERT_NONE)
client.tls_insecure_set(True)
client.on_connect    = on_connect
client.on_disconnect = on_disconnect
client.on_message    = on_message

# ── Arranque ──────────────────────────────────────────────────────────────────
try:
    lcd_mostrar("SmartParkU", "Iniciando...")
    print(f"[...] Conectando a {BROKER}:{PORT} ...")
    client.connect(BROKER, PORT, keepalive=60)

    # Sensores en hilo separado
    hilo = threading.Thread(target=loop_sensores, args=(client,), daemon=True)
    hilo.start()

    client.loop_forever()

except KeyboardInterrupt:
    print("\n[--] Detenido por usuario")

finally:
    lcd_mostrar("SmartParkU", "Apagando...")
    # Apagar todos los LEDs
    for slot in SLOTS:
        GPIO.output(slot["led_pin"], GPIO.LOW)
    servo_pwm.ChangeDutyCycle(0)
    servo_pwm.stop()
    GPIO.cleanup()
    if LCD_DISPONIBLE:
        lcd.clear()
    print("[OK] GPIO liberado correctamente")
