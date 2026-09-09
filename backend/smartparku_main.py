# -*- coding: utf-8 -*-
"""
SmartParkU - Script principal Raspberry Pi 3B
Maneja: Servo SG90 (talanquera) + LCD I2C
Publica estado de barrera a HiveMQ Cloud en tiempo real.

NOTA: Los sensores IR FC-51 de celda han sido retirados del flujo de ocupación.
El estado de cada puesto se gestiona exclusivamente mediante escaneo QR desde la app.
Los LEDs de celda pueden mantenerse por indicación visual local si se desea,
pero ya no publican estado al broker ni a la BD.

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

# ── Configuración Servo / Talanquera ─────────────────────────────────────────
SERVO_PIN          = 12
TOPIC_TALANQUERA   = "talanquera/control"
TOPIC_ENTRADA      = "parqueadero/entrada"

# ── Setup GPIO ────────────────────────────────────────────────────────────────
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
servo_pwm = GPIO.PWM(SERVO_PIN, 50)
servo_pwm.start(0)

lcd_bloqueada = False


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
        client.subscribe(TOPIC_TALANQUERA)
        print(f"[OK] Suscrito a: {TOPIC_TALANQUERA}")
        lcd_mostrar("SmartParkU", "Conectado!")
        # Publicar estado inicial: barrera cerrada
        client.publish(TOPIC_ENTRADA, json.dumps({"libre": False}))
    else:
        print(f"[ERROR] Conexion rechazada: {reason_code}")
        lcd_mostrar("Error MQTT", f"Cod: {reason_code}")


def on_disconnect(client, userdata, flags, reason_code, properties):
    if reason_code != 0:
        print(f"[WARN] Desconectado ({reason_code}), reconectando...")
        lcd_mostrar("Desconectado", "Reconectando...")


def on_message(client, userdata, msg):
    """Recibe comandos de la talanquera desde el backend."""
    global lcd_bloqueada
    try:
        data = json.loads(msg.payload.decode())
        print(f"\n[MQTT] Comando talanquera: {data}")
        accion = data.get("accion", "")
        angulo = data.get("angulo", 90)

        if accion == "abrir":
            print("[->] Abriendo talanquera...")
            set_angulo(90)
            print("[OK] Talanquera ABIERTA")
            lcd_bloqueada = True
            lcd_mostrar("Talanquera", "ABIERTA")
            client.publish("servo/estado", json.dumps({"estado": "abierta", "angulo": 90}))
            client.publish(TOPIC_ENTRADA, json.dumps({"libre": True}))
            time.sleep(3)
            lcd_bloqueada = False
            # Cerrar automáticamente después de 5 segundos
            time.sleep(5)
            set_angulo(0)
            client.publish("servo/estado", json.dumps({"estado": "cerrada", "angulo": 0}))
            client.publish(TOPIC_ENTRADA, json.dumps({"libre": False}))
            lcd_mostrar("Talanquera", "CERRADA")

        elif accion == "cerrar":
            print("[->] Cerrando talanquera...")
            set_angulo(0)
            print("[OK] Talanquera CERRADA")
            lcd_bloqueada = True
            lcd_mostrar("Talanquera", "CERRADA")
            client.publish("servo/estado", json.dumps({"estado": "cerrada", "angulo": 0}))
            client.publish(TOPIC_ENTRADA, json.dumps({"libre": False}))
            time.sleep(3)
            lcd_bloqueada = False

    except Exception as e:
        print(f"[ERROR] on_message: {e}")


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
    client.loop_forever()

except KeyboardInterrupt:
    print("\n[--] Detenido por usuario")

finally:
    lcd_mostrar("SmartParkU", "Apagando...")
    set_angulo(0)  # Asegurar barrera cerrada al apagar
    servo_pwm.ChangeDutyCycle(0)
    servo_pwm.stop()
    GPIO.cleanup()
    if LCD_DISPONIBLE:
        lcd.clear()
    print("[OK] GPIO liberado correctamente")
