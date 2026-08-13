
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import Usuario
from app.models.vehiculo import Vehiculo
from app.models.parking import EspacioParqueo
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

        hora_entrada = data.hora_entrada or datetime.now(timezone.utc).replace(tzinfo=None)

        acceso = self.acceso_repo.create(
            id_usuario=data.id_usuario,
            id_vehiculo=data.id_vehiculo,
            id_espacio=data.id_espacio,
            hora_entrada=hora_entrada,
            metodo=data.metodo,
        )
        return AccesoResponse.model_validate(acceso)

    def registrar_salida(self, id_acceso: int) -> AccesoResponse:
        """
        Registra la hora de salida del vehículo:
          1. Valida que el acceso exista y no tenga ya hora_salida.
          2. Pone hora_salida = ahora UTC.
          3. Libera el EspacioParqueo en la BD (status = 'libre').
          4. Propaga el cambio al mapa en tiempo real via WebSocket.
        """
        acceso = self._get_acceso_or_404(id_acceso)

        if acceso.hora_salida is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Este acceso ya tiene registrada una hora de salida.",
            )

        hora_salida = datetime.now(timezone.utc).replace(tzinfo=None)

        # Actualizar el acceso
        acceso = self.acceso_repo.update(
            acceso=acceso,
            id_usuario=None,
            id_vehiculo=None,
            id_espacio=None,
            hora_entrada=None,
            hora_salida=hora_salida,
            metodo=None,
        )

        # Liberar el espacio en la BD
        if acceso.id_espacio is not None:
            espacio = self.db.query(EspacioParqueo).filter(
                EspacioParqueo.id == acceso.id_espacio
            ).first()
            if espacio:
                espacio.status = "libre"
                espacio.updated_at = datetime.now(timezone.utc)
                self.db.commit()
                self.db.refresh(espacio)

                # Propagar al mapa en tiempo real
                from app.mqtt_client import update_slot_status
                update_slot_status(espacio.slot_id, "libre")

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
