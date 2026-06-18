
from pydantic import BaseModel, EmailStr
from typing import Optional


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
