
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.db.base import Base


class EspacioParqueo(Base):
    __tablename__ = "espacios_parqueo"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    slot_id = Column(String(20), unique=True, index=True, nullable=False)
    label = Column(String(20), nullable=False)
    tipo = Column(String(20), nullable=False)
    status = Column(String(20), default="libre", nullable=False)
    distancia_cm = Column(Float, nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

