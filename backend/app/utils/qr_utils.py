"""
qr_utils.py
-----------
Utilidades para generar y verificar códigos QR firmados con HMAC-SHA256.
El payload se serializa en JSON, se firma, y se codifica en base64 URL-safe
para que pueda embeberse en la imagen QR o enviarse como string.
"""

import hmac
import hashlib
import base64
import json
import os
from dotenv import load_dotenv

load_dotenv()

# La misma SECRET_KEY que usa JWT para no necesitar otra variable de entorno
SECRET_KEY: str = os.getenv("SECRET_KEY", "clave_fallback_segura")


def sign_qr_payload(data: dict) -> str:
    """
    Recibe un dict con los datos del QR (sin firma), agrega la firma HMAC-SHA256
    y devuelve el payload completo codificado en base64 URL-safe.

    Ejemplo de data de entrada:
        {
            "espacio_id": 3,
            "slot_id": "slot_03",
            "usuario_id": 7,
            "timestamp": "2026-06-18T10:00:00"
        }
    """
    # Serializar con separadores compactos y claves ordenadas para firma determinista
    json_data = json.dumps(data, separators=(",", ":"), sort_keys=True)

    signature = hmac.new(
        SECRET_KEY.encode(),
        msg=json_data.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()

    # Agregar firma al payload
    signed = dict(data)
    signed["signature"] = signature

    encoded = base64.urlsafe_b64encode(
        json.dumps(signed, separators=(",", ":"), sort_keys=True).encode()
    ).decode()

    return encoded


def decode_qr_payload(encoded: str) -> dict:
    """
    Decodifica un payload QR base64 y devuelve el dict completo (incluyendo 'signature').
    Lanza ValueError si el encoding es inválido.
    """
    try:
        decoded = base64.urlsafe_b64decode(encoded.encode()).decode()
        return json.loads(decoded)
    except Exception as exc:
        raise ValueError(f"QR payload inválido: {exc}") from exc


def verify_qr_signature(data: dict) -> bool:
    """
    Verifica que la firma HMAC del payload QR sea válida.
    Acepta tanto un dict ya decodificado (con 'signature') como el string base64.

    Devuelve True si la firma es correcta, False en caso contrario.
    """
    if "signature" not in data:
        return False

    received_signature = data["signature"]

    # Reconstruir el JSON original (sin la firma) con las mismas opciones de serialización
    data_copy = {k: v for k, v in data.items() if k != "signature"}
    json_data = json.dumps(data_copy, separators=(",", ":"), sort_keys=True)

    expected_signature = hmac.new(
        SECRET_KEY.encode(),
        msg=json_data.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(received_signature, expected_signature)
