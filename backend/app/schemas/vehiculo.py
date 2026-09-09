
from pydantic import BaseModel
from typing import Optional


class VehiculoCreate(BaseModel):
    placa: str
    tipo: str
    id_usuario: int
    rfid_tag_id: Optional[str] = None


class VehiculoUpdate(BaseModel):
    placa: Optional[str] = None
    tipo: Optional[str] = None
    id_usuario: Optional[int] = None
    rfid_tag_id: Optional[str] = None


class VehiculoResponse(BaseModel):
    id_vehiculo: int
    placa: Optional[str] = None
    tipo: Optional[str] = None
    id_usuario: Optional[int] = None
    rfid_tag_id: Optional[str] = None

    class Config:
        from_attributes = True
