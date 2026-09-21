
from sqlalchemy.orm import Session, joinedload
from app.models.alerta import Alerta
from typing import List, Optional


class AlertaRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, alerta_data: dict) -> Alerta:
        """Crea una nueva alerta."""
        alerta = Alerta(**alerta_data)
        self.db.add(alerta)
        self.db.commit()
        self.db.refresh(alerta)
        return alerta
    
    def get_by_id(self, id_alerta: int) -> Optional[Alerta]:
        """Obtiene una alerta por su ID."""
        return self.db.query(Alerta)\
            .options(joinedload(Alerta.usuario), joinedload(Alerta.revisor))\
            .filter(Alerta.id_alerta == id_alerta)\
            .first()
    
    def get_by_usuario(self, id_usuario: int) -> List[Alerta]:
        """Obtiene todas las alertas de un usuario."""
        return self.db.query(Alerta)\
            .options(joinedload(Alerta.usuario), joinedload(Alerta.revisor))\
            .filter(Alerta.id_usuario == id_usuario)\
            .order_by(Alerta.fecha_creacion.desc())\
            .all()
    
    def get_all(self, estado: Optional[str] = None) -> List[Alerta]:
        """Obtiene todas las alertas, opcionalmente filtradas por estado."""
        query = self.db.query(Alerta)\
            .options(joinedload(Alerta.usuario), joinedload(Alerta.revisor))
        
        if estado:
            query = query.filter(Alerta.estado == estado)
        
        return query.order_by(Alerta.fecha_creacion.desc()).all()
    
    def update(self, id_alerta: int, update_data: dict) -> Optional[Alerta]:
        """Actualiza una alerta."""
        alerta = self.get_by_id(id_alerta)
        if not alerta:
            return None
        
        for key, value in update_data.items():
            setattr(alerta, key, value)
        
        self.db.commit()
        self.db.refresh(alerta)
        return alerta
    
    def count_by_estado(self) -> dict:
        """Cuenta alertas por estado."""
        total = self.db.query(Alerta).count()
        pendientes = self.db.query(Alerta).filter(Alerta.estado == "pendiente").count()
        revisadas = self.db.query(Alerta).filter(Alerta.estado == "revisada").count()
        resueltas = self.db.query(Alerta).filter(Alerta.estado == "resuelta").count()
        
        return {
            "total": total,
            "pendientes": pendientes,
            "revisadas": revisadas,
            "resueltas": resueltas
        }
