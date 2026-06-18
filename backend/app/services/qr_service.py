"""
services/qr_service.py
----------------------
Lógica de negocio para la generación y validación de QR de parqueadero.

Flujo completo:
  1. El estudiante solicita un QR → se busca el primer espacio libre en la BD
     y se genera un payload firmado con su id_usuario, id del espacio y timestamp.
  2. El QR se convierte en imagen PNG (base64) para mostrar en el frontend.
  3. Al escanear el QR (entrada física) → se valida la firma HMAC, se verifica
     que el token no haya expirado, se crea un registro en `accesos` y se marca
     el espacio como ocupado en `espacios_parqueo`.
"""

import qrcode
import base64
import io
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.parking import EspacioParqueo
from app.models.acceso import Acceso
from app.models.vehiculo import Vehiculo
from app.schemas.qr import QRGenerarRequest, QRGeneradoResponse, QREscanearRequest, QREscanearResponse
from app.utils.qr_utils import sign_qr_payload, decode_qr_payload, verify_qr_signature

# Tiempo de validez del QR en minutos.
# Si el estudiante no usa el QR en este tiempo, expira y debe solicitar uno nuevo.
QR_EXPIRE_MINUTES = 10


class QRService:
    def __init__(self, db: Session):
        self.db = db

    # ─────────────────────────────────────────────────────────────────────────
    # GENERAR QR
    # ─────────────────────────────────────────────────────────────────────────

    def generar_qr(self, data: QRGenerarRequest) -> QRGeneradoResponse:
        """
        Busca el primer espacio libre del tipo adecuado y genera un QR firmado.
        No reserva el espacio todavía — eso ocurre cuando se escanea el QR.
        """
        # 1. Verificar que el usuario existe
        from app.models.user import Usuario
        usuario = self.db.query(Usuario).filter(
            Usuario.id_usuario == data.id_usuario
        ).first()
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con id {data.id_usuario} no encontrado"
            )

        # 2. Si se proporciona vehículo, obtener su tipo para filtrar espacio compatible
        tipo_vehiculo: str | None = None
        if data.id_vehiculo is not None:
            vehiculo = self.db.query(Vehiculo).filter(
                Vehiculo.id_vehiculo == data.id_vehiculo
            ).first()
            if not vehiculo:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Vehículo con id {data.id_vehiculo} no encontrado"
                )
            tipo_vehiculo = vehiculo.tipo  # "carro", "moto", "bicicleta", "vip"

        # 3. Buscar el primer espacio libre
        query = self.db.query(EspacioParqueo).filter(EspacioParqueo.status == "libre")
        if tipo_vehiculo:
            # Intentar coincidir con el tipo exacto; si no hay, devolver cualquier espacio libre
            espacio = query.filter(EspacioParqueo.tipo == tipo_vehiculo).first()
            if not espacio:
                espacio = query.first()  # fallback a cualquier espacio libre
        else:
            espacio = query.first()

        if not espacio:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No hay espacios disponibles en el parqueadero en este momento"
            )

        # 4. Construir payload del QR
        now_utc = datetime.now(timezone.utc)
        expira_en = now_utc + timedelta(minutes=QR_EXPIRE_MINUTES)

        payload = {
            "espacio_id": espacio.id,
            "slot_id": espacio.slot_id,
            "id_usuario": data.id_usuario,
            "id_vehiculo": data.id_vehiculo,
            "emitido_en": now_utc.isoformat(),
            "expira_en": expira_en.isoformat(),
        }

        # 5. Firmar y codificar
        qr_token = sign_qr_payload(payload)

        # 6. Generar imagen QR en PNG → base64
        qr_image_base64 = self._generar_imagen_qr(qr_token)

        return QRGeneradoResponse(
            espacio_id=espacio.id,
            slot_id=espacio.slot_id,
            label=espacio.label,
            tipo=espacio.tipo,
            qr_token=qr_token,
            qr_image_base64=qr_image_base64,
            expira_en=expira_en,
            mensaje=(
                f"QR generado para el espacio {espacio.label}. "
                f"Escanéalo en la entrada. Válido por {QR_EXPIRE_MINUTES} minutos."
            ),
        )

    # ─────────────────────────────────────────────────────────────────────────
    # ESCANEAR / VALIDAR QR → CREAR ACCESO
    # ─────────────────────────────────────────────────────────────────────────

    def escanear_qr(self, data: QREscanearRequest) -> QREscanearResponse:
        """
        Valida la firma del QR, verifica expiración y:
          - Marca el espacio como 'ocupado'
          - Crea un registro en la tabla accesos
        """
        # 1. Decodificar payload
        try:
            payload = decode_qr_payload(data.qr_token)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc)
            )

        # 2. Verificar firma HMAC
        if not verify_qr_signature(payload):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="QR inválido o manipulado — la firma no coincide"
            )

        # 3. Verificar expiración
        expira_en_str = payload.get("expira_en")
        if expira_en_str:
            expira_en = datetime.fromisoformat(expira_en_str)
            # Normalizar timezone: si no tiene tzinfo, asumir UTC
            if expira_en.tzinfo is None:
                expira_en = expira_en.replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) > expira_en:
                raise HTTPException(
                    status_code=status.HTTP_410_GONE,
                    detail="El QR ha expirado. Solicita uno nuevo."
                )

        # 4. Obtener espacio y verificar que sigue libre
        espacio_id = payload.get("espacio_id")
        espacio = self.db.query(EspacioParqueo).filter(
            EspacioParqueo.id == espacio_id
        ).first()

        if not espacio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El espacio con id {espacio_id} no existe"
            )

        if espacio.status != "libre":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"El espacio {espacio.label} ya está ocupado. "
                    "Solicita un nuevo QR para otro espacio disponible."
                )
            )

        # 5. Marcar espacio como ocupado
        espacio.status = "ocupado"
        espacio.updated_at = datetime.now(timezone.utc)

        # 6. Crear registro de acceso
        id_usuario = payload.get("id_usuario")
        id_vehiculo = payload.get("id_vehiculo")
        hora_entrada = datetime.now(timezone.utc).replace(tzinfo=None)  # naive UTC para consistencia con el resto

        acceso = Acceso(
            id_usuario=id_usuario,
            id_vehiculo=id_vehiculo,
            id_espacio=espacio.id,
            hora_entrada=hora_entrada,
            metodo="qr",
        )
        self.db.add(acceso)
        self.db.commit()
        self.db.refresh(acceso)
        self.db.refresh(espacio)

        return QREscanearResponse(
            acceso_id=acceso.id_acceso,
            id_usuario=id_usuario,
            id_vehiculo=id_vehiculo,
            espacio_id=espacio.id,
            slot_id=espacio.slot_id,
            label=espacio.label,
            hora_entrada=acceso.hora_entrada,
            mensaje=f"✅ Acceso registrado. Espacio {espacio.label} asignado correctamente.",
        )

    # ─────────────────────────────────────────────────────────────────────────
    # HELPER PRIVADO
    # ─────────────────────────────────────────────────────────────────────────

    def _generar_imagen_qr(self, qr_token: str) -> str:
        """Genera la imagen PNG del QR y la devuelve como string base64 embebible."""
        qr = qrcode.QRCode(
            version=None,       # auto-tamaño
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_token)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        b64 = base64.b64encode(buf.getvalue()).decode()
        buf.close()

        return f"data:image/png;base64,{b64}"
