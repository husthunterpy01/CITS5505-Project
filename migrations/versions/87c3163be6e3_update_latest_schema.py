"""Update latest schema

Revision ID: 87c3163be6e3
Revises: 5d0e25215f40
Create Date: 2026-05-06 16:28:16.149453

"""
from alembic import op
import sqlalchemy as sa
from werkzeug.security import generate_password_hash


# revision identifiers, used by Alembic.
revision = '87c3163be6e3'
down_revision = '5d0e25215f40'
branch_labels = None
depends_on = None


FK_CONVENTION = {'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s'}


def _backfill_user_passwords_if_missing(bind):
    """Ensure users.password/password_hash has no NULL before batch rewrite."""
    inspector = sa.inspect(bind)
    user_columns = {col['name'] for col in inspector.get_columns('users')}

    fallback_hash = generate_password_hash('password123')
    if 'password' in user_columns:
        bind.execute(
            sa.text("UPDATE users SET password = :fallback WHERE password IS NULL"),
            {'fallback': fallback_hash},
        )
    if 'password_hash' in user_columns:
        bind.execute(
            sa.text("UPDATE users SET password_hash = :fallback WHERE password_hash IS NULL"),
            {'fallback': fallback_hash},
        )


def upgrade():
    bind = op.get_bind()
    existing_tables = set(sa.inspect(bind).get_table_names())
    if 'users' in existing_tables:
        _backfill_user_passwords_if_missing(bind)

    if 'conversation_participants' not in existing_tables:
        op.create_table(
            'conversation_participants',
            sa.Column('conversation_participant_id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('conversation_id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('participant_role', sa.String(length=30), nullable=False),
            sa.ForeignKeyConstraint(['conversation_id'], ['conversations.conversation_id']),
            sa.ForeignKeyConstraint(['user_id'], ['users.user_id']),
            sa.PrimaryKeyConstraint('conversation_participant_id'),
        )

    if 'conversations' not in existing_tables:
        op.create_table(
            'conversations',
            sa.Column('conversation_id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('product_id', sa.Integer(), nullable=False),
            sa.Column('conv_type', sa.String(length=30), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.Column('message_id', sa.Integer(), nullable=True),
            sa.Column('participant_id', sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(['message_id'], ['messages.message_id']),
            sa.ForeignKeyConstraint(['participant_id'], ['conversation_participants.conversation_participant_id']),
            sa.ForeignKeyConstraint(['product_id'], ['products.product_id']),
            sa.PrimaryKeyConstraint('conversation_id'),
        )

    if 'logging' not in existing_tables:
        op.create_table(
            'logging',
            sa.Column('logging_id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('target_type', sa.String(length=50), nullable=False),
            sa.Column('target_id', sa.Integer(), nullable=False),
            sa.Column('action', sa.String(length=100), nullable=False),
            sa.Column('reason', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.user_id']),
            sa.PrimaryKeyConstraint('logging_id'),
        )

    with op.batch_alter_table('messages', schema=None, naming_convention=FK_CONVENTION) as batch_op:
        batch_op.add_column(sa.Column('conversation_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('message_type', sa.String(length=30), nullable=False, server_default=sa.text("'text'")))
        batch_op.add_column(sa.Column('is_read', sa.Boolean(), nullable=False, server_default=sa.false()))
        batch_op.add_column(sa.Column('read_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')))
        batch_op.create_foreign_key('fk_messages_conversation_id_conversations', 'conversations', ['conversation_id'], ['conversation_id'])
        batch_op.drop_column('receiver_id')

    op.execute(sa.text(
        """
        INSERT INTO conversations (product_id, conv_type, created_at, updated_at)
        SELECT DISTINCT m.product_id, 'direct', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
        FROM messages AS m
        WHERE NOT EXISTS (
            SELECT 1
            FROM conversations AS c
            WHERE c.product_id = m.product_id
              AND c.conv_type = 'direct'
        )
        """
    ))

    op.execute(sa.text(
        """
        UPDATE messages
        SET conversation_id = (
            SELECT conversation_id
            FROM conversations
            WHERE conversations.product_id = messages.product_id
            ORDER BY conversation_id ASC
            LIMIT 1
        )
        WHERE conversation_id IS NULL
        """
    ))

    with op.batch_alter_table('messages', schema=None, naming_convention=FK_CONVENTION) as batch_op:
        batch_op.alter_column('conversation_id', existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column('created_at', existing_type=sa.DateTime(), server_default=None)
        batch_op.alter_column('message_type', existing_type=sa.String(length=30), server_default=None)
        batch_op.alter_column('is_read', existing_type=sa.Boolean(), server_default=None)

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column(
            'password',
            new_column_name='password_hash',
            existing_type=sa.String(length=255),
            existing_nullable=False,
        )


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column(
            'password_hash',
            new_column_name='password',
            existing_type=sa.VARCHAR(length=255),
            existing_nullable=False,
        )

    with op.batch_alter_table('messages', schema=None, naming_convention=FK_CONVENTION) as batch_op:
        batch_op.add_column(sa.Column('receiver_id', sa.INTEGER(), nullable=True))
        batch_op.create_foreign_key('fk_messages_receiver_id_users', 'users', ['receiver_id'], ['user_id'])
        batch_op.drop_column('created_at')
        batch_op.drop_column('read_at')
        batch_op.drop_column('is_read')
        batch_op.drop_column('message_type')
        batch_op.drop_column('conversation_id')

    bind = op.get_bind()
    existing_tables = set(sa.inspect(bind).get_table_names())
    if 'logging' in existing_tables:
        op.drop_table('logging')
    if 'conversations' in existing_tables:
        op.drop_table('conversations')
    if 'conversation_participants' in existing_tables:
        op.drop_table('conversation_participants')
