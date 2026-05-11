"""merge migration heads

Revision ID: a4039e72343b
Revises: 343b9d9441dd, d4b6b4bc2d2f
Create Date: 2026-05-09 23:30:29.470116

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a4039e72343b'
down_revision = ('343b9d9441dd', 'd4b6b4bc2d2f')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
