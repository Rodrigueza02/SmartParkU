
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

parking_state = {
    "espacios": {
        s["slot_id"]: {
            "status": "libre",
            "tipo": s["tipo"],
            "label": s["label"],
            "distancia_cm": None,
            "updated_at": None,
        }
        for s in SLOTS_DEFINICION
    },
    "entrada_libre": True,
    "total_libre": len(SLOTS_DEFINICION),
    "total_ocupado": 0,
    "ultimo_sensor_cm": None,
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
        client.subscribe("sensores/#")
        client.subscribe("servo/#")
        client.subscribe("parqueadero/#")
        client.subscribe("talanquera/#")
        client.subscribe("#")
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

    if topic == "sensores/ultrasonico" or topic.startswith("sensores/"):
        distancia = data.get("distancia") or data.get("distancia_cm")
        slot_id = str(data.get("slot", "slot_01"))
        tipo = data.get("tipo", "carro")

        if distancia is not None:
            parking_state["ultimo_sensor_cm"] = distancia
            if float(distancia) > 400:
                return
            status = "ocupado" if float(distancia) < 15 else "libre"

            existing = parking_state["espacios"].get(slot_id)
            parking_state["espacios"][slot_id] = {
                "status": status,
                "tipo": existing["tipo"] if existing else tipo,
                "label": existing["label"] if existing else slot_id,
                "distancia_cm": distancia,
                "updated_at": now_str,
            }
            _recalculate_totals()
            _broadcast_state()

    elif topic == "sensores/estado":
        slot_id = str(data.get("slot", "?"))
        status = data.get("status", "desconocido")
        tipo = data.get("tipo", "carro")
        existing = parking_state["espacios"].get(slot_id)
        if existing:
            parking_state["espacios"][slot_id]["status"] = status
            parking_state["espacios"][slot_id]["updated_at"] = now_str
        else:
            parking_state["espacios"][slot_id] = {
                "status": status, "tipo": tipo, "label": slot_id,
                "distancia_cm": None, "updated_at": now_str,
            }
        _recalculate_totals()
        _broadcast_state()

    elif topic == "parqueadero/entrada":
        parking_state["entrada_libre"] = data.get("libre", True)
        _broadcast_state()

    elif topic == "parqueadero/espacios":
        espacios = data.get("espacios", [])
        for e in espacios:
            slot_id = str(e.get("slot"))
            existing = parking_state["espacios"].get(slot_id)
            parking_state["espacios"][slot_id] = {
                "status": e.get("status", "libre"),
                "tipo": e.get("tipo") or (existing["tipo"] if existing else "carro"),
                "label": e.get("label") or (existing["label"] if existing else slot_id),
                "distancia_cm": e.get("distancia_cm") or (existing["distancia_cm"] if existing else None),
                "updated_at": now_str,
            }
        _recalculate_totals()
        _broadcast_state()

    elif topic == "servo/estado":
        logger.info(f"Servo status: {data}")


def _on_disconnect(client, userdata, flags, reason_code, properties):
    if reason_code != 0:
        logger.warning(f"MQTT desconectado inesperadamente (codigo {reason_code}), paho reconectara automaticamente...")


def publish_servo(angulo: int, accion: str = None):
    if _mqtt_client is None:
        raise RuntimeError("MQTT client no inicializado")
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


def update_slot_status(slot_id: str, status: str):
    """
    Actualiza el estado de un espacio en parking_state y lo transmite
    por WebSocket a todos los clientes conectados al mapa.
    Llamar desde qr_service después de escanear un QR.
    """
    now_str = datetime.utcnow().isoformat()
    existing = parking_state["espacios"].get(slot_id)
    if existing:
        parking_state["espacios"][slot_id]["status"] = status
        parking_state["espacios"][slot_id]["updated_at"] = now_str
    else:
        # slot no estaba en memoria (raro), lo inicializamos
        parking_state["espacios"][slot_id] = {
            "status": status,
            "tipo": "carro",
            "label": slot_id,
            "distancia_cm": None,
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

    if not settings.MQTT_USERNAME or not settings.MQTT_PASSWORD:
        logger.error("MQTT_USERNAME o MQTT_PASSWORD no configurados en .env")
        return

    _mqtt_client = mqtt.Client(
        callback_api_version=CallbackAPIVersion.VERSION2,
        client_id="smartparku-backend",
        protocol=mqtt.MQTTv311,
    )
    _mqtt_client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
    _mqtt_client.tls_set(cert_reqs=ssl.CERT_NONE)
    _mqtt_client.tls_insecure_set(True)
    _mqtt_client.on_connect = _on_connect
    _mqtt_client.on_message = _on_message
    _mqtt_client.on_disconnect = _on_disconnect

    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(None, lambda: _mqtt_client.connect(settings.MQTT_BROKER, settings.MQTT_PORT, keepalive=60))
    except Exception as e:
        logger.error(f"No se pudo conectar al broker MQTT: {e}")
        return

    _mqtt_client.loop_start()
    logger.info(f"MQTT conectado a {settings.MQTT_BROKER}:{settings.MQTT_PORT} - loop iniciado")

