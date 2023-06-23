#!/usr/bin/env bash

set -o errexit # if any command fails any reason, script fails
set -o pipefail # if none of your pipecommand fails, exit fails
set -o nounset # if none of variables set, exit

working_dir="$(dirname ${0})"

source "${working_dir}/messages.sh"

message_welcome "These are the backups you have now:"

ls -lht "staticfiles/backups"