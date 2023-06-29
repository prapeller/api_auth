"""empty message

Revision ID: 182514e6040b
Revises: a0bedc808b57
Create Date: 2023-06-05 11:47:15.113430

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '182514e6040b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')


def downgrade() -> None:
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp";')
