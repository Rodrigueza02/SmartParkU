"""
api/qr.py
---------
Endpoints para la funcionalidad de QR del parqueadero SmartParkU.

Flujo:
  POST /api/v1/qr/generar       → El estudiante solicita su QR (recibe imagen PNG base64)
  POST /api/v1/qr/escanear      → Al llegar a la entrada se escanea → asigna cupo y crea acceso
  GET  /api/v1/qr/acceso/{id}   → Consulta el detalle de un acceso creado por QR
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.qr import (
    QRGenerarRequest,
    QRGeneradoResponse,
    QREscanearRequest,
    QREscanearResponse,
)
from app.services.qr_service import QRService
from app.schemas.acceso import AccesoResponse
from app.services.acceso_service import AccesoService
from app.core.security import get_current_user, require_roles

router = APIRouter(prefix="/api/v1/qr", tags=["qr"])

# El escaneo en la entrada lo puede hacer cualquier usuario autenticado
# (incluso el lector físico autenticado como Administrativo)
_any_auth       = Depends(get_current_user)
_puede_generar  = Depends(require_roles("SuperAdmin", "Administrativo", "Estudiante", "Visitante"))


@router.post(
    "/generar",
    response_model=QRGeneradoResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[_puede_generar],
    summary="Generar QR de acceso al parqueadero",
    description=(
        "Busca el primer espacio libre disponible, genera un payload firmado "
        "con HMAC-SHA256 y devuelve la imagen QR en base64. "
        "El QR expira en 10 minutos si no se escanea."
    ),
)
def generar_qr(
    data: QRGenerarRequest,
    db: Session = Depends(get_db),
):
    return QRService(db).generar_qr(data)


@router.post(
    "/escanear",
    response_model=QREscanearResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[_any_auth],
    summary="Escanear QR y asignar cupo en el parqueadero",
    description=(
        "Recibe el token del QR escaneado, verifica la firma HMAC y la expiración, "
        "marca el espacio como 'ocupado' y crea el registro de acceso. "
        "Si el espacio ya fue tomado por otro estudiante devuelve 409."
    ),
)
def escanear_qr(
    data: QREscanearRequest,
    db: Session = Depends(get_db),
):
    """
    ### Casos de error
    - `400` → QR malformado (base64 inválido)
    - `401` → Firma HMAC no válida (QR manipulado)
    - `409` → El espacio ya fue ocupado por otro estudiante
    - `410` → El QR expiró (pasaron más de 10 minutos)
    """
    return QRService(db).escanear_qr(data)


@router.get(
    "/acceso/{id_acceso}",
    response_model=AccesoResponse,
    dependencies=[_any_auth],
    summary="Consultar detalle de un acceso registrado por QR",
)
def get_acceso_qr(
    id_acceso: int,
    db: Session = Depends(get_db),
):
    """Devuelve el acceso creado al escanear el QR."""
    return AccesoService(db).get_by_id(id_acceso)
