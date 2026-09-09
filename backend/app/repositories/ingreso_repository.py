"""
repositories/ingreso_repository.py
-----------------------------------
Acceso a datos para el módulo de control de acceso trimodal.
Sólo hace queries; toda la lógica de negocio vive en IngresoService.
"""

from datetime import datetime
from sqlalchemy.orm import Session
from app.models.acceso import Acceso
from app.models.parking import EspacioParqueo
from app.models.user import Usuario
from app.models.vehiculo import Vehiculo


class IngresoRepository:
    def __init__(self, db: Session):
        self.db = db

    # ── Búsquedas de identidad ────────────────────────────────────────────────

    def get_vehiculo_by_rfid(self, rfid_tag_id: str) -> Vehiculo | None:
        return (
            self.db.query(Vehiculo)
            .filter(Vehiculo.rfid_tag_id == rfid_tag_id)
            .first()
        )

    def get_usuario_by_carnet(self, carnet_id: str) -> Usuario | None:
        return (
            self.db.query(Usuario)
            .filter(Usuario.carnet_id == carnet_id)
            .first()
        )

    def get_vehiculo_by_usuario(self, id_usuario: int) -> Vehiculo | None:
        """Devuelve el primer vehículo activo registrado para el usuario."""
        return (
            self.db.query(Vehiculo)
            .filter(Vehiculo.id_usuario == id_usuario)
            .first()
        )

    def get_usuario_by_id(self, id_usuario: int) -> Usuario | None:
        return (
            self.db.query(Usuario)
            .filter(Usuario.id_usuario == id_usuario)
            .first()
        )

    # ── Espacios ──────────────────────────────────────────────────────────────

    def get_espacio_by_qr_identifier(self, qr_identifier: str) -> EspacioParqueo | None:
        return (
            self.db.query(EspacioParqueo)
            .filter(EspacioParqueo.qr_identifier == qr_identifier)
            .first()
        )

    # ── Accesos (sesiones) ────────────────────────────────────────────────────

    def get_sesion_activa_by_usuario(self, id_usuario: int) -> Acceso | None:
        """
        Devuelve la sesión de ingreso abierta (hora_entrada existe, hora_salida None)
        más reciente para el usuario.
        """
        return (
            self.db.query(Acceso)
            .filter(
                Acceso.id_usuario == id_usuario,
                Acceso.hora_salida.is_(None),
            )
            .order_by(Acceso.hora_entrada.desc())
            .first()
        )

    def get_sesion_activa_by_vehiculo(self, id_vehiculo: int) -> Acceso | None:
        """Sesión abierta por id de vehículo (para ingreso RFID)."""
        return (
            self.db.query(Acceso)
            .filter(
                Acceso.id_vehiculo == id_vehiculo,
                Acceso.hora_salida.is_(None),
            )
            .order_by(Acceso.hora_entrada.desc())
            .first()
        )

    def crear_acceso_porteria(
        self,
        id_usuario: int | None,
        id_vehiculo: int | None,
        metodo: str,
        hora_entrada: datetime,
    ) -> Acceso:
        """Crea el registro de ingreso por portería. El espacio se asigna después."""
        acceso = Acceso(
            id_usuario=id_usuario,
            id_vehiculo=id_vehiculo,
            id_espacio=None,
            hora_entrada=hora_entrada,
            hora_salida=None,
            metodo=metodo,
            puesto_confirmado_en=None,
        )
        self.db.add(acceso)
        self.db.commit()
        self.db.refresh(acceso)
        return acceso

    def asignar_puesto(
        self,
        acceso: Acceso,
        espacio: EspacioParqueo,
        ahora: datetime,
    ) -> Acceso:
        """Vincula el espacio al acceso existente y registra el timestamp de confirmación."""
        acceso.id_espacio = espacio.id
        acceso.puesto_confirmado_en = ahora
        self.db.commit()
        self.db.refresh(acceso)
        return acceso

    def ocupar_espacio(self, espacio: EspacioParqueo, ahora: datetime) -> EspacioParqueo:
        """Marca el espacio como ocupado en la BD."""
        espacio.status = "ocupado"
        espacio.updated_at = ahora
        self.db.commit()
        self.db.refresh(espacio)
        return espacio
