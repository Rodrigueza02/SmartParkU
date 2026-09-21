"""create alertas table

Revision ID: 20260921_1000
Revises: 20260908_1100
Create Date: 2026-09-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260921_1000'
down_revision = '20260908_1100'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'alertas',
        sa.Column('id_alerta', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('id_usuario', sa.Integer(), nullable=False),
        sa.Column('tipo', sa.String(length=50), nullable=False),
        sa.Column('mensaje', sa.Text(), nullable=False),
        sa.Column('ubicacion', sa.String(length=200), nullable=True),
        sa.Column('estado', sa.String(length=50), nullable=True),
        sa.Column('media_url', sa.String(length=500), nullable=True),
        sa.Column('media_type', sa.String(length=20), nullable=True),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False),
        sa.Column('fecha_revision', sa.DateTime(), nullable=True),
        sa.Column('revisado_por', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['id_usuario'], ['usuarios.id_usuario'], ),
        sa.ForeignKeyConstraint(['revisado_por'], ['usuarios.id_usuario'], ),
        sa.PrimaryKeyConstraint('id_alerta')
    )
    op.create_index(op.f('ix_alertas_id_alerta'), 'alertas', ['id_alerta'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_alertas_id_alerta'), table_name='alertas')
    op.drop_table('alertas')
