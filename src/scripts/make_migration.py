import logging

from alembic import command

from core.alembic_helpers import get_updated_alembic_config, get_version_num, get_args_message

logger = logging.getLogger(__name__)


def make_migration(message: str, version_num: int):
    migration_message = f'{version_num}_{message}'
    updated_config = get_updated_alembic_config()
    command.revision(next(updated_config), autogenerate=True, message=migration_message)


if __name__ == '__main__':
    message = get_args_message()
    version_num = get_version_num()
    if message is None and version_num == 0:
        message = 'init'
    if message is None and version_num != 0:
        raise ValueError('need message for creating not initial migration, add -m "message"')

    make_migration(message, version_num)
