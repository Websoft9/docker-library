#!/bin/bash
set -e

# create zammad user and database
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER zammad WITH PASSWORD '${ZAMMAD_PASSWORD}';
    CREATE DATABASE zammad;
    GRANT ALL PRIVILEGES ON DATABASE zammad TO zammad;

EOSQL