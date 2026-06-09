
from sqlalchemy.orm import Session
from app.models import Usuario


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, correo: str) -> Usuario | None:
        return self.db.query(Usuario).filter(Usuario.correo == correo).first()

    def create(self, nombre: str, correo: str, password: str, rol: str, estado: str = "Activo") -> Usuario:
        user = Usuario(nombre=nombre, correo=correo, password=password, rol=rol, estado=estado)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

