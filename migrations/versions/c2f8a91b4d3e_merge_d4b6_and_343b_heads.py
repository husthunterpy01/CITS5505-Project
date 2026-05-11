"""merge d4b6b4bc2d2f and 343b9d9441dd heads

Revision ID: c2f8a91b4d3e
Revises: 343b9d9441dd, d4b6b4bc2d2f
Create Date: 2026-05-10

"""
from alembic import op
import sqlalchemy as sa


revision = "c2f8a91b4d3e"
down_revision = ("343b9d9441dd", "d4b6b4bc2d2f")
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
