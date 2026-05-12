"""merge all current alembic heads

Revision ID: e8d9c4a1b2f0
Revises: c2f8a91b4d3e, f2c1a9b7d8e0
Create Date: 2026-05-11
"""

from alembic import op
import sqlalchemy as sa


revision = "e8d9c4a1b2f0"
down_revision = ("c2f8a91b4d3e", "f2c1a9b7d8e0")
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
