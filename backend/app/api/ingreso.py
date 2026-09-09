"""
api/ingreso.py
--------------
Endpoints del módulo de control de acceso trimodal.

Portería (ETAPA 1):
  POST /api/v1/parking/entry/rfid         → Ingreso vía lector RFID
  POST /api/v1/parking/entry/carnet       → Ingreso vía carnet institucional
  POST /api/v1/parking/entry/qr-general   → Ingreso vía QR general de portería (requiere JWT)

Celda (ETAPA 2):
  POST /api/v1/parking/occupy-spot        → Confirmar puesto escaneando QR individual
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import get_current_user
from app.schemas.ingreso import (
    IngresoRFIDRequest,
    IngresoCarnetRequest,
    IngresoResponse,
    OcuparPuestoRequest,
    OcuparPuestoResponse,
)
from app.services.ingreso_service import IngresoService

router = APIRouter(prefix="/api/v1/parking", tags=["control-acceso"])

# ─────────────────────────────────────────────────────────────────────────────
# ETAPA 1 — Entrada por portería
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/entry/rfid",
    response_model=IngresoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingreso vía RFID",
    description=(
        "El lector RFID de la portería envía el tag leído. "
        "El sistema identifica el vehículo y su propietario, abre la talanquera "
        "y crea una sesión de ingreso. **No requiere JWT** — lo invoca el hardware."
    ),
)
def entry_rfid(data: IngresoRFIDRequest, db: Session = Depends(get_db)):
    return IngresoService(db).ingreso_rfid(data)


@router.post(
    "/entry/carnet",
    response_model=IngresoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingreso vía carnet institucional",
    description=(
        "El terminal de portería escanea el carnet universitario (código de barras, "
        "QR institucional o NFC). El sistema valida al usuario, abre la talanquera "
        "y crea una sesión de ingreso. **No requiere JWT** — lo invoca el hardware."
    ),
)
def entry_carnet(data: IngresoCarnetRequest, db: Session = Depends(get_db)):
    return IngresoService(db).ingreso_carnet(data)


@router.post(
    "/entry/qr-general",
    response_model=IngresoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingreso vía QR general de portería",
    description=(
        "El usuario escanea el QR físico de la portería desde la app móvil/web. "
        "Requiere sesión activa (JWT). El backend identifica al usuario por el token, "
        "abre la talanquera y crea la sesión de ingreso."
    ),
)
def entry_qr_general(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return IngresoService(db).ingreso_qr_entrada(current_user)


# ─────────────────────────────────────────────────────────────────────────────
# ETAPA 2 — Confirmación de celda
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/occupy-spot",
    response_model=OcuparPuestoResponse,
    status_code=status.HTTP_200_OK,
    summary="Confirmar puesto de estacionamiento",
    description=(
        "El usuario escanea el QR único del puesto físico desde la app. "
        "El sistema verifica que exista una sesión activa de ingreso (sin timeout), "
        "que el puesto esté disponible y lo marca como ocupado en tiempo real. "
        "Si el puesto ya está ocupado, devuelve 409 con mensaje de error."
    ),
)
def occupy_spot(
    data: OcuparPuestoRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # Priorizar el id_usuario del JWT sobre el body para seguridad
    data.id_usuario = current_user["id_usuario"]
    return IngresoService(db).ocupar_puesto(data)
