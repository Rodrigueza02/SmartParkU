
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories import UserRepository
from app.core import verify_password, create_access_token
from app.schemas import TokenResponse


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def login(self, correo: str, password: str) -> TokenResponse:
        user = self.user_repo.get_by_email(correo)
        if not user or not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Correo o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if user.estado.lower() != "activo":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="La cuenta se encuentra inactiva. Contacte al administrador de la UCC."
            )
        access_token = create_access_token(data={"sub": user.correo, "rol": user.rol})
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            nombre=user.nombre,
            rol=user.rol,
            estado=user.estado
        )

