#!/usr/bin/env bash

working_dir="$(dirname ${0})"

source "${working_dir}/../../.envs/.${ENV}/.postgres"
source "${working_dir}/messages.sh"

message_welcome "Creating uuid-ossp extension to '${POSTGRES_DB}' database..."

export PGHOST="${POSTGRES_HOST}"
export PHPORT="${POSTGRES_PORT}"
export PGUSER="${POSTGRES_USER}"
export PGPASSWORD="${POSTGRES_PASSWORD}"
export PGDATABASE="${POSTGRES_DB}"

psql -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
message_success "Created uuid-ossp extension to '${POSTGRES_DB}' database..."
