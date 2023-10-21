1) https://github.com/prapeller/Auth_sprint_2
api_auth - authorization api

2) https://github.com/prapeller/Async_API_sprint_2
api_search - search through films, genres, persons

# 1) Deploy locally (api at host)
- > make api-redis-build-loc
- > make postgres-build-loc
- > cd api_auth 
  > python3.11 -m venv venv && source venv/bin/activate && pip install -r requirements/local.txt
- > python -m scripts.migrate
- > export DEBUG=True && export DOCKER=False && python main.py
- > make api-create-superuser-loc
- swagger docs can be found at 127.0.0.1:8081/docs


# 2) Deploy locally (api at docker container)
- > make build-loc
- > make api-migrate-loc
- > make api-create-superuser-loc
- swagger can be found at 127.0.0.1:81/docs


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
