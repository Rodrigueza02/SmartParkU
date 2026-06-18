
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.vehiculo import VehiculoCreate, VehiculoUpdate, VehiculoResponse
from app.services.vehiculo_service import VehiculoService

router = APIRouter(prefix="/api/v1/vehiculos", tags=["vehiculos"])


@router.get("/", response_model=list[VehiculoResponse])
def get_vehiculos(db: Session = Depends(get_db)):
    return VehiculoService(db).get_all()


@router.get("/{id_vehiculo}", response_model=VehiculoResponse)
def get_vehiculo(id_vehiculo: int, db: Session = Depends(get_db)):
    return VehiculoService(db).get_by_id(id_vehiculo)


@router.get("/usuario/{id_usuario}", response_model=list[VehiculoResponse])
def get_vehiculos_por_usuario(id_usuario: int, db: Session = Depends(get_db)):
    return VehiculoService(db).get_by_usuario(id_usuario)


@router.post("/", response_model=VehiculoResponse, status_code=status.HTTP_201_CREATED)
def create_vehiculo(data: VehiculoCreate, db: Session = Depends(get_db)):
    return VehiculoService(db).create(data)


@router.put("/{id_vehiculo}", response_model=VehiculoResponse)
def update_vehiculo(id_vehiculo: int, data: VehiculoUpdate, db: Session = Depends(get_db)):
    return VehiculoService(db).update(id_vehiculo, data)


@router.delete("/{id_vehiculo}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehiculo(id_vehiculo: int, db: Session = Depends(get_db)):
    VehiculoService(db).delete(id_vehiculo)
