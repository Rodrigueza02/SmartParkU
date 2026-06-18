
from sqlalchemy.orm import Session
from app.models.vehiculo import Vehiculo


class VehiculoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Vehiculo]:
        return self.db.query(Vehiculo).order_by(Vehiculo.id_vehiculo).all()

    def get_by_id(self, id_vehiculo: int) -> Vehiculo | None:
        return self.db.query(Vehiculo).filter(Vehiculo.id_vehiculo == id_vehiculo).first()

    def get_by_usuario(self, id_usuario: int) -> list[Vehiculo]:
        return (
            self.db.query(Vehiculo)
            .filter(Vehiculo.id_usuario == id_usuario)
            .order_by(Vehiculo.id_vehiculo)
            .all()
        )

    def get_by_placa(self, placa: str) -> Vehiculo | None:
        return self.db.query(Vehiculo).filter(Vehiculo.placa == placa).first()

    def create(self, placa: str, tipo: str, id_usuario: int) -> Vehiculo:
        vehiculo = Vehiculo(placa=placa, tipo=tipo, id_usuario=id_usuario)
        self.db.add(vehiculo)
        self.db.commit()
        self.db.refresh(vehiculo)
        return vehiculo

    def update(self, vehiculo: Vehiculo, placa: str | None, tipo: str | None, id_usuario: int | None) -> Vehiculo:
        if placa is not None:
            vehiculo.placa = placa
        if tipo is not None:
            vehiculo.tipo = tipo
        if id_usuario is not None:
            vehiculo.id_usuario = id_usuario
        self.db.commit()
        self.db.refresh(vehiculo)
        return vehiculo

    def delete(self, vehiculo: Vehiculo) -> None:
        self.db.delete(vehiculo)
        self.db.commit()
