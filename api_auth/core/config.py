import os
from pathlib import Path

import pydantic as pd


class Settings(pd.BaseSettings):
    PROJECT_NAME: str

    API_AUTH_HOST: str
    API_AUTH_PORT: int

    SERVICE_TO_SERVICE_SECRET: str

    API_NOTIFICATIONS_HOST: str
    API_NOTIFICATIONS_PORT: int

    JAEGER_HOST: str
    JAEGER_PORT: int

    REDIS_HOST: str
    REDIS_PORT: int

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    AUTH_SECRET: str

    DOCS_URL: str

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    YANDEX_CLIENT_ID: str
    YANDEX_CLIENT_SECRET: str

    def __init__(self, DOCKER, DEBUG, BASE_DIR):

        if DEBUG and DOCKER:
            super().__init__([BASE_DIR / '.envs/.docker-compose-local/.api',
                              BASE_DIR / '.envs/.docker-compose-local/.postgres',
                              BASE_DIR / '.envs/.docker-compose-local/.redis'])
        elif DEBUG and not DOCKER:
            super().__init__([BASE_DIR / '.envs/.local/.api',
                              BASE_DIR / '.envs/.local/.postgres',
                              BASE_DIR / '.envs/.local/.redis'])
        else:
            super().__init__([BASE_DIR / '.envs/.prod/.api',
                              BASE_DIR / '.envs/.prod/.postgres',
                              BASE_DIR / '.envs/.prod/.redis'])


BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEBUG = True if os.getenv('DEBUG', 'False') == 'True' else False
DOCKER = True if os.getenv('DOCKER', 'False') == 'True' else False

settings = Settings(DOCKER, DEBUG, BASE_DIR)

ACCESS_TOKEN_EXP_MIN: int = 15
REFRESH_TOKEN_EXP_MIN: int = 60 * 24 * 30
TEMPORARY_REGISTER_TOKEN_EXP_MIN: int = 60 * 3
TOKEN_ENCODE_ALGORITHM: str = 'HS256'
API_NOTIFICATIONS_HTTP_PREFIX: str = f'http://{settings.API_NOTIFICATIONS_HOST}:{settings.API_NOTIFICATIONS_PORT}'