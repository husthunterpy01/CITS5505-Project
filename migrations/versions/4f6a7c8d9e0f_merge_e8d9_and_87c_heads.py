"""merge e8d9c4a1b2f0 and 87c3163be6e3 heads

Revision ID: 4f6a7c8d9e0f
Revises: e8d9c4a1b2f0, 87c3163be6e3
Create Date: 2026-05-12
"""

from alembic import op
import sqlalchemy as sa


revision = "4f6a7c8d9e0f"
down_revision = ("e8d9c4a1b2f0", "87c3163be6e3")
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass