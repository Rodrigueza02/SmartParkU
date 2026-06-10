
from app.schemas.auth import LoginRequest, UserResponse, TokenResponse
from app.schemas.parking import EspacioParqueoBase, EspacioParqueoResponse, ParkingEstadoResponse
from app.schemas.vehiculo import VehiculoCreate, VehiculoUpdate, VehiculoResponse
from app.schemas.acceso import AccesoCreate, AccesoUpdate, AccesoResponse

__all__ = [
    "LoginRequest", "UserResponse", "TokenResponse",
    "EspacioParqueoBase", "EspacioParqueoResponse", "ParkingEstadoResponse",
    "VehiculoCreate", "VehiculoUpdate", "VehiculoResponse",
    "AccesoCreate", "AccesoUpdate", "AccesoResponse",
]
