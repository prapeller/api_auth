from alembic import command

from core.alembic_helpers import (
    get_updated_alembic_config,
    get_args_message,
    get_current_version_index,
)


def migrate(current_version_index=None, to_migrate_version_index=None):
    updated_config = get_updated_alembic_config()
    if current_version_index is None and to_migrate_version_index is None:
        command.upgrade(next(updated_config), "head")
    else:
        diff = to_migrate_version_index - current_version_index
        if diff > 0:
            command.upgrade(next(updated_config), f'+{diff}')
        else:
            command.downgrade(next(updated_config), f'{diff}')


if __name__ == '__main__':
    message = get_args_message()
    to_migrate_version_index = None

    if message is not None:
        try:
            to_migrate_version_index = int(message)
        except ValueError:
            raise ValueError('it should be index number to migrate to, use (-m version_index_int)')
        current_version_index = get_current_version_index()
        migrate(current_version_index, to_migrate_version_index)
    else:
        migrate()
