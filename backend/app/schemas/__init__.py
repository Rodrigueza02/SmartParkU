
from app.schemas.auth import (
    LoginRequest, UserResponse, TokenResponse,
    RegisterRequest, RegisterResponse,
    ForgotPasswordRequest, ForgotPasswordResponse,
    ResetPasswordRequest, ResetPasswordResponse,
)
from app.schemas.parking import EspacioParqueoBase, EspacioParqueoResponse, ParkingEstadoResponse
from app.schemas.vehiculo import VehiculoCreate, VehiculoUpdate, VehiculoResponse
from app.schemas.acceso import AccesoCreate, AccesoUpdate, AccesoResponse
from app.schemas.qr import (
    QRGenerarRequest,
    QRGeneradoResponse,
    QREscanearRequest,
    QREscanearResponse,
)
from app.schemas.ingreso import (
    IngresoRFIDRequest,
    IngresoCarnetRequest,
    IngresoQREntradaRequest,
    OcuparPuestoRequest,
    IngresoResponse,
    OcuparPuestoResponse,
)
from app.schemas.alerta import (
    AlertaCreate,
    AlertaResponse,
    AlertaUpdate,
    AlertaListResponse,
)

__all__ = [
    "LoginRequest", "UserResponse", "TokenResponse",
    "RegisterRequest", "RegisterResponse",
    "ForgotPasswordRequest", "ForgotPasswordResponse",
    "ResetPasswordRequest", "ResetPasswordResponse",
    "EspacioParqueoBase", "EspacioParqueoResponse", "ParkingEstadoResponse",
    "VehiculoCreate", "VehiculoUpdate", "VehiculoResponse",
    "AccesoCreate", "AccesoUpdate", "AccesoResponse",
    "QRGenerarRequest", "QRGeneradoResponse", "QREscanearRequest", "QREscanearResponse",
    "IngresoRFIDRequest", "IngresoCarnetRequest", "IngresoQREntradaRequest",
    "OcuparPuestoRequest", "IngresoResponse", "OcuparPuestoResponse",
    "AlertaCreate", "AlertaResponse", "AlertaUpdate", "AlertaListResponse",
]
