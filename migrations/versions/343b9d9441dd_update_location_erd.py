"""Update location erd

Revision ID: 343b9d9441dd
Revises: 1e1679d8eaeb
Create Date: 2026-05-08 20:58:40.306353

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '343b9d9441dd'
down_revision = '1e1679d8eaeb'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if 'locations' not in existing_tables:
        op.create_table(
            'locations',
            sa.Column('location_id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('location_name', sa.String(length=200), nullable=False),
            sa.Column('longitude', sa.Float(), nullable=False),
            sa.Column('latitude', sa.Float(), nullable=False),
            sa.PrimaryKeyConstraint('location_id'),
        )

    # Do not re-add conv_type: revision 1e1679d8eaeb removed it to match the ORM.
    # Keep messages.product_id: Message ORM still maps product_id (needed for seed & queries).

    product_columns = {col['name'] for col in inspector.get_columns('products')}

    if 'location' in product_columns:
        # Backfill unique location rows from existing products before moving to FK.
        op.execute(sa.text(
            """
            INSERT INTO locations (location_name, longitude, latitude)
            SELECT p.location, 0.0, 0.0
            FROM products AS p
            WHERE p.location IS NOT NULL
              AND TRIM(p.location) <> ''
              AND NOT EXISTS (
                SELECT 1
                FROM locations AS l
                WHERE l.location_name = p.location
              )
            """
        ))

    if 'location_id' not in product_columns:
        with op.batch_alter_table('products', schema=None) as batch_op:
            batch_op.add_column(sa.Column('location_id', sa.Integer(), nullable=True))

    if 'location' in product_columns:
        op.execute(sa.text(
            """
            UPDATE products
            SET location_id = (
                SELECT l.location_id
                FROM locations AS l
                WHERE l.location_name = products.location
                LIMIT 1
            )
            WHERE location_id IS NULL
            """
        ))

    op.execute(sa.text(
        """
        UPDATE products
        SET location_id = (
            SELECT location_id
            FROM locations
            ORDER BY location_id ASC
            LIMIT 1
        )
        WHERE location_id IS NULL
        """
    ))

    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.alter_column('location_id', existing_type=sa.Integer(), nullable=False)
        batch_op.create_foreign_key(batch_op.f('fk_products_location_id_locations'), 'locations', ['location_id'], ['location_id'])
        if 'location' in product_columns:
            batch_op.drop_column('location')
        if 'review' in product_columns:
            batch_op.drop_column('review')


def downgrade():
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.add_column(sa.Column('review', sa.TEXT(), nullable=True))
        batch_op.add_column(sa.Column('location', sa.VARCHAR(length=200), nullable=True))

    op.execute(sa.text(
        """
        UPDATE products
        SET location = (
            SELECT l.location_name
            FROM locations AS l
            WHERE l.location_id = products.location_id
            LIMIT 1
        )
        """
    ))

    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.alter_column('location', existing_type=sa.VARCHAR(length=200), nullable=False)
        batch_op.drop_constraint(batch_op.f('fk_products_location_id_locations'), type_='foreignkey')
        batch_op.drop_column('location_id')

    op.drop_table('locations')
