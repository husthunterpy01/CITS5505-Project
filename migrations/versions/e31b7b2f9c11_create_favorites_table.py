"""create favorites table

Revision ID: e31b7b2f9c11
Revises: b1d2e3f4a5b6
Create Date: 2026-05-16 15:58:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = 'e31b7b2f9c11'
down_revision = 'b1d2e3f4a5b6'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'favorites',
        sa.Column('favorite_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.product_id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id']),
        sa.PrimaryKeyConstraint('favorite_id'),
        sa.UniqueConstraint('user_id', 'product_id', name='uq_favorite_user_product'),
    )
    op.create_index(op.f('ix_favorites_user_id'), 'favorites', ['user_id'], unique=False)
    op.create_index(op.f('ix_favorites_product_id'), 'favorites', ['product_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_favorites_product_id'), table_name='favorites')
    op.drop_index(op.f('ix_favorites_user_id'), table_name='favorites')
    op.drop_table('favorites')
