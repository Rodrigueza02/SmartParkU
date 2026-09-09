import ssl
import json
import asyncio
import logging
from datetime import datetime
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
from app.core.config import settings

logger = logging.getLogger("smartparku.mqtt")

SLOTS_DEFINICION = [
    {"slot_id": "slot_01", "label": "C-01", "tipo": "carro"},
    {"slot_id": "slot_02", "label": "C-02", "tipo": "carro"},
    {"slot_id": "slot_03", "label": "C-03", "tipo": "carro"},
    {"slot_id": "slot_04", "label": "C-04", "tipo": "carro"},
    {"slot_id": "slot_05", "label": "M-01", "tipo": "moto"},
    {"slot_id": "slot_06", "label": "M-02", "tipo": "moto"},
    {"slot_id": "slot_07", "label": "M-03", "tipo": "moto"},
    {"slot_id": "slot_08", "label": "B-01", "tipo": "bicicleta"},
    {"slot_id": "slot_09", "label": "B-02", "tipo": "bicicleta"},
    {"slot_id": "slot_10", "label": "V-01", "tipo": "vip"},
]

# Estado en memoria del parqueadero — la fuente de verdad es la BD.
# Este dict sólo alimenta el WebSocket del mapa en tiempo real.
# El estado de ocupación se actualiza ÚNICAMENTE por el flujo QR
# (ingreso_service.ocupar_puesto / acceso_service.registrar_salida → update_slot_status).
parking_state = {
    "espacios": {
        s["slot_id"]: {
            "status": "libre",
            "tipo": s["tipo"],
            "label": s["label"],
            "updated_at": None,
        }
        for s in SLOTS_DEFINICION
    },
    "entrada_libre": True,
    "total_libre": len(SLOTS_DEFINICION),
    "total_ocupado": 0,
    "timestamp": None,
}

ws_listeners: set = set()
_mqtt_client: mqtt.Client = None


def _broadcast_state():
    if not ws_listeners:
        return
    payload = json.dumps(parking_state, default=str)
    for q in ws_listeners.copy():
        try:
            q.put_nowait(payload)
        except asyncio.QueueFull:
            pass


def _recalculate_totals():
    libre = sum(1 for s in parking_state["espacios"].values() if s["status"] == "libre")
    ocupado = sum(1 for s in parking_state["espacios"].values() if s["status"] == "ocupado")
    parking_state["total_libre"] = libre
    parking_state["total_ocupado"] = ocupado


def _on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        logger.info("MQTT conectado al broker HiveMQ")
        # Solo escuchar tópicos de control de talanquera y estado de barrera.
        # Los sensores de celda ya NO determinan ocupación — eso lo hace el flujo QR.
        client.subscribe("servo/#")
        client.subscribe("talanquera/#")
        client.subscribe("parqueadero/entrada")
    else:
        logger.error(f"MQTT conexion rechazada, codigo: {reason_code}")


def _on_message(client, userdata, msg):
    topic = msg.topic
    raw = msg.payload.decode()
    now_str = datetime.utcnow().isoformat()

    try:
        data = json.loads(raw)
    except ValueError:
        data = {"raw": raw}

    parking_state["timestamp"] = now_str
    logger.debug(f"MQTT [{topic}] {data}")

    if topic == "parqueadero/entrada":
        # Actualiza el indicador de barrera principal (abierta/cerrada)
        parking_state["entrada_libre"] = data.get("libre", True)
        _broadcast_state()

    elif topic == "servo/estado":
        logger.info(f"Servo status: {data}")


def _on_disconnect(client, userdata, flags, reason_code, properties):
    if reason_code != 0:
        logger.warning(
            f"MQTT desconectado inesperadamente (codigo {reason_code}), "
            "paho reconectara automaticamente..."
        )


def publish_servo(angulo: int, accion: str = None):
    if _mqtt_client is None:
        raise RuntimeError("MQTT client no inicializado")
    accion_str = accion or ("abrir" if angulo >= 90 else "cerrar")
    payload = json.dumps({"angulo": angulo, "accion": accion_str})
    _mqtt_client.publish("talanquera/control", payload)
    logger.info(f"Servo comando publicado en talanquera/control: {payload}")


def add_ws_listener(queue: asyncio.Queue):
    ws_listeners.add(queue)


def remove_ws_listener(queue: asyncio.Queue):
    ws_listeners.discard(queue)


def update_slot_status(slot_id: str, status: str):
    """
    Actualiza el estado de un espacio en parking_state y lo transmite
    por WebSocket a todos los clientes conectados al mapa.

    Esta es la ÚNICA vía por la que un slot cambia de estado en memoria:
    se invoca desde ingreso_service (ocupar_puesto) y acceso_service (registrar_salida).
    """
    now_str = datetime.utcnow().isoformat()
    existing = parking_state["espacios"].get(slot_id)
    if existing:
        parking_state["espacios"][slot_id]["status"] = status
        parking_state["espacios"][slot_id]["updated_at"] = now_str
    else:
        parking_state["espacios"][slot_id] = {
            "status": status,
            "tipo": "carro",
            "label": slot_id,
            "updated_at": now_str,
        }
    parking_state["timestamp"] = now_str
    _recalculate_totals()
    _broadcast_state()
    logger.info(f"Slot {slot_id} actualizado a '{status}' via QR → broadcast WebSocket")


def stop_mqtt():
    global _mqtt_client
    if _mqtt_client:
        _mqtt_client.loop_stop()
        _mqtt_client.disconnect()
        logger.info("MQTT desconectado limpiamente")


async def start_mqtt():
    global _mqtt_client

    use_tls = settings.MQTT_PORT != 1883
    if use_tls and (not settings.MQTT_USERNAME or not settings.MQTT_PASSWORD):
        logger.error("MQTT_USERNAME o MQTT_PASSWORD no configurados en .env")
        return

    _mqtt_client = mqtt.Client(
        callback_api_version=CallbackAPIVersion.VERSION2,
        client_id="smartparku-backend",
        protocol=mqtt.MQTTv311,
    )

    # Puerto 1883 = Mosquitto local sin TLS (docker-compose dev)
    # Puerto 8883 = HiveMQ Cloud con TLS (produccion)
    use_tls = settings.MQTT_PORT != 1883
    if use_tls:
        if settings.MQTT_USERNAME:
            _mqtt_client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
        _mqtt_client.tls_set(cert_reqs=ssl.CERT_NONE)
        _mqtt_client.tls_insecure_set(True)
        logger.info("MQTT configurado con TLS (modo cloud)")
    else:
        logger.info("MQTT configurado sin TLS (modo local Mosquitto)")

    _mqtt_client.on_connect = _on_connect
    _mqtt_client.on_message = _on_message
    _mqtt_client.on_disconnect = _on_disconnect

    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(
            None,
            lambda: _mqtt_client.connect(settings.MQTT_BROKER, settings.MQTT_PORT, keepalive=60),
        )
    except Exception as e:
        logger.error(f"No se pudo conectar al broker MQTT: {e}")
        return

    _mqtt_client.loop_start()
    logger.info(f"MQTT conectado a {settings.MQTT_BROKER}:{settings.MQTT_PORT} - loop iniciado")
