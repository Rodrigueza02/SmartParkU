
from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories import UserRepository
from app.core import verify_password, create_access_token, get_password_hash
from app.schemas import TokenResponse, ForgotPasswordResponse, ResetPasswordResponse


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
        access_token = create_access_token(
            data={"sub": user.correo, "rol": user.rol, "id": user.id_usuario}
        )
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            nombre=user.nombre,
            rol=user.rol,
            estado=user.estado,
            id_usuario=user.id_usuario,
        )

    def forgot_password(self, correo: str) -> ForgotPasswordResponse:
        """
        Genera un token de reseteo de contraseña de corta duración (30 min).
        En producción este token se enviaría por correo electrónico.
        Por ahora lo devuelve en la respuesta para que el frontend pueda
        redirigir al formulario de nueva contraseña.

        NOTA PARA HELEN: cuando haya servidor de correo configurado,
        cambiar para enviar el token por email en lugar de devolverlo aquí.
        """
        user = self.user_repo.get_by_email(correo)
        # Respuesta genérica independiente de si el correo existe (evita enumeración de usuarios)
        mensaje_generico = (
            "Si el correo está registrado en SmartParkU, "
            "recibirás las instrucciones para restablecer tu contraseña."
        )

        if not user or user.estado.lower() != "activo":
            return ForgotPasswordResponse(mensaje=mensaje_generico)

        # Token firmado con expiración de 30 minutos, tipo 'reset'
        reset_token = create_access_token(
            data={"sub": user.correo, "type": "reset"},
            expires_delta=timedelta(minutes=30),
        )

        # TODO: enviar reset_token por correo al usuario
        # Por ahora se devuelve directamente para pruebas de frontend
        return ForgotPasswordResponse(
            mensaje=mensaje_generico,
            # campo extra solo en dev — quitar cuando se implemente el correo
            # reset_token=reset_token  # descomentar si se necesita en dev
        )

    def reset_password(self, token: str, nueva_password: str) -> ResetPasswordResponse:
        """
        Valida el token de reseteo y actualiza la contraseña del usuario.
        """
        from jose import jwt, JWTError
        from app.core.config import settings

        credentials_exception = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de reseteo inválido o expirado.",
        )
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            correo: str = payload.get("sub")
            tipo: str = payload.get("type")
            if correo is None or tipo != "reset":
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = self.user_repo.get_by_email(correo)
        if not user:
            raise credentials_exception

        if len(nueva_password) < 8:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="La nueva contraseña debe tener al menos 8 caracteres.",
            )

        user.password = get_password_hash(nueva_password)
        self.db.commit()

        return ResetPasswordResponse(mensaje="Contraseña actualizada correctamente. Ya puedes iniciar sesión.")

