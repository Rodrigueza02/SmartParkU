
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from app.repositories.alerta_repository import AlertaRepository
from app.schemas.alerta import AlertaCreate, AlertaResponse, AlertaUpdate, AlertaListResponse
from datetime import datetime
from typing import List, Optional
import os
import uuid


class AlertaService:
    def __init__(self, db: Session):
        self.db = db
        self.alerta_repo = AlertaRepository(db)
    
    async def create_alerta(
        self, 
        id_usuario: int, 
        alerta_data: AlertaCreate,
        media_file: Optional[UploadFile] = None
    ) -> AlertaResponse:
        """Crea una nueva alerta, opcionalmente con archivo multimedia."""
        media_url = None
        
        # Si hay archivo multimedia, guardarlo
        if media_file:
            # Crear directorio si no existe
            upload_dir = "backend/data/alertas"
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generar nombre único para el archivo
            file_extension = os.path.splitext(media_file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(upload_dir, unique_filename)
            
            # Guardar archivo
            with open(file_path, "wb") as f:
                content = await media_file.read()
                f.write(content)
            
            media_url = f"/data/alertas/{unique_filename}"
        
        # Crear alerta en BD
        alerta_dict = {
            "id_usuario": id_usuario,
            "tipo": alerta_data.tipo,
            "mensaje": alerta_data.mensaje,
            "ubicacion": alerta_data.ubicacion,
            "media_url": media_url,
            "media_type": alerta_data.media_type,
            "estado": "pendiente"
        }
        
        alerta = self.alerta_repo.create(alerta_dict)
        
        return self._to_response(alerta)
    
    def get_alerta(self, id_alerta: int) -> AlertaResponse:
        """Obtiene una alerta por ID."""
        alerta = self.alerta_repo.get_by_id(id_alerta)
        if not alerta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alerta no encontrada"
            )
        return self._to_response(alerta)
    
    def get_alertas_usuario(self, id_usuario: int) -> List[AlertaResponse]:
        """Obtiene todas las alertas de un usuario."""
        alertas = self.alerta_repo.get_by_usuario(id_usuario)
        return [self._to_response(a) for a in alertas]
    
    def get_all_alertas(self, estado: Optional[str] = None) -> AlertaListResponse:
        """Obtiene todas las alertas con estadísticas."""
        alertas = self.alerta_repo.get_all(estado)
        stats = self.alerta_repo.count_by_estado()
        
        return AlertaListResponse(
            total=stats["total"],
            pendientes=stats["pendientes"],
            revisadas=stats["revisadas"],
            resueltas=stats["resueltas"],
            alertas=[self._to_response(a) for a in alertas]
        )
    
    def update_estado(
        self, 
        id_alerta: int, 
        alerta_update: AlertaUpdate,
        id_revisor: int
    ) -> AlertaResponse:
        """Actualiza el estado de una alerta."""
        alerta = self.alerta_repo.get_by_id(id_alerta)
        if not alerta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alerta no encontrada"
            )
        
        update_data = {
            "estado": alerta_update.estado,
            "fecha_revision": datetime.utcnow(),
            "revisado_por": id_revisor
        }
        
        alerta_actualizada = self.alerta_repo.update(id_alerta, update_data)
        return self._to_response(alerta_actualizada)
    
    def _to_response(self, alerta) -> AlertaResponse:
        """Convierte un modelo Alerta a AlertaResponse."""
        return AlertaResponse(
            id_alerta=alerta.id_alerta,
            id_usuario=alerta.id_usuario,
            tipo=alerta.tipo,
            mensaje=alerta.mensaje,
            ubicacion=alerta.ubicacion,
            estado=alerta.estado,
            media_url=alerta.media_url,
            media_type=alerta.media_type,
            fecha_creacion=alerta.fecha_creacion,
            fecha_revision=alerta.fecha_revision,
            revisado_por=alerta.revisado_por,
            usuario_nombre=alerta.usuario.nombre if alerta.usuario else None,
            revisor_nombre=alerta.revisor.nombre if alerta.revisor else None
        )
