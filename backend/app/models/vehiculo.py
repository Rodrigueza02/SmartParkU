
from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base


class Vehiculo(Base):
    __tablename__ = "vehiculos"

    id_vehiculo = Column(Integer, primary_key=True, index=True, autoincrement=True)
    placa = Column(String(20), nullable=True)
    tipo = Column(String(20), nullable=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=True, index=True)
