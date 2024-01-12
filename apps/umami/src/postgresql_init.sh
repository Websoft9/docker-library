#!/bin/bash

set -a

echo "POSTGRES_USER is set to: '${POSTGRES_USER}'"
echo "POSTGRES_UMAMI_PASSWORD is set to: '${POSTGRES_UMAMI_PASSWORD}'"
# create umami user
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE USER umami WITH PASSWORD '${POSTGRES_UMAMI_PASSWORD}' SUPERUSER;
EOSQL