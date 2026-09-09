"""remove sensor fields from espacios_parqueo

Revision ID: 20260908_1100
Revises: 20260908_1000
Create Date: 2026-09-08 11:00:00.000000

Motivo:
  La detección de ocupación ya no depende de sensores físicos (HC-SR04, IR FC-51).
  El estado de cada celda se gestiona exclusivamente por el flujo QR:
    - POST /api/v1/parking/occupy-spot   → marca OCUPADO
    - POST /api/v1/accesos/{id}/salida   → marca LIBRE

  Se elimina la columna `distancia_cm` de `espacios_parqueo`, que almacenaba
  la lectura del sensor ultrasónico y ya no tiene uso.
"""

from alembic import op
import sqlalchemy as sa

revision = "20260908_1100"
down_revision = "20260908_1000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Eliminar columna distancia_cm de espacios_parqueo
    op.drop_column("espacios_parqueo", "distancia_cm")


def downgrade() -> None:
    # Restaurar columna distancia_cm (nullable, sin datos históricos)
    op.add_column(
        "espacios_parqueo",
        sa.Column("distancia_cm", sa.Float(), nullable=True),
    )
