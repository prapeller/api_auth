#!/usr/bin/env bash

working_dir="$(dirname ${0})"

source "${working_dir}/../../.envs/.${ENV}/.postgres"
source "${working_dir}/messages.sh"

message_welcome "Backing up the '${POSTGRES_DB}' database..."

dump_last="dump_last"

mkdir staticfiles
cd staticfiles
mkdir backups
cd backups

export PGHOST="${POSTGRES_HOST}"
export PGPORT="${POSTGRES_PORT}"
export PGUSER="${POSTGRES_USER}"
export PGPASSWORD="${POSTGRES_PASSWORD}"
export PGDATABASE="${POSTGRES_DB}"

pg_dump -Fc > "${dump_last}" || exit
message_success "'${POSTGRES_DB}' database made backup to 'staticfiles/backups/${dump_last}'"
