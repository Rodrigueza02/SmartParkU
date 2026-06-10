
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import Usuario
from app.repositories.vehiculo_repository import VehiculoRepository
from app.schemas.vehiculo import VehiculoCreate, VehiculoUpdate, VehiculoResponse


class VehiculoService:
    def __init__(self, db: Session):
        self.db = db
        self.vehiculo_repo = VehiculoRepository(db)

    # ── helpers ──────────────────────────────────────────────────────────────

    def _get_usuario_or_404(self, id_usuario: int) -> Usuario:
        usuario = self.db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con id {id_usuario} no encontrado"
            )
        return usuario

    def _get_vehiculo_or_404(self, id_vehiculo: int):
        vehiculo = self.vehiculo_repo.get_by_id(id_vehiculo)
        if not vehiculo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vehículo con id {id_vehiculo} no encontrado"
            )
        return vehiculo

    # ── public methods ────────────────────────────────────────────────────────

    def get_all(self) -> list[VehiculoResponse]:
        vehiculos = self.vehiculo_repo.get_all()
        return [VehiculoResponse.model_validate(v) for v in vehiculos]

    def get_by_id(self, id_vehiculo: int) -> VehiculoResponse:
        vehiculo = self._get_vehiculo_or_404(id_vehiculo)
        return VehiculoResponse.model_validate(vehiculo)

    def get_by_usuario(self, id_usuario: int) -> list[VehiculoResponse]:
        self._get_usuario_or_404(id_usuario)
        vehiculos = self.vehiculo_repo.get_by_usuario(id_usuario)
        return [VehiculoResponse.model_validate(v) for v in vehiculos]

    def create(self, data: VehiculoCreate) -> VehiculoResponse:
        self._get_usuario_or_404(data.id_usuario)
        vehiculo = self.vehiculo_repo.create(
            placa=data.placa,
            tipo=data.tipo,
            id_usuario=data.id_usuario,
        )
        return VehiculoResponse.model_validate(vehiculo)

    def update(self, id_vehiculo: int, data: VehiculoUpdate) -> VehiculoResponse:
        vehiculo = self._get_vehiculo_or_404(id_vehiculo)
        if data.id_usuario is not None:
            self._get_usuario_or_404(data.id_usuario)
        vehiculo = self.vehiculo_repo.update(
            vehiculo=vehiculo,
            placa=data.placa,
            tipo=data.tipo,
            id_usuario=data.id_usuario,
        )
        return VehiculoResponse.model_validate(vehiculo)

    def delete(self, id_vehiculo: int) -> None:
        vehiculo = self._get_vehiculo_or_404(id_vehiculo)
        self.vehiculo_repo.delete(vehiculo)
