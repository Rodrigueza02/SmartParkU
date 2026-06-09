
from sqlalchemy import Column, Integer, String
from app.db.base import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(100), nullable=False)
    rol = Column(String(50), nullable=False)
    estado = Column(String(50), default="Activo")

