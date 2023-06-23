import os
from pathlib import Path

import pydantic as pd


class TestSettings(pd.BaseSettings):
    API_HOST: str = '127.0.0.1'
    API_PORT: int = 8080

    REDIS_HOST: str = '127.0.0.1'
    REDIS_PORT: int = 6379

    def __init__(self, DOCKER):
        BASE_DIR = Path(__file__).resolve().parent.parent.parent

        if DOCKER:
            super().__init__(_env_file=[BASE_DIR / '.envs/.docker-compose-local/.tests',
                                        BASE_DIR / '.envs/.docker-compose-local/.elastic',
                                        BASE_DIR / '.envs/.docker-compose-local/.redis'])
        else:
            super().__init__([BASE_DIR / '.envs/.local/.tests',
                              BASE_DIR / '.envs/.local/.elastic',
                              BASE_DIR / '.envs/.local/.redis'])


DOCKER = True if os.getenv('DOCKER', 'False') == 'True' else False

test_settings = TestSettings(DOCKER)
