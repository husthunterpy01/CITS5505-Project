"""Drop participant role from conversation participants

Revision ID: d4b6b4bc2d2f
Revises: 343b9d9441dd
Create Date: 2026-05-09 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4b6b4bc2d2f'
down_revision = '343b9d9441dd'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('conversation_participants', schema=None) as batch_op:
        batch_op.drop_column('participant_role')


def downgrade():
    with op.batch_alter_table('conversation_participants', schema=None) as batch_op:
        batch_op.add_column(sa.Column('participant_role', sa.String(length=30), nullable=False, server_default='user'))
