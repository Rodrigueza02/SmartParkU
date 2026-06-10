
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.acceso import AccesoCreate, AccesoUpdate, AccesoResponse
from app.services.acceso_service import AccesoService

router = APIRouter(prefix="/api/v1/accesos", tags=["accesos"])


@router.get("/", response_model=list[AccesoResponse])
def get_accesos(db: Session = Depends(get_db)):
    return AccesoService(db).get_all()


@router.get("/usuario/{id_usuario}", response_model=list[AccesoResponse])
def get_accesos_por_usuario(id_usuario: int, db: Session = Depends(get_db)):
    return AccesoService(db).get_by_usuario(id_usuario)


@router.get("/vehiculo/{id_vehiculo}", response_model=list[AccesoResponse])
def get_accesos_por_vehiculo(id_vehiculo: int, db: Session = Depends(get_db)):
    return AccesoService(db).get_by_vehiculo(id_vehiculo)


@router.get("/{id_acceso}", response_model=AccesoResponse)
def get_acceso(id_acceso: int, db: Session = Depends(get_db)):
    return AccesoService(db).get_by_id(id_acceso)


@router.post("/", response_model=AccesoResponse, status_code=status.HTTP_201_CREATED)
def create_acceso(data: AccesoCreate, db: Session = Depends(get_db)):
    return AccesoService(db).create(data)


@router.put("/{id_acceso}", response_model=AccesoResponse)
def update_acceso(id_acceso: int, data: AccesoUpdate, db: Session = Depends(get_db)):
    return AccesoService(db).update(id_acceso, data)


@router.delete("/{id_acceso}", status_code=status.HTTP_204_NO_CONTENT)
def delete_acceso(id_acceso: int, db: Session = Depends(get_db)):
    AccesoService(db).delete(id_acceso)
