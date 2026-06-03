from pydantic import BaseModel, EmailStr
from typing import Optional

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
