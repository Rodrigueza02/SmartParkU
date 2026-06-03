# -*- coding: utf-8 -*-
"""
SmartParkU - Cliente MQTT integrado al backend FastAPI
Corre como tarea de fondo (asyncio) junto al servidor.
- Recibe datos del HC-SR04 y actualiza el estado del parqueadero en memoria.
- Expone el estado via WebSocket al frontend.
- Publica comandos al servo desde los endpoints REST.
"""
import ssl
import json
import asyncio
import logging
from datetime import datetime
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
from dotenv import load_dotenv
import os

load_dotenv()

logger = logging.getLogger("smartparku.mqtt")

BROKER   = os.getenv("MQTT_BROKER",   "7de2fa1d05f84c5c8f2fcacca06d98da.s1.eu.hivemq.cloud")
PORT     = int(os.getenv("MQTT_PORT", "8883"))
USERNAME = os.getenv("MQTT_USERNAME", "Juliana")
PASSWORD = os.getenv("MQTT_PASSWORD", "")

# ── Estado compartido en memoria ───────────────────────────────────────────────
# Actualizado por MQTT, leido por WebSocket y endpoints REST
parking_state = {
    "espacios": {
        # "slot_id": {"status": "libre"|"ocupado", "tipo": "carro"|"moto"|"bicicleta",
        #             "distancia_cm": float, "updated_at": str}
    },
    "entrada_libre": True,
    "total_libre": 0,
    "total_ocupado": 0,
    "ultimo_sensor_cm": None,
    "timestamp": None,
}

# Clientes WebSocket conectados (set de asyncio.Queue)
ws_listeners: set = set()

# Cliente MQTT global (para publicar desde endpoints)
_mqtt_client: mqtt.Client = None


# ── Helpers ────────────────────────────────────────────────────────────────────

def _broadcast_state():
    """Envia el estado actual a todos los listeners WebSocket."""
    if not ws_listeners:
        return
    payload = json.dumps(parking_state, default=str)
    for q in ws_listeners.copy():
        try:
            q.put_nowait(payload)
        except asyncio.QueueFull:
            pass


def _recalculate_totals():
    libre   = sum(1 for s in parking_state["espacios"].values() if s["status"] == "libre")
    ocupado = sum(1 for s in parking_state["espacios"].values() if s["status"] == "ocupado")
    parking_state["total_libre"]   = libre
    parking_state["total_ocupado"] = ocupado


# ── Handlers MQTT ──────────────────────────────────────────────────────────────

def _on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        logger.info("MQTT conectado al broker HiveMQ")
        # Topicos propios del sistema
        client.subscribe("sensores/#")
        client.subscribe("servo/#")
        client.subscribe("parqueadero/#")
        # Topico del servo real en la Raspberry
        client.subscribe("talanquera/#")
        # Wildcard para ver cualquier topico desconocido
        client.subscribe("#")
    else:
        logger.error(f"MQTT conexion rechazada, codigo: {reason_code}")


