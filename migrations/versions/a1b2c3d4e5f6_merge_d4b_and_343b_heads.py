"""Merge migration heads

Revision ID: a1b2c3d4e5f6
Revises: 343b9d9441dd, d4b6b4bc2d2f
Create Date: 2026-05-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = ('343b9d9441dd', 'd4b6b4bc2d2f')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass