
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas import (
    LoginRequest, TokenResponse, RegisterRequest, RegisterResponse,
    ForgotPasswordRequest, ForgotPasswordResponse,
    ResetPasswordRequest, ResetPasswordResponse,
)
from app.services import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse, status_code=201)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Registra un nuevo usuario en el sistema, opcionalmente con vehículo."""
    return AuthService(db).register_student(
        nombre=request.nombre,
        correo=request.correo,
        password=request.password,
        carnet_id=request.carnet_id,
        rol=request.rol,
        tipo_vehiculo=request.tipo_vehiculo,
        placa_vehiculo=request.placa_vehiculo
    )


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Autentica al usuario y devuelve un JWT con rol e id_usuario."""
    return AuthService(db).login(request.correo, request.password)


@router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponse,
    summary="Solicitar reseteo de contraseña",
    description=(
        "Envía instrucciones de recuperación al correo registrado. "
        "La respuesta es genérica para no revelar si el correo existe."
    ),
)
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    return AuthService(db).forgot_password(request.correo)


@router.post(
    "/reset-password",
    response_model=ResetPasswordResponse,
    summary="Restablecer contraseña con token",
    description=(
        "Valida el token recibido por correo y actualiza la contraseña. "
        "El token expira en 30 minutos."
    ),
)
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    return AuthService(db).reset_password(request.token, request.nueva_password)
