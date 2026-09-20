#!/bin/bash

set -o errexit
set -o pipefail

zammad_abort() {
  echo "$1" >&2
  echo "Correct this, then remove the postgresql-data volume and start again. The" >&2
  echo "  database directory is already initialised, so this will not run twice." >&2
  exit 1
}

# Zammad must not reuse the bootstrap role, which is always a superuser.
if [ "${ZAMMAD_DB_USER}" = "${POSTGRES_USER}" ]; then
  zammad_abort "ZAMMAD_DB_USER and POSTGRES_USER must differ, the latter is a superuser."
fi

# The system databases exist already, so they would keep the bootstrap role as owner.
case "${ZAMMAD_DB}" in
  postgres | template0 | template1)
    zammad_abort "ZAMMAD_DB must not be one of PostgreSQL's system databases."
    ;;
esac

echo "Creating the '${ZAMMAD_DB_USER}' role and the '${ZAMMAD_DB}' database..."

psql --variable ON_ERROR_STOP=1 \
     --username "${POSTGRES_USER}" \
     --dbname "${POSTGRES_DB:-postgres}" \
     --variable role="${ZAMMAD_DB_USER}" \
     --variable pass="${ZAMMAD_DB_PASS}" \
     --variable db="${ZAMMAD_DB}" <<'EOSQL'
CREATE ROLE :"role" LOGIN PASSWORD :'pass';
CREATE DATABASE :"db" OWNER :"role";
EOSQL
