
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import Usuario
from app.models.vehiculo import Vehiculo
from app.repositories.acceso_repository import AccesoRepository
from app.schemas.acceso import AccesoCreate, AccesoUpdate, AccesoResponse


class AccesoService:
    def __init__(self, db: Session):
        self.db = db
        self.acceso_repo = AccesoRepository(db)

    # ── helpers ──────────────────────────────────────────────────────────────

    def _get_acceso_or_404(self, id_acceso: int):
        acceso = self.acceso_repo.get_by_id(id_acceso)
        if not acceso:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Acceso con id {id_acceso} no encontrado",
            )
        return acceso

    def _get_usuario_or_404(self, id_usuario: int) -> Usuario:
        usuario = self.db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con id {id_usuario} no encontrado",
            )
        return usuario

    def _get_vehiculo_or_404(self, id_vehiculo: int) -> Vehiculo:
        vehiculo = self.db.query(Vehiculo).filter(Vehiculo.id_vehiculo == id_vehiculo).first()
        if not vehiculo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vehículo con id {id_vehiculo} no encontrado",
            )
        return vehiculo

    # ── public methods ────────────────────────────────────────────────────────

    def get_all(self) -> list[AccesoResponse]:
        accesos = self.acceso_repo.get_all()
        return [AccesoResponse.model_validate(a) for a in accesos]

    def get_by_id(self, id_acceso: int) -> AccesoResponse:
        acceso = self._get_acceso_or_404(id_acceso)
        return AccesoResponse.model_validate(acceso)

    def get_by_usuario(self, id_usuario: int) -> list[AccesoResponse]:
        self._get_usuario_or_404(id_usuario)
        accesos = self.acceso_repo.get_by_usuario(id_usuario)
        return [AccesoResponse.model_validate(a) for a in accesos]

    def get_by_vehiculo(self, id_vehiculo: int) -> list[AccesoResponse]:
        self._get_vehiculo_or_404(id_vehiculo)
        accesos = self.acceso_repo.get_by_vehiculo(id_vehiculo)
        return [AccesoResponse.model_validate(a) for a in accesos]

    def create(self, data: AccesoCreate) -> AccesoResponse:
        self._get_usuario_or_404(data.id_usuario)
        if data.id_vehiculo is not None:
            self._get_vehiculo_or_404(data.id_vehiculo)

        # Default hora_entrada to now if not provided
        hora_entrada = data.hora_entrada or datetime.now(timezone.utc).replace(tzinfo=None)

        acceso = self.acceso_repo.create(
            id_usuario=data.id_usuario,
            id_vehiculo=data.id_vehiculo,
            id_espacio=data.id_espacio,
            hora_entrada=hora_entrada,
            metodo=data.metodo,
        )
        return AccesoResponse.model_validate(acceso)

    def update(self, id_acceso: int, data: AccesoUpdate) -> AccesoResponse:
        acceso = self._get_acceso_or_404(id_acceso)
        if data.id_usuario is not None:
            self._get_usuario_or_404(data.id_usuario)
        if data.id_vehiculo is not None:
            self._get_vehiculo_or_404(data.id_vehiculo)
        acceso = self.acceso_repo.update(
            acceso=acceso,
            id_usuario=data.id_usuario,
            id_vehiculo=data.id_vehiculo,
            id_espacio=data.id_espacio,
            hora_entrada=data.hora_entrada,
            hora_salida=data.hora_salida,
            metodo=data.metodo,
        )
        return AccesoResponse.model_validate(acceso)

    def delete(self, id_acceso: int) -> None:
        acceso = self._get_acceso_or_404(id_acceso)
        self.acceso_repo.delete(acceso)
