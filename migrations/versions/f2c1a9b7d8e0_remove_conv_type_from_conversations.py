"""Remove conv_type from conversations

Revision ID: f2c1a9b7d8e0
Revises: a1b2c3d4e5f6
Create Date: 2026-05-10 15:51:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f2c1a9b7d8e0"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    conversation_columns = {col["name"] for col in inspector.get_columns("conversations")}

    if "conv_type" in conversation_columns:
        with op.batch_alter_table("conversations", schema=None) as batch_op:
            batch_op.drop_column("conv_type")


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    conversation_columns = {col["name"] for col in inspector.get_columns("conversations")}

    if "conv_type" not in conversation_columns:
        with op.batch_alter_table("conversations", schema=None) as batch_op:
            batch_op.add_column(
                sa.Column(
                    "conv_type",
                    sa.String(length=30),
                    nullable=False,
                    server_default=sa.text("'direct'"),
                )
            )

        with op.batch_alter_table("conversations", schema=None) as batch_op:
            batch_op.alter_column(
                "conv_type",
                existing_type=sa.String(length=30),
                server_default=None,
            )
