from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# ─── Auth ─────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    """Esquema para la petición de inicio de sesión."""
    correo: EmailStr
    password: str


class UserResponse(BaseModel):
    """Datos básicos del usuario para incluir en el payload de respuesta."""
    nombre: str
    rol: str
    estado: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """
    Respuesta exitosa de autenticación.
    Contiene el token JWT y metadatos del usuario para el Frontend adaptativo.
    """
    access_token: str
    token_type: str = "bearer"
    # Datos críticos para que el Frontend de la UCC renderice el Dashboard correcto
    nombre: str
    rol: str
    estado: str


# ─── Parking Slots ────────────────────────────────────────────────────────────

class EspacioParqueoBase(BaseModel):
    """Campos base de un espacio de parqueo."""
    slot_id: str
    label: str
    tipo: str       # 'carro' | 'moto' | 'bicicleta' | 'vip'
    status: str     # 'libre' | 'ocupado'


class EspacioParqueoResponse(EspacioParqueoBase):
    """
    Respuesta completa de un espacio de parqueo.
    Incluye el estado en tiempo real del sensor y el ID de base de datos.
    """
    id: int
    distancia_cm: Optional[float] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ParkingEstadoResponse(BaseModel):
    """
    Respuesta del endpoint /api/v1/parking/slots.
    Devuelve todos los espacios con su estado actual y los totales.
    """
    espacios: list[EspacioParqueoResponse]
    total_libre: int
    total_ocupado: int
    total_espacios: int
