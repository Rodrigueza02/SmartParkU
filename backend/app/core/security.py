
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema Bearer — extrae el token del header Authorization: Bearer <token>
bearer_scheme = HTTPBearer(auto_error=True)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def _decode_token(token: str) -> dict:
    """Decodifica y valida el JWT. Lanza 401 si es inválido o expirado."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado. Inicia sesión nuevamente.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        correo: str = payload.get("sub")
        rol: str = payload.get("rol")
        if correo is None:
            raise credentials_exception
        return {"correo": correo, "rol": rol}
    except JWTError:
        raise credentials_exception


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """
    Dependencia reutilizable que valida el JWT y devuelve
    {"correo": ..., "rol": ...} del usuario autenticado.
    Usar con: current_user: dict = Depends(get_current_user)
    """
    return _decode_token(credentials.credentials)


def require_roles(*roles: str):
    """
    Fábrica de dependencias que restringe el acceso a uno o más roles.

    Uso:
        @router.get("/admin", dependencies=[Depends(require_roles("SuperAdmin", "Administrativo"))])
        @router.get("/me",    dependencies=[Depends(require_roles("Estudiante"))])
    """
    def _check(current_user: dict = Depends(get_current_user)):
        if current_user["rol"] not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Se requiere uno de los roles: {', '.join(roles)}.",
            )
        return current_user
    return _check

