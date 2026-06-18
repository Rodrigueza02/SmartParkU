"""create vehiculos and accesos tables

Revision ID: 000000000004
Revises: 000000000003
Create Date: 2026-06-18 12:00:00.000000

Qué hace esta migración:
  Crea las tablas `vehiculos` y `accesos` que faltaban en el historial de Alembic.
  Las tablas existen en la BD de desarrollo actual (se crearon manualmente o via
  SQLAlchemy create_all), pero este archivo garantiza que un entorno nuevo quede
  correctamente inicializado al correr `alembic upgrade head`.

  Usa `checkfirst=True` en create_table y maneja el caso en que las tablas
  ya existan, por lo que es seguro correrla sobre la BD de desarrollo existente.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.exc import ProgrammingError


# revision identifiers
revision: str = '000000000004'
down_revision: Union[str, None] = '000000000003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Tabla vehiculos ───────────────────────────────────────────────────────
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()

    if 'vehiculos' not in existing_tables:
        op.create_table(
            'vehiculos',
            sa.Column('id_vehiculo', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('placa', sa.String(length=20), nullable=True),
            sa.Column('tipo', sa.String(length=20), nullable=True),
            sa.Column(
                'id_usuario', sa.Integer(),
                sa.ForeignKey('usuarios.id_usuario', name='vehiculos_id_usuario_fkey'),
                nullable=True,
            ),
            sa.PrimaryKeyConstraint('id_vehiculo'),
        )
        op.create_index('ix_vehiculos_id_vehiculo', 'vehiculos', ['id_vehiculo'], unique=False)
        op.create_index('ix_vehiculos_id_usuario',  'vehiculos', ['id_usuario'],  unique=False)

    # ── Tabla accesos ─────────────────────────────────────────────────────────
    if 'accesos' not in existing_tables:
        op.create_table(
            'accesos',
            sa.Column('id_acceso',    sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('id_usuario',   sa.Integer(),
                      sa.ForeignKey('usuarios.id_usuario',          name='accesos_id_usuario_fkey'),
                      nullable=True),
            sa.Column('id_vehiculo',  sa.Integer(),
                      sa.ForeignKey('vehiculos.id_vehiculo',         name='accesos_id_vehiculo_fkey'),
                      nullable=True),
            sa.Column('id_espacio',   sa.Integer(),
                      sa.ForeignKey('espacios_parqueo.id',           name='accesos_id_espacio_fkey'),
                      nullable=True),
            sa.Column('hora_entrada', sa.DateTime(), nullable=True),
            sa.Column('hora_salida',  sa.DateTime(), nullable=True),
            sa.Column('metodo',       sa.String(length=50), nullable=True),
            sa.PrimaryKeyConstraint('id_acceso'),
        )
        op.create_index('ix_accesos_id_acceso',   'accesos', ['id_acceso'],   unique=False)
        op.create_index('ix_accesos_id_usuario',  'accesos', ['id_usuario'],  unique=False)
        op.create_index('ix_accesos_id_vehiculo', 'accesos', ['id_vehiculo'], unique=False)
        op.create_index('ix_accesos_id_espacio',  'accesos', ['id_espacio'],  unique=False)
        op.create_index('ix_accesos_metodo',      'accesos', ['metodo'],      unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()

    if 'accesos' in existing_tables:
        op.drop_index('ix_accesos_metodo',      table_name='accesos')
        op.drop_index('ix_accesos_id_espacio',  table_name='accesos')
        op.drop_index('ix_accesos_id_vehiculo', table_name='accesos')
        op.drop_index('ix_accesos_id_usuario',  table_name='accesos')
        op.drop_index('ix_accesos_id_acceso',   table_name='accesos')
        op.drop_table('accesos')

    if 'vehiculos' in existing_tables:
        op.drop_index('ix_vehiculos_id_usuario',  table_name='vehiculos')
        op.drop_index('ix_vehiculos_id_vehiculo', table_name='vehiculos')
        op.drop_table('vehiculos')
