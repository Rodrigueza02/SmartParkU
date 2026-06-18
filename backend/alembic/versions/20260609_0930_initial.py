
"""initial

Revision ID: 000000000001
Revises: 
Create Date: 2026-06-09 09:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '000000000001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create usuarios table
    op.create_table(
        'usuarios',
        sa.Column('id_usuario', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.Column('correo', sa.String(length=100), nullable=False),
        sa.Column('password', sa.String(length=100), nullable=False),
        sa.Column('rol', sa.String(length=50), nullable=False),
        sa.Column('estado', sa.String(length=50), nullable=True, server_default='Activo'),
        sa.PrimaryKeyConstraint('id_usuario'),
        sa.UniqueConstraint('correo')
    )
    op.create_index(op.f('ix_usuarios_correo'), 'usuarios', ['correo'], unique=True)
    op.create_index(op.f('ix_usuarios_id_usuario'), 'usuarios', ['id_usuario'], unique=False)

    # Create espacios_parqueo table
    op.create_table(
        'espacios_parqueo',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('slot_id', sa.String(length=20), nullable=False),
        sa.Column('label', sa.String(length=20), nullable=False),
        sa.Column('tipo', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='libre'),
        sa.Column('distancia_cm', sa.Float(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slot_id')
    )
    op.create_index(op.f('ix_espacios_parqueo_id'), 'espacios_parqueo', ['id'], unique=False)
    op.create_index(op.f('ix_espacios_parqueo_slot_id'), 'espacios_parqueo', ['slot_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_espacios_parqueo_slot_id'), table_name='espacios_parqueo')
    op.drop_index(op.f('ix_espacios_parqueo_id'), table_name='espacios_parqueo')
    op.drop_table('espacios_parqueo')
    op.drop_index(op.f('ix_usuarios_id_usuario'), table_name='usuarios')
    op.drop_index(op.f('ix_usuarios_correo'), table_name='usuarios')
    op.drop_table('usuarios')
