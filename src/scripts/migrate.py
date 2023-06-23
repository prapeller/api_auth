from alembic import command

from core.alembic_helpers import get_updated_alembic_config


def migrate():
    updated_config = get_updated_alembic_config()
    command.upgrade(next(updated_config), "head")


if __name__ == '__main__':
    migrate()
