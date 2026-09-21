
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.alerta import AlertaCreate, AlertaResponse, AlertaUpdate, AlertaListResponse
from app.services.alerta_service import AlertaService
from app.core.security import get_current_user
from typing import Optional

router = APIRouter(prefix="/api/v1/alertas", tags=["alertas"])


@router.post("", response_model=AlertaResponse, status_code=201)
async def crear_alerta(
    tipo: str = Form(...),
    mensaje: str = Form(...),
    ubicacion: Optional[str] = Form(None),
    media_type: Optional[str] = Form(None),
    media_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Crea una nueva alerta de seguridad.
    Permite adjuntar foto o video opcionalmente.
    """
    alerta_data = AlertaCreate(
        tipo=tipo,
        mensaje=mensaje,
        ubicacion=ubicacion,
        media_type=media_type
    )
    
    service = AlertaService(db)
    return await service.create_alerta(
        id_usuario=current_user["id"],
        alerta_data=alerta_data,
        media_file=media_file
    )


@router.get("/mis-alertas", response_model=list[AlertaResponse])
def obtener_mis_alertas(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obtiene todas las alertas del usuario actual."""
    service = AlertaService(db)
    return service.get_alertas_usuario(current_user["id"])


@router.get("", response_model=AlertaListResponse)
def listar_alertas(
    estado: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Lista todas las alertas del sistema (solo admin).
    Opcionalmente filtra por estado: pendiente, revisada, resuelta
    """
    # Solo admins pueden ver todas las alertas
    if current_user["rol"] not in ["SuperAdmin", "Administrativo"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver todas las alertas"
        )
    
    service = AlertaService(db)
    return service.get_all_alertas(estado)


@router.get("/{id_alerta}", response_model=AlertaResponse)
def obtener_alerta(
    id_alerta: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Obtiene una alerta específica por ID."""
    service = AlertaService(db)
    alerta = service.get_alerta(id_alerta)
    
    # Verificar permisos: admin o dueño de la alerta
    if current_user["rol"] not in ["SuperAdmin", "Administrativo"]:
        if alerta.id_usuario != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para ver esta alerta"
            )
    
    return alerta


@router.patch("/{id_alerta}/estado", response_model=AlertaResponse)
def actualizar_estado_alerta(
    id_alerta: int,
    alerta_update: AlertaUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Actualiza el estado de una alerta (solo admin)."""
    if current_user["rol"] not in ["SuperAdmin", "Administrativo"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar alertas"
        )
    
    service = AlertaService(db)
    return service.update_estado(id_alerta, alerta_update, current_user["id"])
