import logging

from alembic import command

from core.alembic_helpers import (
    get_updated_alembic_config,
    get_next_version_index,
    get_args_message,
)

logger = logging.getLogger(__name__)


def make_migration(message: str, version_index: int):
    migration_message = f'{version_index}_{message}'
    updated_config = get_updated_alembic_config()
    command.revision(next(updated_config), autogenerate=True, message=migration_message)


if __name__ == '__main__':
    message = get_args_message()
    next_version_index = get_next_version_index()
    if message is None and next_version_index == 0:
        message = 'init'
    if message is None and next_version_index != 0:
        raise ValueError('need message for creating not initial migration, add -m "message"')

    make_migration(message, next_version_index)
