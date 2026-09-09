from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.base import Base


class EspacioParqueo(Base):
    __tablename__ = "espacios_parqueo"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    slot_id = Column(String(20), unique=True, index=True, nullable=False)
    label = Column(String(20), nullable=False)
    tipo = Column(String(20), nullable=False)
    # Estado gestionado exclusivamente por el flujo QR: libre | ocupado | mantenimiento
    status = Column(String(20), default="libre", nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    # Código QR único físico adherido a cada celda (ej: QR_PUESTO_C-01)
    qr_identifier = Column(String(100), unique=True, nullable=True, index=True)
