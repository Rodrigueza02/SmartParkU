"""
services/ingreso_service.py
----------------------------
Lógica de negocio del módulo de control de acceso trimodal.

Flujo de dos etapas:
  ETAPA 1 — Portería (cualquiera de 3 métodos)
    → Identifica usuario/vehículo
    → Crea un Acceso con hora_entrada y metodo; id_espacio queda NULL
    → Abre la talanquera vía MQTT
    → Devuelve IngresoResponse

  ETAPA 2 — Celda (QR único del puesto físico)
    → Valida que exista sesión abierta (sin hora_salida ni puesto confirmado)
    → Verifica que el puesto scaneado esté LIBRE
    → Asigna id_espacio al Acceso + registra puesto_confirmado_en
    → Cambia status del espacio a 'ocupado' en BD y en tiempo real (WS)
    → Devuelve OcuparPuestoResponse

Timeout de sesión inconclusa:
  Si el usuario ingresó por portería pero no confirmó el puesto en
  INGRESO_TIMEOUT_MINUTES minutos, la sesión se considera inconclusa y
  se deniega una nueva entrada hasta que la anterior sea anulada o venza.
  (La anulación automática se hace en el chequeo de sesión activa.)
"""

import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories.ingreso_repository import IngresoRepository
from app.schemas.ingreso import (
    IngresoRFIDRequest,
    IngresoCarnetRequest,
    IngresoQREntradaRequest,
    OcuparPuestoRequest,
    IngresoResponse,
    OcuparPuestoResponse,
)

logger = logging.getLogger("smartparku.ingreso")

# Tiempo máximo (minutos) entre ingreso por portería y confirmación de celda.
# Las sesiones más antiguas se marcan como inconclusas y se permiten nuevas entradas.
INGRESO_TIMEOUT_MINUTES = 30


