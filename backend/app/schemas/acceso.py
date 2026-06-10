
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AccesoCreate(BaseModel):
    id_usuario:  int
    id_vehiculo: Optional[int] = None
    id_espacio:  Optional[int] = None
    hora_entrada: Optional[datetime] = None
    metodo:      Optional[str] = None


class AccesoUpdate(BaseModel):
    id_usuario:  Optional[int] = None
    id_vehiculo: Optional[int] = None
    id_espacio:  Optional[int] = None
    hora_entrada: Optional[datetime] = None
    hora_salida:  Optional[datetime] = None
    metodo:      Optional[str] = None


class AccesoResponse(BaseModel):
    id_acceso:   int
    id_usuario:  Optional[int] = None
    id_vehiculo: Optional[int] = None
    id_espacio:  Optional[int] = None
    hora_entrada: Optional[datetime] = None
    hora_salida:  Optional[datetime] = None
    metodo:      Optional[str] = None

    class Config:
        from_attributes = True
