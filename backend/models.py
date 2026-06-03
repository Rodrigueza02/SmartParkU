from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
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
    password = Column(String(100), nullable=False)  # Almacenado como Hash Bcrypt

    # El rol determina la experiencia UI/UX en el Frontend sostenible
    # Valores: 'SuperAdmin', 'Estudiante', 'Administrativo', 'Visitante'
    rol = Column(String(50), nullable=False)

    # Estado del usuario (ej. 'Activo', 'Inactivo')
    estado = Column(String(50), default="Activo")


class EspacioParqueo(Base):
    """
    Modelo ORM que mapea la tabla 'espacios_parqueo' de SmartParkU.
    Define los 10 espacios físicos fijos del parqueadero UCC Pasto.

    Cada espacio tiene un slot_id canónico que coincide con el campo
    'slot' publicado por los sensores MQTT desde la Raspberry Pi.
    """
    __tablename__ = "espacios_parqueo"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # ID canónico del espacio — coincide con el slot_id de MQTT
    # Ejemplos: "slot_01", "slot_02", ..., "slot_10"
    slot_id = Column(String(20), unique=True, index=True, nullable=False)

    # Etiqueta visual para el Frontend (ej. "C-01", "M-01", "V-01")
    label = Column(String(20), nullable=False)

    # Tipo de vehículo permitido: 'carro', 'moto', 'bicicleta', 'vip'
    tipo = Column(String(20), nullable=False)

    # Estado en tiempo real — actualizado por MQTT: 'libre' | 'ocupado'
    status = Column(String(20), default="libre", nullable=False)

    # Última distancia registrada por el sensor HC-SR04 (cm)
    distancia_cm = Column(Float, nullable=True)

    # Timestamp de la última actualización del sensor
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
