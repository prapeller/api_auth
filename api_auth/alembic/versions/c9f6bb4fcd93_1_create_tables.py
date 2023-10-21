"""1_create tables

Revision ID: c9f6bb4fcd93
Revises: 182514e6040b
Create Date: 2023-10-21 11:17:56.785528

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c9f6bb4fcd93'
down_revision = '182514e6040b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('permission',
    sa.Column('name', sa.String(length=20), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uuid', sa.UUID(as_uuid=False), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_permission_uuid'), 'permission', ['uuid'], unique=True)
    op.create_table('role',
    sa.Column('name', sa.String(length=20), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uuid', sa.UUID(as_uuid=False), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_role_uuid'), 'role', ['uuid'], unique=True)
    op.create_table('user',
    sa.Column('email', sa.String(length=50), nullable=True),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.Column('password', sa.String(length=100), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uuid', sa.UUID(as_uuid=False), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_uuid'), 'user', ['uuid'], unique=True)
    op.create_table('role_permission',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('role_uuid', sa.UUID(as_uuid=False), nullable=True),
    sa.Column('permission_uuid', sa.UUID(as_uuid=False), nullable=True),
    sa.ForeignKeyConstraint(['permission_uuid'], ['permission.uuid'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['role_uuid'], ['role.uuid'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('role_uuid', 'permission_uuid', name='unique_role_uuid_permission_uuid')
    )
    op.create_table('session',
    sa.Column('user_uuid', sa.UUID(as_uuid=False), nullable=True),
    sa.Column('useragent', sa.String(length=512), nullable=True),
    sa.Column('ip', sa.String(length=39), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uuid', sa.UUID(as_uuid=False), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_uuid'], ['user.uuid'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_session_uuid'), 'session', ['uuid'], unique=True)
    op.create_table('social_account',
    sa.Column('user_uuid', sa.UUID(as_uuid=False), nullable=True),
    sa.Column('social_name', sa.String(length=20), nullable=True),
    sa.Column('social_uuid', sa.String(length=50), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uuid', sa.UUID(as_uuid=False), server_default=sa.text('uuid_generate_v4()'), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_uuid'], ['user.uuid'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_uuid', 'social_uuid', name='unique_user_uuid_social_uuid')
    )
    op.create_index(op.f('ix_social_account_uuid'), 'social_account', ['uuid'], unique=True)
    op.create_table('user_role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_uuid', sa.UUID(as_uuid=False), nullable=True),
    sa.Column('role_uuid', sa.UUID(as_uuid=False), nullable=True),
    sa.ForeignKeyConstraint(['role_uuid'], ['role.uuid'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_uuid'], ['user.uuid'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_uuid', 'role_uuid', name='unique_user_uuid_role_uuid')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_role')
    op.drop_index(op.f('ix_social_account_uuid'), table_name='social_account')
    op.drop_table('social_account')
    op.drop_index(op.f('ix_session_uuid'), table_name='session')
    op.drop_table('session')
    op.drop_table('role_permission')
    op.drop_index(op.f('ix_user_uuid'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_index(op.f('ix_role_uuid'), table_name='role')
    op.drop_table('role')
    op.drop_index(op.f('ix_permission_uuid'), table_name='permission')
    op.drop_table('permission')
    # ### end Alembic commands ###
