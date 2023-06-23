#!/usr/bin/env bash

#set -o errexit # if any command fails any reason, script fails
set -o pipefail # if none of of your pipecommand fails, exit fails
set -o nounset # if none of variables set, exit

working_dir="$(dirname ${0})"

source "${working_dir}/../../.envs/.${ENV}/.postgres"
source "${working_dir}/messages.sh"

message_welcome "Restoring to '${POSTGRES_DB}' database..."

uploaded_dump="uploaded_dump"

cd staticfiles/backups || exit

export PGHOST="${POSTGRES_HOST}"
export PGPORT="${POSTGRES_PORT}"
export PGUSER="${POSTGRES_USER}"
export PGPASSWORD="${POSTGRES_PASSWORD}"
export PGDATABASE="${POSTGRES_DB}"

pg_restore -d ${POSTGRES_DB} --clean "${uploaded_dump}" || exit
message_success "'${POSTGRES_DB}' database was restored from 'staticfiles/backups/${uploaded_dump}'"
