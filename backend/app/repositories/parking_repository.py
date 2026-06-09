
from sqlalchemy.orm import Session
from app.models import EspacioParqueo


class ParkingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[EspacioParqueo]:
        return self.db.query(EspacioParqueo).order_by(EspacioParqueo.id).all()

    def get_by_slot_id(self, slot_id: str) -> EspacioParqueo | None:
        return self.db.query(EspacioParqueo).filter(EspacioParqueo.slot_id == slot_id).first()

    def create(self, slot_id: str, label: str, tipo: str, status: str = "libre") -> EspacioParqueo:
        espacio = EspacioParqueo(slot_id=slot_id, label=label, tipo=tipo, status=status)
        self.db.add(espacio)
        self.db.commit()
        self.db.refresh(espacio)
        return espacio

