
from sqlalchemy.orm import Session
from app.repositories import ParkingRepository
from app.schemas import ParkingEstadoResponse, EspacioParqueoResponse
from app.mqtt_client import parking_state, SLOTS_DEFINICION


class ParkingService:
    def __init__(self, db: Session):
        self.db = db
        self.parking_repo = ParkingRepository(db)

    def get_parking_slots(self) -> ParkingEstadoResponse:
        espacios_db = self.parking_repo.get_all()
        resultado = []

        if not espacios_db:
            for i, s in enumerate(SLOTS_DEFINICION, start=1):
                estado_live = parking_state["espacios"].get(s["slot_id"], {})
                resultado.append(EspacioParqueoResponse(
                    id=i,
                    slot_id=s["slot_id"],
                    label=s["label"],
                    tipo=s["tipo"],
                    status=estado_live.get("status", "libre"),
                    distancia_cm=estado_live.get("distancia_cm"),
                    updated_at=estado_live.get("updated_at"),
                ))
        else:
            for espacio in espacios_db:
                estado_live = parking_state["espacios"].get(espacio.slot_id, {})
                resultado.append(EspacioParqueoResponse(
                    id=espacio.id,
                    slot_id=espacio.slot_id,
                    label=espacio.label,
                    tipo=espacio.tipo,
                    status=estado_live.get("status", espacio.status),
                    distancia_cm=estado_live.get("distancia_cm", espacio.distancia_cm),
                    updated_at=estado_live.get("updated_at", espacio.updated_at),
                ))

        total_libre = sum(1 for e in resultado if e.status == "libre")
        total_ocupado = len(resultado) - total_libre

        return ParkingEstadoResponse(
            espacios=resultado,
            total_libre=total_libre,
            total_ocupado=total_ocupado,
            total_espacios=len(resultado)
        )

