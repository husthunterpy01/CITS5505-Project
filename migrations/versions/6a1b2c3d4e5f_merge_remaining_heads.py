"""merge remaining alembic heads

Revision ID: 6a1b2c3d4e5f
Revises: a4039e72343b, 4f6a7c8d9e0f
Create Date: 2026-05-12
"""

from alembic import op
import sqlalchemy as sa


revision = "6a1b2c3d4e5f"
down_revision = ("a4039e72343b", "4f6a7c8d9e0f")
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass