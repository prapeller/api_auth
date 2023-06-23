import argparse
import configparser
import tempfile

from alembic.config import Config

from core.shared import SRC_PATH
from db import DATABASE_URL


def get_updated_alembic_config():
    alembic_ini_path = SRC_PATH / "alembic.ini"

    # Read the alembic.ini file
    config = configparser.ConfigParser()
    config.read(alembic_ini_path)

    # Set the sqlalchemy.url adn script_location values
    config.set("alembic", "sqlalchemy.url", DATABASE_URL)
    config.set("alembic", "script_location", str(SRC_PATH / 'alembic'))

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_config_file:
        config.write(temp_config_file)
        temp_config_file_path = temp_config_file.name
    updated_config = Config(temp_config_file_path)
    try:
        yield updated_config
    finally:
        temp_config_file.close()


def get_version_num() -> int:
    versions_path = SRC_PATH / 'alembic/versions'
    return sum(1 for _ in versions_path.iterdir() if _.is_file())


def get_args_message() -> str | None:
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--message', type=str, help='The message string')

    args = parser.parse_args()
    message = args.message
    return message
