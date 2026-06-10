"""sync indexes and fix accesos FK to espacios_parqueo

Revision ID: 000000000002
Revises: 000000000001
Create Date: 2026-06-10 11:00:00.000000

Qué hace esta migración:
  A) Crea los índices ix_* faltantes en usuarios, vehiculos y accesos
     (las tablas ya existen — NO se recrea ninguna tabla)
  B) Corrige la FK accesos.id_espacio:
       ANTES : accesos_id_espacio_fkey -> espacios.id_espacio  (tabla legacy v1)
       DESPUÉS: accesos_id_espacio_fkey -> espacios_parqueo.id (tabla IoT activa)

Pre-condición verificada (2026-06-10):
  - accesos contiene 1 fila con id_espacio=1
  - espacios_parqueo.id=1 existe (slot_01, C-01)
  - 0 huérfanos -> migración de FK es segura

SQL equivalente:
  -- índices
  CREATE INDEX ix_usuarios_id_usuario   ON usuarios        (id_usuario);
  CREATE INDEX ix_usuarios_correo       ON usuarios        (correo);
  CREATE INDEX ix_vehiculos_id_vehiculo ON vehiculos       (id_vehiculo);
  CREATE INDEX ix_vehiculos_id_usuario  ON vehiculos       (id_usuario);
  CREATE INDEX ix_accesos_id_acceso     ON accesos         (id_acceso);
  CREATE INDEX ix_accesos_id_usuario    ON accesos         (id_usuario);
  CREATE INDEX ix_accesos_id_vehiculo   ON accesos         (id_vehiculo);
  CREATE INDEX ix_accesos_id_espacio    ON accesos         (id_espacio);
  -- FK correction
  ALTER TABLE accesos DROP CONSTRAINT accesos_id_espacio_fkey;
  ALTER TABLE accesos ADD CONSTRAINT accesos_id_espacio_fkey
      FOREIGN KEY (id_espacio) REFERENCES espacios_parqueo (id);
"""
from typing import Sequence, Union
from alembic import op


# revision identifiers
revision: str = '000000000002'
down_revision: Union[str, None] = '000000000001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── A) Índices faltantes en usuarios ─────────────────────────────────────
    op.create_index('ix_usuarios_id_usuario', 'usuarios', ['id_usuario'], unique=False)
    op.create_index('ix_usuarios_correo',     'usuarios', ['correo'],     unique=True)

    # ── B) Índices faltantes en vehiculos ─────────────────────────────────────
    op.create_index('ix_vehiculos_id_vehiculo', 'vehiculos', ['id_vehiculo'], unique=False)
    op.create_index('ix_vehiculos_id_usuario',  'vehiculos', ['id_usuario'],  unique=False)

    # ── C) Índices faltantes en accesos ───────────────────────────────────────
    op.create_index('ix_accesos_id_acceso',   'accesos', ['id_acceso'],   unique=False)
    op.create_index('ix_accesos_id_usuario',  'accesos', ['id_usuario'],  unique=False)
    op.create_index('ix_accesos_id_vehiculo', 'accesos', ['id_vehiculo'], unique=False)
    op.create_index('ix_accesos_id_espacio',  'accesos', ['id_espacio'],  unique=False)

    # ── D) Corregir FK accesos.id_espacio -> espacios_parqueo.id ──────────────
    # Eliminar constraint legacy que apunta a espacios.id_espacio
    op.drop_constraint('accesos_id_espacio_fkey', 'accesos', type_='foreignkey')
    # Crear nuevo constraint apuntando a espacios_parqueo.id
    op.create_foreign_key(
        constraint_name='accesos_id_espacio_fkey',
        source_table='accesos',
        referent_table='espacios_parqueo',
        local_cols=['id_espacio'],
        remote_cols=['id'],
    )


def downgrade() -> None:
    # ── Revertir FK a espacios (legacy) ──────────────────────────────────────
    op.drop_constraint('accesos_id_espacio_fkey', 'accesos', type_='foreignkey')
    op.create_foreign_key(
        constraint_name='accesos_id_espacio_fkey',
        source_table='accesos',
        referent_table='espacios',
        local_cols=['id_espacio'],
        remote_cols=['id_espacio'],
    )

    # ── Eliminar índices accesos ──────────────────────────────────────────────
    op.drop_index('ix_accesos_id_espacio',  table_name='accesos')
    op.drop_index('ix_accesos_id_vehiculo', table_name='accesos')
    op.drop_index('ix_accesos_id_usuario',  table_name='accesos')
    op.drop_index('ix_accesos_id_acceso',   table_name='accesos')

    # ── Eliminar índices vehiculos ────────────────────────────────────────────
    op.drop_index('ix_vehiculos_id_usuario',  table_name='vehiculos')
    op.drop_index('ix_vehiculos_id_vehiculo', table_name='vehiculos')

    # ── Eliminar índices usuarios ─────────────────────────────────────────────
    op.drop_index('ix_usuarios_correo',     table_name='usuarios')
    op.drop_index('ix_usuarios_id_usuario', table_name='usuarios')
