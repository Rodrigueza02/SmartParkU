
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.db.base import Base


class Acceso(Base):
    __tablename__ = "accesos"

    id_acceso   = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_usuario  = Column(Integer, ForeignKey("usuarios.id_usuario"),   nullable=True, index=True)
    id_vehiculo = Column(Integer, ForeignKey("vehiculos.id_vehiculo"), nullable=True, index=True)
    # FK to the legacy 'espacios' table (v1 schema — migration to espacios_parqueo is Phase 2.4)
    id_espacio  = Column(Integer, ForeignKey("espacios.id_espacio"),   nullable=True, index=True)
    hora_entrada = Column(DateTime, nullable=True)
    hora_salida  = Column(DateTime, nullable=True)
    metodo       = Column(String(50), nullable=True)
