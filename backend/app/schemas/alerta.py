
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class AlertaCreate(BaseModel):
    tipo: str
    mensaje: str
    ubicacion: Optional[str] = None
    media_type: Optional[str] = None  # 'foto', 'video'
    
    @field_validator('tipo')
    @classmethod
    def validate_tipo(cls, v):
        tipos_validos = ['seguridad', 'emergencia', 'reporte']
        if v not in tipos_validos:
            raise ValueError(f'Tipo debe ser uno de: {", ".join(tipos_validos)}')
        return v
    
    @field_validator('mensaje')
    @classmethod
    def validate_mensaje(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('El mensaje debe tener al menos 10 caracteres')
        return v.strip()


class AlertaResponse(BaseModel):
    id_alerta: int
    id_usuario: int
    tipo: str
    mensaje: str
    ubicacion: Optional[str]
    estado: str
    media_url: Optional[str]
    media_type: Optional[str]
    fecha_creacion: datetime
    fecha_revision: Optional[datetime]
    revisado_por: Optional[int]
    usuario_nombre: Optional[str] = None
    revisor_nombre: Optional[str] = None
    
    class Config:
        from_attributes = True


class AlertaUpdate(BaseModel):
    estado: str
    
    @field_validator('estado')
    @classmethod
    def validate_estado(cls, v):
        estados_validos = ['pendiente', 'revisada', 'resuelta']
        if v not in estados_validos:
            raise ValueError(f'Estado debe ser uno de: {", ".join(estados_validos)}')
        return v


class AlertaListResponse(BaseModel):
    total: int
    pendientes: int
    revisadas: int
    resueltas: int
    alertas: list[AlertaResponse]
