"""add index on accesos.metodo for QR flow

Revision ID: 000000000003
Revises: 000000000002
Create Date: 2026-06-18 10:00:00.000000

Qué hace esta migración:
  - Agrega un índice en accesos.metodo para acelerar las consultas
    de accesos registrados por QR (metodo = 'qr').
  - No modifica la estructura de tablas existentes.

Flujo QR:
  Al escanear un QR, el servicio qr_service.py crea un Acceso con
  metodo='qr', id_espacio apuntando al espacio asignado, y marca
  el EspacioParqueo.status = 'ocupado'.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = '000000000003'
down_revision: Union[str, None] = '000000000002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    # Solo crear si la tabla existe y el índice no existe todavía
    if 'accesos' in inspector.get_table_names():
        existing = [ix["name"] for ix in inspector.get_indexes('accesos')]
        if 'ix_accesos_metodo' not in existing:
            op.create_index('ix_accesos_metodo', 'accesos', ['metodo'], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if 'accesos' in inspector.get_table_names():
        existing = [ix["name"] for ix in inspector.get_indexes('accesos')]
        if 'ix_accesos_metodo' in existing:
            op.drop_index('ix_accesos_metodo', table_name='accesos')
