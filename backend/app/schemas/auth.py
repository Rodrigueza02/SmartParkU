
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional


class RegisterRequest(BaseModel):
    nombre: str
    correo: EmailStr
    password: str
    carnet_id: Optional[str] = None

    @field_validator('nombre')
    @classmethod
    def validate_nombre(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('El nombre debe tener al menos 3 caracteres')
        return v.strip()

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('La contraseña debe tener al menos 6 caracteres')
        return v


class RegisterResponse(BaseModel):
    mensaje: str
    id_usuario: int
    correo: str


class LoginRequest(BaseModel):
    correo: EmailStr
    password: str


class UserResponse(BaseModel):
    nombre: str
    rol: str
    estado: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    nombre: str
    rol: str
    estado: str
    id_usuario: int


class ForgotPasswordRequest(BaseModel):
    correo: EmailStr


class ForgotPasswordResponse(BaseModel):
    mensaje: str


class ResetPasswordRequest(BaseModel):
    token: str
    nueva_password: str


class ResetPasswordResponse(BaseModel):
    mensaje: str
