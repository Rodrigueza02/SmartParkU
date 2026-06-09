
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class EspacioParqueoBase(BaseModel):
    slot_id: str
    label: str
    tipo: str
    status: str


class EspacioParqueoResponse(EspacioParqueoBase):
    id: int
    distancia_cm: Optional[float] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ParkingEstadoResponse(BaseModel):
    espacios: list[EspacioParqueoResponse]
    total_libre: int
    total_ocupado: int
    total_espacios: int

