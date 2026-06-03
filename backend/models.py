from sqlalchemy import Column, Integer, String
from database import Base

class Usuario(Base):
    """
    Modelo ORM que mapea la tabla 'usuarios' de SmartParkU.
    Representa la identidad de los miembros de la UCC.
    """
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(100), nullable=False) # Almacenado como Hash Bcrypt
    
    # El rol determina la experiencia UI/UX en el Frontend sostenible
    # Valores: 'SuperAdmin', 'Estudiante', 'Administrativo', 'Visitante'
    rol = Column(String(50), nullable=False)
    
    # Estado del usuario (ej. 'Activo', 'Inactivo')
    estado = Column(String(50), default="Activo")
