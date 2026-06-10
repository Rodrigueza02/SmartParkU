
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.acceso import Acceso


class AccesoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Acceso]:
        return self.db.query(Acceso).order_by(Acceso.id_acceso).all()

    def get_by_id(self, id_acceso: int) -> Acceso | None:
        return self.db.query(Acceso).filter(Acceso.id_acceso == id_acceso).first()

    def get_by_usuario(self, id_usuario: int) -> list[Acceso]:
        return (
            self.db.query(Acceso)
            .filter(Acceso.id_usuario == id_usuario)
            .order_by(Acceso.id_acceso)
            .all()
        )

    def get_by_vehiculo(self, id_vehiculo: int) -> list[Acceso]:
        return (
            self.db.query(Acceso)
            .filter(Acceso.id_vehiculo == id_vehiculo)
            .order_by(Acceso.id_acceso)
            .all()
        )

    def create(
        self,
        id_usuario:  int,
        id_vehiculo: int | None,
        id_espacio:  int | None,
        hora_entrada: datetime | None,
        metodo:      str | None,
    ) -> Acceso:
        acceso = Acceso(
            id_usuario=id_usuario,
            id_vehiculo=id_vehiculo,
            id_espacio=id_espacio,
            hora_entrada=hora_entrada,
            metodo=metodo,
        )
        self.db.add(acceso)
        self.db.commit()
        self.db.refresh(acceso)
        return acceso

    def update(
        self,
        acceso:      Acceso,
        id_usuario:  int | None,
        id_vehiculo: int | None,
        id_espacio:  int | None,
        hora_entrada: datetime | None,
        hora_salida:  datetime | None,
        metodo:      str | None,
    ) -> Acceso:
        if id_usuario is not None:
            acceso.id_usuario = id_usuario
        if id_vehiculo is not None:
            acceso.id_vehiculo = id_vehiculo
        if id_espacio is not None:
            acceso.id_espacio = id_espacio
        if hora_entrada is not None:
            acceso.hora_entrada = hora_entrada
        if hora_salida is not None:
            acceso.hora_salida = hora_salida
        if metodo is not None:
            acceso.metodo = metodo
        self.db.commit()
        self.db.refresh(acceso)
        return acceso

    def delete(self, acceso: Acceso) -> None:
        self.db.delete(acceso)
        self.db.commit()
