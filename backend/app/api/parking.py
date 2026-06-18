
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
import json
import asyncio
from app.db import get_db
from app.schemas import ParkingEstadoResponse
from app.services import ParkingService
from app.mqtt_client import parking_state, publish_servo, add_ws_listener, remove_ws_listener
from app.core.security import get_current_user, require_roles

router = APIRouter(prefix="/api/v1/parking", tags=["parking"])

_any_auth   = Depends(get_current_user)
_admin_only = Depends(require_roles("SuperAdmin", "Administrativo"))


@router.get("/estado", dependencies=[_any_auth])
def get_parking_estado():
    """Estado en tiempo real del parqueadero (desde memoria MQTT)."""
    return parking_state


@router.get("/slots", response_model=ParkingEstadoResponse, dependencies=[_any_auth])
def get_parking_slots(db: Session = Depends(get_db)):
    parking_service = ParkingService(db)
    return parking_service.get_parking_slots()


@router.post("/servo", dependencies=[_admin_only])
def control_servo(accion: str = "abrir"):
    """Solo administradores pueden controlar la talanquera."""
    if accion not in ("abrir", "cerrar"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="accion debe ser 'abrir' o 'cerrar'"
        )
    angulo = 90 if accion == "abrir" else 0
    try:
        publish_servo(angulo, accion)
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    return {"ok": True, "accion": accion, "angulo": angulo}


@router.websocket("/ws/parking")
async def websocket_parking(websocket: WebSocket):
    """
    WebSocket público — el frontend necesita conectarse antes del login
    para mostrar disponibilidad. La autenticación se hace a nivel HTTP.
    """
    await websocket.accept()
    queue: asyncio.Queue = asyncio.Queue(maxsize=20)
    add_ws_listener(queue)
    await websocket.send_text(json.dumps(parking_state, default=str))
    try:
        while True:
            try:
                message = await asyncio.wait_for(queue.get(), timeout=30.0)
                await websocket.send_text(message)
            except asyncio.TimeoutError:
                await websocket.send_text(json.dumps({"ping": True}))
    except WebSocketDisconnect:
        pass
    finally:
        remove_ws_listener(queue)

