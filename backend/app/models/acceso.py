
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Acceso(Base):
    __tablename__ = "accesos"

    id_acceso    = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_usuario   = Column(Integer, ForeignKey("usuarios.id_usuario"),         nullable=True, index=True)
    id_vehiculo  = Column(Integer, ForeignKey("vehiculos.id_vehiculo"),        nullable=True, index=True)
    id_espacio   = Column(Integer, ForeignKey("espacios_parqueo.id"),          nullable=True, index=True)
    hora_entrada = Column(DateTime, nullable=True)
    hora_salida  = Column(DateTime, nullable=True)
    metodo       = Column(String(50), nullable=True)

    # ORM relationships (lazy load — no circular import risk)
    usuario  = relationship("Usuario",       foreign_keys=[id_usuario],  lazy="select")
    vehiculo = relationship("Vehiculo",      foreign_keys=[id_vehiculo], lazy="select")
    espacio  = relationship("EspacioParqueo",foreign_keys=[id_espacio],  lazy="select")
