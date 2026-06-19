"""sync indexes and fix accesos FK to espacios_parqueo

Revision ID: 000000000002
Revises: 000000000001
Create Date: 2026-06-10 11:00:00.000000

Qué hace esta migración:
  A) Agrega índices ix_* en usuarios, vehiculos y accesos
     (usa IF NOT EXISTS para ser idempotente — las tablas pueden existir
      ya sea de la BD de dev o de la migración 000000000004 que las creó antes)
  B) Corrige la FK accesos.id_espacio → espacios_parqueo.id

  NOTA: vehiculos y accesos se crean en 000000000004. Si ya existen (entorno
  de dev) esta migración solo agrega los índices faltantes sin fallar.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = '000000000002'
down_revision: Union[str, None] = '000000000001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _index_exists(bind, table_name: str, index_name: str) -> bool:
    inspector = sa.inspect(bind)
    return any(ix["name"] == index_name for ix in inspector.get_indexes(table_name))


def _table_exists(bind, table_name: str) -> bool:
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    bind = op.get_bind()

    # ── A) Índices en usuarios ────────────────────────────────────────────────
    if not _index_exists(bind, 'usuarios', 'ix_usuarios_id_usuario'):
        op.create_index('ix_usuarios_id_usuario', 'usuarios', ['id_usuario'], unique=False)
    if not _index_exists(bind, 'usuarios', 'ix_usuarios_correo'):
        op.create_index('ix_usuarios_correo', 'usuarios', ['correo'], unique=True)

    # ── B) Índices en vehiculos (solo si la tabla existe) ─────────────────────
    if _table_exists(bind, 'vehiculos'):
        if not _index_exists(bind, 'vehiculos', 'ix_vehiculos_id_vehiculo'):
            op.create_index('ix_vehiculos_id_vehiculo', 'vehiculos', ['id_vehiculo'], unique=False)
        if not _index_exists(bind, 'vehiculos', 'ix_vehiculos_id_usuario'):
            op.create_index('ix_vehiculos_id_usuario', 'vehiculos', ['id_usuario'], unique=False)

    # ── C) Índices en accesos (solo si la tabla existe) ───────────────────────
    if _table_exists(bind, 'accesos'):
        if not _index_exists(bind, 'accesos', 'ix_accesos_id_acceso'):
            op.create_index('ix_accesos_id_acceso', 'accesos', ['id_acceso'], unique=False)
        if not _index_exists(bind, 'accesos', 'ix_accesos_id_usuario'):
            op.create_index('ix_accesos_id_usuario', 'accesos', ['id_usuario'], unique=False)
        if not _index_exists(bind, 'accesos', 'ix_accesos_id_vehiculo'):
            op.create_index('ix_accesos_id_vehiculo', 'accesos', ['id_vehiculo'], unique=False)
        if not _index_exists(bind, 'accesos', 'ix_accesos_id_espacio'):
            op.create_index('ix_accesos_id_espacio', 'accesos', ['id_espacio'], unique=False)

        # ── D) Corregir FK accesos.id_espacio → espacios_parqueo.id ──────────
        fks = {fk["name"] for fk in sa.inspect(bind).get_foreign_keys('accesos')}
        if 'accesos_id_espacio_fkey' in fks:
            op.drop_constraint('accesos_id_espacio_fkey', 'accesos', type_='foreignkey')
        op.create_foreign_key(
            constraint_name='accesos_id_espacio_fkey',
            source_table='accesos',
            referent_table='espacios_parqueo',
            local_cols=['id_espacio'],
            remote_cols=['id'],
        )


def downgrade() -> None:
    bind = op.get_bind()

    if _table_exists(bind, 'accesos'):
        op.drop_constraint('accesos_id_espacio_fkey', 'accesos', type_='foreignkey')
        if _index_exists(bind, 'accesos', 'ix_accesos_id_espacio'):
            op.drop_index('ix_accesos_id_espacio',  table_name='accesos')
        if _index_exists(bind, 'accesos', 'ix_accesos_id_vehiculo'):
            op.drop_index('ix_accesos_id_vehiculo', table_name='accesos')
        if _index_exists(bind, 'accesos', 'ix_accesos_id_usuario'):
            op.drop_index('ix_accesos_id_usuario',  table_name='accesos')
        if _index_exists(bind, 'accesos', 'ix_accesos_id_acceso'):
            op.drop_index('ix_accesos_id_acceso',   table_name='accesos')

    if _table_exists(bind, 'vehiculos'):
        if _index_exists(bind, 'vehiculos', 'ix_vehiculos_id_usuario'):
            op.drop_index('ix_vehiculos_id_usuario',  table_name='vehiculos')
        if _index_exists(bind, 'vehiculos', 'ix_vehiculos_id_vehiculo'):
            op.drop_index('ix_vehiculos_id_vehiculo', table_name='vehiculos')

    if _index_exists(bind, 'usuarios', 'ix_usuarios_correo'):
        op.drop_index('ix_usuarios_correo',     table_name='usuarios')
    if _index_exists(bind, 'usuarios', 'ix_usuarios_id_usuario'):
        op.drop_index('ix_usuarios_id_usuario', table_name='usuarios')
