up:
	docker-compose -f docker-compose-base.yml -f docker-compose-prod.yml -p api_auth up -d

up-loc:
	docker-compose -f docker-compose-base.yml -f docker-compose-local.yml -p api_auth up -d


build-postgres:
	docker-compose -f docker-compose-base.yml -f docker-compose-prod.yml -p api_auth up --build -d  --remove-orphans --no-deps postgres_auth

build-postgres-loc:
	docker-compose -f docker-compose-base.yml -f docker-compose-local.yml -p api_auth up --build -d  --remove-orphans --no-deps postgres_auth


build-redis:
	docker-compose -f docker-compose-base.yml -f docker-compose-prod.yml -p api_auth up --build -d  --remove-orphans --no-deps redis_auth

build-redis-loc:
	docker-compose -f docker-compose-base.yml -f docker-compose-local.yml -p api_auth up --build -d  --remove-orphans --no-deps redis_auth


build-api:
	docker-compose -f docker-compose-base.yml -f docker-compose-prod.yml -p api_auth up --build -d  --remove-orphans --no-deps api_auth

build-api-loc:
	docker-compose -f docker-compose-base.yml -f docker-compose-local.yml -p api_auth up --build -d  --remove-orphans --no-deps api_auth


down:
	docker-compose -f docker-compose-base.yml -f docker-compose-prod.yml -p api_auth down

down-loc:
	docker-compose -f docker-compose-base.yml -f docker-compose-local.yml -p api_auth down


down-v:
	docker-compose -f docker-compose-base.yml -f docker-compose-prod.yml -p api_auth down -v

down-v-loc:
	docker-compose -f docker-compose-base.yml -f docker-compose-local.yml -p api_auth down -v


restart:
	docker-compose -f docker-compose-base.yml -f docker-compose-prod.yml -p api_auth restart

restart-loc:
	docker-compose -f docker-compose-base.yml -f docker-compose-local.yml -p api_auth restart


check-config:
	docker-compose -f docker-compose-base.yml -f docker-compose-prod.yml -p api_auth config

check-config-loc:
	docker-compose -f docker-compose-base.yml -f docker-compose-local.yml -p api_auth config


postgres-dump:
	docker-compose -f docker-compose-base.yml -f docker-compose-prod.yml -p api_auth exec postgres_auth dump.sh

postgres-dump-loc:
	docker-compose -f docker-compose-base.yml -f docker-compose-local.yml -p api_auth exec postgres_auth dump.sh


pipinstall:
	docker-compose -f docker-compose-base.yml -f docker-compose-prod.yml -p api_auth run --rm api_auth pip install -r requirements/prod.txt

pipinstall-loc:
	docker-compose -f docker-compose-base.yml -f docker-compose-local.yml -p api_auth run --rm api_auth pip install -r requirements/local.txt


check-logs:
	docker-compose -f docker-compose-base.yml -f docker-compose-prod.yml -p api_auth logs

check-logs-loc:
	docker-compose -f docker-compose-base.yml -f docker-compose-local.yml -p api_auth logs


superuser:
	docker-compose -f docker-compose-base.yml -f docker-compose-prod.yml -p api_auth run --rm api_auth python3 -m scripts.create_superuser

superuser-loc:
	docker-compose -f docker-compose-base.yml -f docker-compose-local.yml -p api_auth run --rm api_auth python3 -m scripts.create_superuser


make-migration:
	docker-compose -f docker-compose-base.yml -f docker-compose-prod.yml -p api_auth run --rm api_auth python3 -m scripts.make_migration

make-migration-loc:
	docker-compose -f docker-compose-base.yml -f docker-compose-local.yml -p api_auth run --rm api_auth python3 -m scripts.make_migration


migrate:
	docker-compose -f docker-compose-base.yml -f docker-compose-prod.yml -p api_auth run --rm api_auth python3 -m scripts.migrate

migrate-loc:
	docker-compose -f docker-compose-base.yml -f docker-compose-local.yml -p api_auth run --rm api_auth python3 -m scripts.migrate


build:
	docker-compose -f docker-compose-base.yml -f docker-compose-prod.yml -p api_auth up --build -d --remove-orphans

build-loc:
	docker-compose -f docker-compose-base.yml -f docker-compose-local.yml -p api_auth up --build -d --remove-orphans


build-nginx:
	docker-compose -f docker-compose-base.yml -f docker-compose-prod.yml -p api_auth up --build -d  --remove-orphans --no-deps nginx


piplist:
	docker-compose -f docker-compose-base.yml -f docker-compose-local.yml -p api_auth run --rm api_auth pip list

flake8:
	docker-compose -f docker-compose-base.yml -f docker-compose-local.yml -p api_auth exec api_auth flake8 .

black-check:
	docker-compose -f docker-compose-base.yml -f docker-compose-local.yml -p api_auth exec api_auth black --check --exclude=venv .

black-diff:
	docker-compose -f docker-compose-base.yml -f docker-compose-local.yml -p api_auth exec api_auth black --diff --exclude=venv .

black:
	docker-compose -f docker-compose-base.yml -f docker-compose-local.yml -p api_auth exec api_auth black --exclude=venv .

isort-check:
	docker-compose -f docker-compose-base.yml -f docker-compose-local.yml -p api_auth exec api_auth isort . --check-only --skip venv

isort-diff:
	docker-compose -f docker-compose-base.yml -f docker-compose-local.yml -p api_auth exec api_auth isort . --diff --skip venv

isort:
	docker-compose -f docker-compose-base.yml -f docker-compose-local.yml -p api_auth exec api_auth isort . --skip venv

tests:
	docker-compose -f docker-compose-base.yml -f docker-compose-local.yml -p api_auth up --build -d --remove-orphans --no-deps tests_auth




check-vol-media:
	docker volume inspect app_media_volume

check-ip-api:
	docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' api_auth

check-ip-redis:
	docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' redis_auth
