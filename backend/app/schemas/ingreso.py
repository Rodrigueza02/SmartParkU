"""
schemas/ingreso.py
------------------
Esquemas Pydantic para el módulo de control de acceso trimodal.

Flujo:
  Portería (RFID | CARNET | QR_ENTRADA) → crea Acceso con hora_entrada
  Celda     (QR del puesto individual)   → asocia espacio + puesto_confirmado_en
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ─────────────────────────────────────────────────────────────────────────────
# REQUESTS — Entrada por portería
# ─────────────────────────────────────────────────────────────────────────────

class IngresoRFIDRequest(BaseModel):
    """Entrada vía lector RFID. El hardware envía el tag leído."""
    rfid_tag_id: str = Field(
        ...,
        description="Identificador del tag RFID leído en la portería",
        examples=["RFID-A1B2C3D4"],
    )


class IngresoCarnetRequest(BaseModel):
    """Entrada vía carnet institucional (código de barras, QR o NFC)."""
    carnet_id: str = Field(
        ...,
        description="Identificador del carnet universitario",
        examples=["EST-20230045"],
    )


class IngresoQREntradaRequest(BaseModel):
    """
    Entrada vía QR general de portería.
    El usuario escanea el QR físico de la puerta desde la app.
    El backend identifica al usuario a través del JWT en el header.
    """
    # No requiere cuerpo adicional: el usuario se obtiene del JWT.
    # Se incluye por consistencia de la API y para casos de extensión futura.
    pass


# ─────────────────────────────────────────────────────────────────────────────
# REQUEST — Confirmación de celda (QR del puesto individual)
# ─────────────────────────────────────────────────────────────────────────────

class OcuparPuestoRequest(BaseModel):
    """
    Escaneo del QR físico adherido al puesto de estacionamiento.
    Puede enviarse con o sin id_usuario dependiendo de si el dispositivo
    tiene sesión activa en la app.
    """
    qr_identifier: str = Field(
        ...,
        description="Código único del puesto escaneado (ej: QR_PUESTO_C-01)",
        examples=["QR_PUESTO_C-01", "QR_PUESTO_M-02"],
    )
    id_usuario: Optional[int] = Field(
        None,
        description="ID del usuario que ocupa el puesto (si lo envía la app)",
    )


# ─────────────────────────────────────────────────────────────────────────────
# RESPONSE — Ingreso por portería (los 3 métodos usan la misma respuesta)
# ─────────────────────────────────────────────────────────────────────────────

class IngresoResponse(BaseModel):
    """Respuesta unificada para los 3 métodos de ingreso por portería."""
    acceso_id: int
    id_usuario: Optional[int] = None
    id_vehiculo: Optional[int] = None
    metodo: str = Field(description="RFID | CARNET | QR_ENTRADA")
    hora_entrada: datetime
    talanquera_abierta: bool = True
    mensaje: str

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────────────────────────────────────
# RESPONSE — Confirmación de celda
# ─────────────────────────────────────────────────────────────────────────────

class OcuparPuestoResponse(BaseModel):
    """Respuesta tras confirmar el puesto de estacionamiento."""
    acceso_id: int
    id_usuario: Optional[int] = None
    id_vehiculo: Optional[int] = None
    espacio_id: int
    slot_id: str
    label: str
    tipo: str
    puesto_confirmado_en: datetime
    mensaje: str

    class Config:
        from_attributes = True
