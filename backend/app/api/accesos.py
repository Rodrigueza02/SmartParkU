
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.acceso import AccesoCreate, AccesoUpdate, AccesoResponse
from app.services.acceso_service import AccesoService
from app.core.security import get_current_user, require_roles

router = APIRouter(prefix="/api/v1/accesos", tags=["accesos"])

# Alias de dependencias para legibilidad
_any_auth   = Depends(get_current_user)
_admin_only = Depends(require_roles("SuperAdmin", "Administrativo"))


@router.get("/", response_model=list[AccesoResponse], dependencies=[_admin_only])
def get_accesos(db: Session = Depends(get_db)):
    """Solo admins pueden ver todos los accesos."""
    return AccesoService(db).get_all()


@router.get("/usuario/{id_usuario}", response_model=list[AccesoResponse], dependencies=[_any_auth])
def get_accesos_por_usuario(id_usuario: int, db: Session = Depends(get_db)):
    return AccesoService(db).get_by_usuario(id_usuario)


@router.get("/vehiculo/{id_vehiculo}", response_model=list[AccesoResponse], dependencies=[_any_auth])
def get_accesos_por_vehiculo(id_vehiculo: int, db: Session = Depends(get_db)):
    return AccesoService(db).get_by_vehiculo(id_vehiculo)


@router.get("/{id_acceso}", response_model=AccesoResponse, dependencies=[_any_auth])
def get_acceso(id_acceso: int, db: Session = Depends(get_db)):
    return AccesoService(db).get_by_id(id_acceso)


@router.post("/", response_model=AccesoResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[_admin_only])
def create_acceso(data: AccesoCreate, db: Session = Depends(get_db)):
    """Solo admins pueden crear accesos manualmente."""
    return AccesoService(db).create(data)


@router.post("/{id_acceso}/salida", response_model=AccesoResponse, dependencies=[_any_auth])
def registrar_salida(id_acceso: int, db: Session = Depends(get_db)):
    """
    Registra la hora de salida del vehículo y libera el espacio en la BD y en el mapa.
    Devuelve 409 si el acceso ya tiene hora_salida registrada.
    """
    return AccesoService(db).registrar_salida(id_acceso)


@router.put("/{id_acceso}", response_model=AccesoResponse, dependencies=[_admin_only])
def update_acceso(id_acceso: int, data: AccesoUpdate, db: Session = Depends(get_db)):
    return AccesoService(db).update(id_acceso, data)


@router.delete("/{id_acceso}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[_admin_only])
def delete_acceso(id_acceso: int, db: Session = Depends(get_db)):
    AccesoService(db).delete(id_acceso)
