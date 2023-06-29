# 1) Run .local
- install docker, docker-compose
https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-22-04
https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-20-04
-  rename .envs/.example to .envs/.local, set your variables
- > python3.11 -m venv venv
- > source venv/bin/activate && cd src && pip install -r requirements/local.txt
- > make build-postgres-loc
- > make build-redis-loc
- > python -m scripts.migrate
- > python -m scripts.create_superuser
- > export DEBUG=True
- > export DOCKER=False
- > python main.py

- swagger can be found at 127.0.0.1:8080/[DOCS_URL]

- to run tests:
- > python -m pytest

# 2) Run .docker-compose-local
- install docker, docker-compose
-  rename .envs/.example to .envs/.docker-compose-local, set your variables
- > cd src
- > make build-loc
- > make superuser-loc

- swagger can be found at 127.0.0.1:8080/[DOCS_URL]

- to run tests:
- > make tests


# 2) Run .prod
- install docker, docker-compose
-  rename .envs/.example to .envs/.prod
- > cd src
- > make build
- > make superuser

- swagger can be found at 127.0.0.1/[DOCS_URL]


# Architecture:
### Database:
- function: store users credentials, roles, permissions
- specific: Postgres

### SqlAlchemyRepository:
- function: crud for sqlalchemy models
- specific: declarative base

### AuthManager
- function: register, login, refresh-token, logout
- specific: JWT tokens

### Cache:
- function: store sessions with active refresh tokens
- specific: Redis

