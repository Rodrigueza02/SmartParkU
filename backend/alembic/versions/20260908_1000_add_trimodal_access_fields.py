"""add trimodal access fields

Revision ID: 20260908_1000
Revises: 20260618_1200_create_vehiculos_accesos
Create Date: 2026-09-08 10:00:00.000000

Cambios:
  - usuarios.carnet_id          VARCHAR(100) UNIQUE NULLABLE
  - vehiculos.rfid_tag_id       VARCHAR(100) UNIQUE NULLABLE
  - espacios_parqueo.qr_identifier  VARCHAR(100) UNIQUE NULLABLE
  - accesos.puesto_confirmado_en    TIMESTAMP NULLABLE
"""

from alembic import op
import sqlalchemy as sa

revision = "20260908_1000"
down_revision = "000000000004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── usuarios ─────────────────────────────────────────────────────────────
    op.add_column(
        "usuarios",
        sa.Column("carnet_id", sa.String(100), nullable=True),
    )
    op.create_unique_constraint("uq_usuarios_carnet_id", "usuarios", ["carnet_id"])
    op.create_index("ix_usuarios_carnet_id", "usuarios", ["carnet_id"])

    # ── vehiculos ─────────────────────────────────────────────────────────────
    op.add_column(
        "vehiculos",
        sa.Column("rfid_tag_id", sa.String(100), nullable=True),
    )
    op.create_unique_constraint("uq_vehiculos_rfid_tag_id", "vehiculos", ["rfid_tag_id"])
    op.create_index("ix_vehiculos_rfid_tag_id", "vehiculos", ["rfid_tag_id"])
    # Índice en placa (puede ya existir en la BD — solo crear si no existe)
    # Nota: op.create_index no soporta if_not_exists en todas las versiones de Alembic;
    # se usa un bloque try/except para hacerlo idempotente.
    try:
        op.create_index("ix_vehiculos_placa", "vehiculos", ["placa"], unique=False)
    except Exception:
        pass  # El índice ya existe en esta BD

    # ── espacios_parqueo ──────────────────────────────────────────────────────
    op.add_column(
        "espacios_parqueo",
        sa.Column("qr_identifier", sa.String(100), nullable=True),
    )
    op.create_unique_constraint(
        "uq_espacios_parqueo_qr_identifier", "espacios_parqueo", ["qr_identifier"]
    )
    op.create_index(
        "ix_espacios_parqueo_qr_identifier", "espacios_parqueo", ["qr_identifier"]
    )

    # ── accesos ───────────────────────────────────────────────────────────────
    op.add_column(
        "accesos",
        sa.Column("puesto_confirmado_en", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    # ── accesos ───────────────────────────────────────────────────────────────
    op.drop_column("accesos", "puesto_confirmado_en")

    # ── espacios_parqueo ──────────────────────────────────────────────────────
    op.drop_index("ix_espacios_parqueo_qr_identifier", table_name="espacios_parqueo")
    op.drop_constraint(
        "uq_espacios_parqueo_qr_identifier", "espacios_parqueo", type_="unique"
    )
    op.drop_column("espacios_parqueo", "qr_identifier")

    # ── vehiculos ─────────────────────────────────────────────────────────────
    op.drop_index("ix_vehiculos_rfid_tag_id", table_name="vehiculos")
    op.drop_constraint("uq_vehiculos_rfid_tag_id", "vehiculos", type_="unique")
    op.drop_column("vehiculos", "rfid_tag_id")

    # ── usuarios ─────────────────────────────────────────────────────────────
    op.drop_index("ix_usuarios_carnet_id", table_name="usuarios")
    op.drop_constraint("uq_usuarios_carnet_id", "usuarios", type_="unique")
    op.drop_column("usuarios", "carnet_id")
