from sqlalchemy.orm import Session
from app.repositories import ParkingRepository
from app.schemas import ParkingEstadoResponse, EspacioParqueoResponse
from app.mqtt_client import parking_state, SLOTS_DEFINICION


class ParkingService:
    def __init__(self, db: Session):
        self.db = db
        self.parking_repo = ParkingRepository(db)

    def get_parking_slots(self) -> ParkingEstadoResponse:
        """
        Combina los espacios de la BD con el estado en memoria (parking_state).
        La fuente de verdad del estado de ocupación es la BD (actualizada por QR);
        parking_state se usa sólo para el broadcast WebSocket del mapa.
        """
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
                    updated_at=estado_live.get("updated_at"),
                    qr_identifier=None,
                ))
        else:
            for espacio in espacios_db:
                estado_live = parking_state["espacios"].get(espacio.slot_id, {})
                resultado.append(EspacioParqueoResponse(
                    id=espacio.id,
                    slot_id=espacio.slot_id,
                    label=espacio.label,
                    tipo=espacio.tipo,
                    # La BD es la fuente de verdad; el estado en memoria es fallback de red
                    status=estado_live.get("status", espacio.status),
                    updated_at=estado_live.get("updated_at") or espacio.updated_at,
                    qr_identifier=espacio.qr_identifier,
                ))

        total_libre = sum(1 for e in resultado if e.status == "libre")
        total_ocupado = len(resultado) - total_libre

        return ParkingEstadoResponse(
            espacios=resultado,
            total_libre=total_libre,
            total_ocupado=total_ocupado,
            total_espacios=len(resultado),
        )
