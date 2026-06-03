from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import asyncio
import json
import models, schemas, auth, database
from database import engine, get_db
import mqtt_client
from mqtt_client import parking_state, publish_servo, add_ws_listener, remove_ws_listener, stop_mqtt, SLOTS_DEFINICION

# Crear las tablas en la base de datos
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SmartParkU - Backend",
    description="API de autenticación, sensores IoT y control de acceso para SmartParkU UCC",
    version="2.0.0"
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Eventos de ciclo de vida ──────────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    """Inicia el cliente MQTT al arrancar el servidor."""
    await mqtt_client.start_mqtt()


@app.on_event("shutdown")
async def shutdown_event():
    """Detiene el cliente MQTT al apagar el servidor."""
    stop_mqtt()


# ─── Auth (RF01) ───────────────────────────────────────────────────────────────
@app.post("/api/v1/auth/login", response_model=schemas.TokenResponse)
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    """
    Endpoint RF01: Autenticación de Usuarios.
    Verifica credenciales y retorna un JWT junto con los metadatos del perfil.
    """
    user = db.query(models.Usuario).filter(models.Usuario.correo == request.correo).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not auth.verify_password(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.estado.lower() != "activo":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta se encuentra inactiva. Contacte al administrador de la UCC."
        )

    access_token = auth.create_access_token(
        data={"sub": user.correo, "rol": user.rol}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "nombre": user.nombre,
        "rol": user.rol,
        "estado": user.estado,
    }


# ─── Parking / IoT REST ────────────────────────────────────────────────────────

@app.get("/api/v1/parking/estado", summary="Estado actual del parqueadero")
def get_parking_estado():
    """
    Retorna el estado en tiempo real de todos los espacios del parqueadero.
    Los datos son actualizados automáticamente via MQTT desde los sensores.
    """
    return parking_state


@app.get("/api/v1/parking/slots", response_model=schemas.ParkingEstadoResponse, summary="Definición y estado de los 10 espacios")
def get_parking_slots(db: Session = Depends(get_db)):
    """
    Retorna los 10 espacios fijos del parqueadero UCC Pasto con su estado actual.

    Combina la definición persistente de la DB con el estado en tiempo real
    del parking_state en memoria (actualizado por MQTT).
    Útil para que el Frontend inicialice el mapa con layout fijo.
    """
    espacios_db = db.query(models.EspacioParqueo).order_by(models.EspacioParqueo.id).all()

    # Si la DB no tiene datos todavía, usar la definición canónica en memoria
    if not espacios_db:
        from datetime import datetime
        resultado = []
        for i, s in enumerate(SLOTS_DEFINICION, start=1):
            estado_live = parking_state["espacios"].get(s["slot_id"], {})
            resultado.append(schemas.EspacioParqueoResponse(
                id=i,
                slot_id=s["slot_id"],
                label=s["label"],
                tipo=s["tipo"],
                status=estado_live.get("status", "libre"),
                distancia_cm=estado_live.get("distancia_cm"),
                updated_at=estado_live.get("updated_at"),
            ))
    else:
        resultado = []
        for espacio in espacios_db:
            # Combinar con estado en tiempo real del MQTT
            estado_live = parking_state["espacios"].get(espacio.slot_id, {})
            espacio.status       = estado_live.get("status", espacio.status)
            espacio.distancia_cm = estado_live.get("distancia_cm", espacio.distancia_cm)
            resultado.append(espacio)

    total_libre   = sum(1 for e in resultado if (e.status if isinstance(e, schemas.EspacioParqueoResponse) else e.status) == "libre")
    total_ocupado = len(resultado) - total_libre

    return schemas.ParkingEstadoResponse(
        espacios=resultado,
        total_libre=total_libre,
        total_ocupado=total_ocupado,
        total_espacios=len(resultado),
    )


@app.post("/api/v1/parking/servo", summary="Controla la barrera de acceso")
def control_servo(accion: str = "abrir"):
    """
    Envia un comando a la talanquera (servo SG90 en Raspberry Pi).
    - accion=abrir  → abre la barrera (90 grados)
    - accion=cerrar → cierra la barrera (0 grados)
    """
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


# ─── WebSocket: actualizaciones en tiempo real al Frontend ───────────────────

@app.websocket("/ws/parking")
async def websocket_parking(websocket: WebSocket):
    """
    Canal WebSocket que hace streaming del estado del parqueadero al Frontend.
    Cada vez que un sensor MQTT publica, el frontend recibe el nuevo estado.

    Arquitectura:
        Raspberry Pi → HiveMQ Cloud → Backend (MQTT) → WebSocket → Frontend
    """
    await websocket.accept()

    queue: asyncio.Queue = asyncio.Queue(maxsize=20)
    add_ws_listener(queue)

    # Enviar estado actual inmediatamente al conectarse
    await websocket.send_text(json.dumps(parking_state, default=str))

    try:
        while True:
            # Esperar nuevo mensaje de la cola (con timeout para hacer ping)
            try:
                message = await asyncio.wait_for(queue.get(), timeout=30.0)
                await websocket.send_text(message)
            except asyncio.TimeoutError:
                # Ping para mantener la conexión viva
                await websocket.send_text(json.dumps({"ping": True}))
    except WebSocketDisconnect:
        pass
    finally:
        remove_ws_listener(queue)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
