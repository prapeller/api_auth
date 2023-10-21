API_AUTH_LOCAL := -p api_auth -f ./docker/api/docker-compose-local.yml
POSTGRES_AUTH_LOCAL := -p postgres_auth -f ./docker/postgres/docker-compose-local.yml

API_AUTH_PROD := -p api_auth -f ./docker/api/prod.yml
POSTGRES_AUTH_PROD := -p postgres_auth -f ./docker/postgres/prod.yml

build-loc:
	@docker network create shared_network || true
	docker-compose $(POSTGRES_AUTH_LOCAL) up --build -d --remove-orphans
	docker-compose $(API_AUTH_LOCAL) up --build -d --remove-orphans

build:
	@docker network create shared_network || true
	docker-compose $(POSTGRES_AUTH_PROD) up --build -d --remove-orphans
	docker-compose $(API_AUTH_PROD) up --build -d --remove-orphans

down-loc:
	docker-compose $(POSTGRES_AUTH_LOCAL) down
	docker-compose $(API_AUTH_LOCAL) down

down:
	docker-compose $(POSTGRES_AUTH_PROD) down
	docker-compose $(API_AUTH_PROD) down

down-v-loc:
	docker-compose $(POSTGRES_AUTH_LOCAL) down -v
	docker-compose $(API_AUTH_LOCAL) down -v

down-v:
	docker-compose $(POSTGRES_AUTH_PROD) down -v
	docker-compose $(API_AUTH_PROD) down -v



api-build-loc:
	docker-compose $(API_AUTH_LOCAL) up --build -d  --remove-orphans --no-deps api_auth

api-build:
	docker-compose $(API_AUTH_PROD) up --build -d  --remove-orphans --no-deps api_auth

api-pipinstall-loc:
	docker-compose $(API_AUTH_LOCAL)  run --rm api_auth pip install -r requirements/local.txt

api-pipinstall:
	docker-compose $(API_AUTH_PROD)  run --rm api_auth pip install -r requirements/prod.txt

api-check-ip:
	docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' api_auth

api-redis-build-loc:
	docker-compose $(API_AUTH_LOCAL) up --build -d --remove-orphans --no-deps redis_auth

api-nginx-build-loc:
	docker-compose $(API_AUTH_LOCAL) up --build -d  --remove-orphans --no-deps nginx_auth

api-tests-build-loc:
	docker-compose $(API_AUTH_LOCAL) up --build -d --remove-orphans --no-deps tests_auth

api-create-superuser-loc:
	docker-compose $(API_AUTH_LOCAL) run --rm api_auth python3 -m scripts.create_superuser

api-create-superuser:
	docker-compose $(API_AUTH_PROD) run --rm api_auth python3 -m scripts.create_superuser

api-make-migration-loc:
	docker-compose $(API_AUTH_LOCAL) run --rm api_auth python3 -m scripts.make_migration

api-make-migration:
	docker-compose $(API_AUTH_PROD) run --rm api_auth python3 -m scripts.make_migration

api-migrate-loc:
	docker-compose $(API_AUTH_LOCAL) run --rm api_auth python3 -m scripts.migrate

api-migrate:
	docker-compose $(API_AUTH_PROD) run --rm api_auth python3 -m scripts.migrate

api-jaeger-build:
	docker-compose -f docker-compose-base.yml -f docker-compose-prod.yml -p jaeger_auth up --build -d  --remove-orphans --no-deps jaeger_auth

api-jaeger-build-loc:
	docker-compose -f docker-compose-base.yml -f docker-compose-local.yml -p jaeger_auth up --build -d  --remove-orphans --no-deps jaeger_auth



postgres-build:
	docker-compose $(POSTGRES_AUTH_PROD) up --build -d  --remove-orphans --no-deps postgres_auth

postgres-build-loc:
	docker-compose $(POSTGRES_AUTH_LOCAL) up --build -d  --remove-orphans --no-deps postgres_auth

postgres-down-loc:
	docker-compose $(POSTGRES_AUTH_LOCAL) down

postgres-down:
	docker-compose $(POSTGRES_AUTH_PROD) down

postgres-down-v-loc:
	docker-compose $(POSTGRES_AUTH_LOCAL) down -v

postgres-down-v:
	docker-compose $(POSTGRES_AUTH_PROD) down -v

postgres-dump-loc:
	docker-compose $(POSTGRES_AUTH_LOCAL) exec postgres_auth dump.sh

postgres-dump:
	docker-compose $(POSTGRES_AUTH_PROD) exec postgres_auth dump.sh



check-config:
	docker-compose $(API_AUTH_PROD) config
	docker-compose $(POSTGRES_AUTH_PROD) config

check-config-loc:
	docker-compose $(API_AUTH_LOCAL) config
	docker-compose $(POSTGRES_AUTH_LOCAL) config



check-logs:
	docker-compose $(API_AUTH_PROD) logs
	docker-compose $(POSTGRES_AUTH_PROD) logs

check-logs-loc:
	docker-compose $(API_AUTH_LOCAL) logs
	docker-compose $(POSTGRES_AUTH_LOCAL) logs



flake8:
	docker-compose $(API_AUTH_LOCAL) exec api_auth flake8 .

black-check:
	docker-compose $(API_AUTH_LOCAL) exec api_auth black --check --exclude=venv .

black-diff:
	docker-compose $(API_AUTH_LOCAL) exec api_auth black --diff --exclude=venv .

black:
	docker-compose $(API_AUTH_LOCAL) exec api_auth black --exclude=venv .

isort-check:
	docker-compose $(API_AUTH_LOCAL) exec api_auth isort . --check-only --skip venv

isort-diff:
	docker-compose $(API_AUTH_LOCAL) exec api_auth isort . --diff --skip venv

isort:
	docker-compose $(API_AUTH_LOCAL) exec api_auth isort . --skip venv







make-migration:
	docker-compose -f docker-compose-base.yml -f docker-compose-prod.yml -p api_auth run --rm api_auth python3 -m scripts.make_migration

make-migration-loc:
	docker-compose -f docker-compose-base.yml -f docker-compose-local.yml -p api_auth run --rm api_auth python3 -m scripts.make_migration


migrate:
	docker-compose -f docker-compose-base.yml -f docker-compose-prod.yml -p api_auth run --rm api_auth python3 -m scripts.migrate

migrate-loc:
	docker-compose -f docker-compose-base.yml -f docker-compose-local.yml -p api_auth run --rm api_auth python3 -m scripts.migrate
