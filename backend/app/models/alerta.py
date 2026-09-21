
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Alerta(Base):
    __tablename__ = "alertas"

    id_alerta = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    tipo = Column(String(50), nullable=False)  # 'seguridad', 'emergencia', 'reporte'
    mensaje = Column(Text, nullable=False)
    ubicacion = Column(String(200), nullable=True)
    estado = Column(String(50), default="pendiente")  # 'pendiente', 'revisada', 'resuelta'
    media_url = Column(String(500), nullable=True)  # URL de la foto/video
    media_type = Column(String(20), nullable=True)  # 'foto', 'video'
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_revision = Column(DateTime, nullable=True)
    revisado_por = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=True)
    
    # Relaciones
    usuario = relationship("Usuario", foreign_keys=[id_usuario], backref="alertas_creadas")
    revisor = relationship("Usuario", foreign_keys=[revisado_por], backref="alertas_revisadas")
