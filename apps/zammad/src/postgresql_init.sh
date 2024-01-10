#!/bin/bash
set -e

# create zammad user and database
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE USER zammad WITH PASSWORD '${POSTGRES_ZAMMAD_PASSWORD}';
    CREATE DATABASE zammad;
    GRANT ALL PRIVILEGES ON DATABASE zammad TO zammad;
EOSQL