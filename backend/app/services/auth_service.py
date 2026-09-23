
from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.repositories import UserRepository
from app.core import verify_password, create_access_token, get_password_hash
from app.schemas import TokenResponse, ForgotPasswordResponse, ResetPasswordResponse, RegisterResponse


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def register_student(
        self, 
        nombre: str, 
        correo: str, 
        password: str, 
        carnet_id: str = None,
        rol: str = "Estudiante",
        tipo_vehiculo: str = None,
        placa_vehiculo: str = None
    ) -> RegisterResponse:
        """
        Registra un nuevo usuario en el sistema.
        Opcionalmente crea un vehículo asociado si se proporcionan tipo y placa.
        """
        # Verificar si el correo ya está registrado
        existing_user = self.user_repo.get_by_email(correo)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo ya está registrado. Por favor inicia sesión o recupera tu contraseña."
            )
        
        # Verificar si el carnet_id ya existe (si se proporcionó)
        if carnet_id:
            from app.models import Usuario
            existing_carnet = self.db.query(Usuario).filter(Usuario.carnet_id == carnet_id).first()
            if existing_carnet:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El carnet universitario ya está registrado."
                )
        
        # Crear nuevo usuario
        from app.models import Usuario
        hashed_password = get_password_hash(password)
        new_user = Usuario(
            nombre=nombre,
            correo=correo,
            password=hashed_password,
            rol=rol,
            estado="Activo",
            carnet_id=carnet_id
        )
        
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        
        # Crear vehículo si se proporcionaron los datos
        vehiculo_registrado = False
        if tipo_vehiculo and placa_vehiculo:
            from app.models import Vehiculo
            nuevo_vehiculo = Vehiculo(
                placa=placa_vehiculo,
                tipo=tipo_vehiculo,
                id_usuario=new_user.id_usuario
            )
            self.db.add(nuevo_vehiculo)
            self.db.commit()
            vehiculo_registrado = True
        
        return RegisterResponse(
            mensaje="Cuenta creada exitosamente. Ya puedes iniciar sesión.",
            id_usuario=new_user.id_usuario,
            correo=new_user.correo,
            rol=new_user.rol,
            vehiculo_registrado=vehiculo_registrado
        )

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

