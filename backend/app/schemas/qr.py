"""
schemas/qr.py
-------------
Schemas Pydantic para la funcionalidad de QR de parqueadero.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class QRGenerarRequest(BaseModel):
    """
    Datos necesarios para generar un QR de acceso al parqueadero.
    El frontend envía el id del usuario autenticado.
    """
    id_usuario: int
    id_vehiculo: Optional[int] = None


class QRGeneradoResponse(BaseModel):
    """
    Respuesta con la imagen QR en base64 y los datos del espacio asignado temporalmente.
    El QR es válido por un tiempo limitado (ver QR_EXPIRE_MINUTES en config).
    """
    espacio_id: int
    slot_id: str
    label: str
    tipo: str
    qr_token: str                           # payload firmado y codificado en base64
    qr_image_base64: str                    # PNG embebido como data:image/png;base64,...
    expira_en: datetime                     # timestamp UTC de expiración
    mensaje: str


class QREscanearRequest(BaseModel):
    """
    Payload que envía el frontend al escanear un QR con la cámara.
    Contiene el token decodificado del QR (el string base64).
    """
    qr_token: str


class QREscanearResponse(BaseModel):
    """
    Resultado del escaneo: acceso creado o error de validación.
    """
    acceso_id: int
    id_usuario: int
    id_vehiculo: Optional[int] = None
    espacio_id: int
    slot_id: str
    label: str
    hora_entrada: datetime
    mensaje: str