def _on_message(client, userdata, msg):
    topic   = msg.topic
    raw     = msg.payload.decode()
    now_str = datetime.utcnow().isoformat()

    try:
        data = json.loads(raw)
    except ValueError:
        data = {"raw": raw}

    parking_state["timestamp"] = now_str
    logger.debug(f"MQTT [{topic}] {data}")

    # sensores/ultrasonico — acepta formato Raspberry {"distancia_cm": X}
    # y formato propio {"distancia": X, "slot": "1", "tipo": "carro"}
    if topic == "sensores/ultrasonico" or topic.startswith("sensores/"):
        # Acepta "distancia" o "distancia_cm" (formato Raspberry)
        distancia = data.get("distancia") or data.get("distancia_cm")
        slot_id   = str(data.get("slot", "1"))   # default slot 1 si la Raspberry no lo manda
        tipo      = data.get("tipo", "carro")

        if distancia is not None:
            parking_state["ultimo_sensor_cm"] = distancia
            # Umbral: < 15 cm = vehiculo presente (ocupado)
            # Distancias > 400 cm = error del sensor HC-SR04, ignorar
            if float(distancia) > 400:
                return
            status = "ocupado" if float(distancia) < 15 else "libre"
            parking_state["espacios"][slot_id] = {
                "status":       status,
                "tipo":         tipo,
                "distancia_cm": distancia,
                "updated_at":   now_str,
            }
            _recalculate_totals()
            _broadcast_state()

    # sensores/estado
    elif topic == "sensores/estado":
        slot_id = str(data.get("slot", "?"))
        status  = data.get("status", "desconocido")
        tipo    = data.get("tipo", "carro")
        if slot_id in parking_state["espacios"]:
            parking_state["espacios"][slot_id]["status"]     = status
            parking_state["espacios"][slot_id]["updated_at"] = now_str
        else:
            parking_state["espacios"][slot_id] = {
                "status": status, "tipo": tipo,
                "distancia_cm": None, "updated_at": now_str,
            }
        _recalculate_totals()
        _broadcast_state()

    # parqueadero/entrada
    elif topic == "parqueadero/entrada":
        parking_state["entrada_libre"] = data.get("libre", True)
        _broadcast_state()

    # parqueadero/espacios (mensaje masivo)
    elif topic == "parqueadero/espacios":
        espacios = data.get("espacios", [])
        for e in espacios:
            slot_id = str(e.get("slot"))
            parking_state["espacios"][slot_id] = {
                "status":       e.get("status", "libre"),
                "tipo":         e.get("tipo", "carro"),
                "distancia_cm": e.get("distancia_cm"),
                "updated_at":   now_str,
            }
        _recalculate_totals()
        _broadcast_state()

    # servo/estado
    elif topic == "servo/estado":
        logger.info(f"Servo status: {data}")


def _on_disconnect(client, userdata, flags, reason_code, properties):
    if reason_code != 0:
        logger.warning(f"MQTT desconectado inesperadamente (codigo {reason_code}), paho reconectara automaticamente...")


# ── API publica ────────────────────────────────────────────────────────────────

def publish_servo(angulo: int, accion: str = None):
    """Publica un comando al servo desde un endpoint REST."""
    if _mqtt_client is None:
        raise RuntimeError("MQTT client no inicializado")
    # La Raspberry escucha "talanquera/control" con {"accion": "abrir"|"cerrar"}
    accion_str = accion or ("abrir" if angulo >= 90 else "cerrar")
    payload = json.dumps({
        "angulo": angulo,
        "accion": accion_str,
    })
    _mqtt_client.publish("talanquera/control", payload)
    logger.info(f"Servo comando publicado en talanquera/control: {payload}")


def add_ws_listener(queue: asyncio.Queue):
    ws_listeners.add(queue)


def remove_ws_listener(queue: asyncio.Queue):
    ws_listeners.discard(queue)


def stop_mqtt():
    """Detiene el cliente MQTT limpiamente al apagar el servidor."""
    global _mqtt_client
    if _mqtt_client:
        _mqtt_client.loop_stop()
        _mqtt_client.disconnect()
        logger.info("MQTT desconectado limpiamente")


# ── Arranque como tarea asyncio ───────────────────────────────────────────────

async def start_mqtt():
    """
    Inicializa el cliente MQTT y lo conecta al broker HiveMQ Cloud.
    Usa loop_start() para que paho maneje su propio hilo de networking
    sin bloquear el event loop de FastAPI/asyncio.
    """
    global _mqtt_client

    if not USERNAME or not PASSWORD:
        logger.error("MQTT_USERNAME o MQTT_PASSWORD no configurados en .env")
        return

    _mqtt_client = mqtt.Client(
        callback_api_version=CallbackAPIVersion.VERSION2,
        client_id="smartparku-backend",
        protocol=mqtt.MQTTv311,
    )
    _mqtt_client.username_pw_set(USERNAME, PASSWORD)
    _mqtt_client.tls_set(cert_reqs=ssl.CERT_NONE)
    _mqtt_client.tls_insecure_set(True)
    _mqtt_client.on_connect    = _on_connect
    _mqtt_client.on_message    = _on_message
    _mqtt_client.on_disconnect = _on_disconnect

    # connect() en executor para no bloquear el startup de FastAPI
    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(None, lambda: _mqtt_client.connect(BROKER, PORT, keepalive=60))
    except Exception as e:
        logger.error(f"No se pudo conectar al broker MQTT: {e}")
        return

    # loop_start() lanza un hilo interno de paho que maneja
    # reconexiones, pings y recepcion de mensajes automaticamente
    _mqtt_client.loop_start()
    logger.info(f"MQTT conectado a {BROKER}:{PORT} — loop iniciado")