class IngresoService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = IngresoRepository(db)

    # ═════════════════════════════════════════════════════════════════════════
    # ETAPA 1 — Métodos de ingreso por portería
    # ═════════════════════════════════════════════════════════════════════════

    def ingreso_rfid(self, data: IngresoRFIDRequest) -> IngresoResponse:
        """
        Entrada vía lector RFID.
        Identifica el vehículo por su rfid_tag_id y obtiene el usuario asociado.
        """
        vehiculo = self.repo.get_vehiculo_by_rfid(data.rfid_tag_id)
        if not vehiculo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró un vehículo con el tag RFID '{data.rfid_tag_id}'. "
                       "Registra el vehículo antes de ingresar.",
            )

        if vehiculo.id_usuario is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"El vehículo con tag '{data.rfid_tag_id}' no tiene usuario asociado.",
            )

        usuario = self.repo.get_usuario_by_id(vehiculo.id_usuario)
        if not usuario or usuario.estado != "Activo":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El usuario asociado al vehículo está inactivo o no existe.",
            )

        self._verificar_sin_sesion_activa(vehiculo.id_usuario, por_vehiculo=vehiculo.id_vehiculo)

        acceso = self._crear_acceso_porteria(
            id_usuario=vehiculo.id_usuario,
            id_vehiculo=vehiculo.id_vehiculo,
            metodo="RFID",
        )

        self._abrir_talanquera()
        logger.info(f"Ingreso RFID: vehículo {vehiculo.placa}, usuario {usuario.nombre}")

        return IngresoResponse(
            acceso_id=acceso.id_acceso,
            id_usuario=vehiculo.id_usuario,
            id_vehiculo=vehiculo.id_vehiculo,
            metodo="RFID",
            hora_entrada=acceso.hora_entrada,
            talanquera_abierta=True,
            mensaje=f"✅ Bienvenido, {usuario.nombre}. Talanquera abierta. "
                    "Escanea el QR de tu puesto para confirmar la ocupación.",
        )

    def ingreso_carnet(self, data: IngresoCarnetRequest) -> IngresoResponse:
        """
        Entrada vía carnet institucional.
        Identifica al usuario por su carnet_id y obtiene su primer vehículo registrado.
        """
        usuario = self.repo.get_usuario_by_carnet(data.carnet_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró un usuario con el carnet '{data.carnet_id}'. "
                       "Registra tu carnet en el sistema.",
            )

        if usuario.estado != "Activo":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tu cuenta está inactiva. Contacta al administrador.",
            )

        vehiculo = self.repo.get_vehiculo_by_usuario(usuario.id_usuario)
        # No se bloquea si el usuario no tiene vehículo registrado (puede ser peatón)

        self._verificar_sin_sesion_activa(usuario.id_usuario)

        acceso = self._crear_acceso_porteria(
            id_usuario=usuario.id_usuario,
            id_vehiculo=vehiculo.id_vehiculo if vehiculo else None,
            metodo="CARNET",
        )

        self._abrir_talanquera()
        logger.info(f"Ingreso CARNET: usuario {usuario.nombre} (carnet {data.carnet_id})")

        return IngresoResponse(
            acceso_id=acceso.id_acceso,
            id_usuario=usuario.id_usuario,
            id_vehiculo=vehiculo.id_vehiculo if vehiculo else None,
            metodo="CARNET",
            hora_entrada=acceso.hora_entrada,
            talanquera_abierta=True,
            mensaje=f"✅ Bienvenido, {usuario.nombre}. Talanquera abierta. "
                    "Escanea el QR de tu puesto para confirmar la ocupación.",
        )

    def ingreso_qr_entrada(
        self,
        current_user: dict,  # {"correo": ..., "rol": ..., "id_usuario": ...}
    ) -> IngresoResponse:
        """
        Entrada vía QR general de portería.
        El usuario escanea el QR físico de la entrada desde la app (ya autenticado con JWT).
        """
        id_usuario: int = current_user["id_usuario"]

        usuario = self.repo.get_usuario_by_id(id_usuario)
        if not usuario or usuario.estado != "Activo":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Tu cuenta está inactiva o no existe.",
            )

        vehiculo = self.repo.get_vehiculo_by_usuario(id_usuario)

        self._verificar_sin_sesion_activa(id_usuario)

        acceso = self._crear_acceso_porteria(
            id_usuario=id_usuario,
            id_vehiculo=vehiculo.id_vehiculo if vehiculo else None,
            metodo="QR_ENTRADA",
        )

        self._abrir_talanquera()
        logger.info(f"Ingreso QR_ENTRADA: usuario {usuario.nombre} (id {id_usuario})")

        return IngresoResponse(
            acceso_id=acceso.id_acceso,
            id_usuario=id_usuario,
            id_vehiculo=vehiculo.id_vehiculo if vehiculo else None,
            metodo="QR_ENTRADA",
            hora_entrada=acceso.hora_entrada,
            talanquera_abierta=True,
            mensaje=f"✅ Bienvenido, {usuario.nombre}. Talanquera abierta. "
                    "Escanea el QR de tu puesto para confirmar la ocupación.",
        )

    # ═════════════════════════════════════════════════════════════════════════
    # ETAPA 2 — Confirmación de celda
    # ═════════════════════════════════════════════════════════════════════════

    def ocupar_puesto(self, data: OcuparPuestoRequest) -> OcuparPuestoResponse:
        """
        El usuario escanea el QR físico del puesto de estacionamiento.

        Validaciones:
          1. El puesto (qr_identifier) debe existir en la BD.
          2. El puesto debe estar en estado 'libre'.
          3. Debe existir una sesión de ingreso abierta (sin hora_salida)
             para el usuario que no haya superado el timeout.
          4. La sesión no debe tener ya un puesto confirmado asignado.
        """
        ahora = datetime.now(timezone.utc).replace(tzinfo=None)

        # 1. Verificar que el puesto existe
        espacio = self.repo.get_espacio_by_qr_identifier(data.qr_identifier)
        if not espacio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El código QR '{data.qr_identifier}' no corresponde a ningún puesto registrado.",
            )

        # 2. Verificar que el puesto está disponible
        if espacio.status == "mantenimiento":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El puesto {espacio.label} está en mantenimiento. Elige otro puesto.",
            )
        if espacio.status != "libre":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El puesto {espacio.label} ya está ocupado. "
                       "Por favor intenta en otro puesto disponible.",
            )

        # 3. Localizar sesión activa del usuario
        if data.id_usuario is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Debes incluir tu id_usuario para confirmar la ocupación del puesto.",
            )

        sesion = self.repo.get_sesion_activa_by_usuario(data.id_usuario)

        if sesion is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se encontró una sesión de ingreso activa para este usuario. "
                       "Ingresa primero por la portería.",
            )

        # 4. Verificar timeout de sesión inconclusa
        if sesion.hora_entrada:
            hora_entrada = sesion.hora_entrada
            # Normalizar si tiene tzinfo
            if hasattr(hora_entrada, 'tzinfo') and hora_entrada.tzinfo is not None:
                hora_entrada = hora_entrada.replace(tzinfo=None)
            edad_sesion = ahora - hora_entrada
            if edad_sesion > timedelta(minutes=INGRESO_TIMEOUT_MINUTES):
                raise HTTPException(
                    status_code=status.HTTP_408_REQUEST_TIMEOUT,
                    detail=(
                        f"Tu sesión de ingreso expiró (límite: {INGRESO_TIMEOUT_MINUTES} min). "
                        "Vuelve a ingresar por la portería para iniciar una nueva sesión."
                    ),
                )

        # 5. Verificar que la sesión aún no tiene puesto asignado
        if sesion.id_espacio is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya tienes un puesto confirmado en tu sesión actual. "
                       "Finaliza tu sesión antes de confirmar otro puesto.",
            )

        # 6. Asignar el puesto al acceso y marcarlo como ocupado
        self.repo.ocupar_espacio(espacio, ahora)
        sesion = self.repo.asignar_puesto(sesion, espacio, ahora)

        # 7. Propagar cambio al mapa en tiempo real (WebSocket)
        try:
            from app.mqtt_client import update_slot_status
            update_slot_status(espacio.slot_id, "ocupado")
        except Exception as exc:
            logger.warning(f"No se pudo actualizar el mapa WS: {exc}")

        logger.info(
            f"Puesto confirmado: {espacio.label} → usuario {data.id_usuario}, "
            f"acceso {sesion.id_acceso}"
        )

        return OcuparPuestoResponse(
            acceso_id=sesion.id_acceso,
            id_usuario=sesion.id_usuario,
            id_vehiculo=sesion.id_vehiculo,
            espacio_id=espacio.id,
            slot_id=espacio.slot_id,
            label=espacio.label,
            tipo=espacio.tipo,
            puesto_confirmado_en=ahora,
            mensaje=f"✅ Puesto {espacio.label} confirmado correctamente.",
        )

    # ═════════════════════════════════════════════════════════════════════════
    # Helpers privados
    # ═════════════════════════════════════════════════════════════════════════

    def _verificar_sin_sesion_activa(
        self,
        id_usuario: int,
        por_vehiculo: int | None = None,
    ) -> None:
        """
        Verifica que el usuario/vehículo no tenga una sesión de ingreso abierta.
        Si la sesión encontrada ya superó el timeout, la ignora (sesión inconclusa).
        Lanza 409 si hay una sesión vigente dentro del periodo de timeout.
        """
        sesion = self.repo.get_sesion_activa_by_usuario(id_usuario)

        if sesion is None and por_vehiculo is not None:
            sesion = self.repo.get_sesion_activa_by_vehiculo(por_vehiculo)

        if sesion is None:
            return  # Sin sesión activa → puede ingresar

        # Revisar si la sesión ya expiró por timeout
        if sesion.hora_entrada:
            ahora = datetime.now(timezone.utc).replace(tzinfo=None)
            hora_entrada = sesion.hora_entrada
            if hasattr(hora_entrada, 'tzinfo') and hora_entrada.tzinfo is not None:
                hora_entrada = hora_entrada.replace(tzinfo=None)
            edad = ahora - hora_entrada
            if edad > timedelta(minutes=INGRESO_TIMEOUT_MINUTES):
                # Sesión expirada — no bloquear nuevo ingreso
                logger.info(
                    f"Sesión {sesion.id_acceso} del usuario {id_usuario} expiró por timeout. "
                    "Se permite nueva entrada."
                )
                return

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Ya tienes una sesión de ingreso activa (acceso #{sesion.id_acceso}). "
                "Finaliza tu sesión actual antes de ingresar de nuevo."
            ),
        )

    def _crear_acceso_porteria(
        self,
        id_usuario: int | None,
        id_vehiculo: int | None,
        metodo: str,
    ):
        """Crea el registro de ingreso por portería con hora actual UTC."""
        hora_entrada = datetime.now(timezone.utc).replace(tzinfo=None)
        return self.repo.crear_acceso_porteria(
            id_usuario=id_usuario,
            id_vehiculo=id_vehiculo,
            metodo=metodo,
            hora_entrada=hora_entrada,
        )

    def _abrir_talanquera(self) -> None:
        """Publica comando de apertura en el topic MQTT de la talanquera."""
        try:
            from app.mqtt_client import publish_servo
            publish_servo(90, "abrir")
        except Exception as exc:
            # No bloquear el flujo si el servo no está disponible
            logger.warning(f"No se pudo abrir la talanquera vía MQTT: {exc}")
