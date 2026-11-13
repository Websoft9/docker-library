# CHANGELOG

## 2026-11-13

- Added `env_file: .env` to the main `console` service (`${W9_ID}`) so runtime `W9_*` metadata variables are loaded on container startup.

## 2026-11-04

- Declared internal PostgreSQL, MongoDB, and ClickHouse dependencies with their existing service environment sources; excluded Redpanda.
- Recorded the postgres and admin database names without mistaking the newjitsu PostgreSQL schema for another database.
- Kept all three stores internal-only and removed external providers and connection mappings.
- Restored original console, rotor, bulker, and ingest connection expressions; removed variables added solely for external databases without changing initialization or guessing new keys.
- Preserved default connections and image versions; passed static configuration and regression checks without deployment or live database verification. PostgreSQL 14 still reaches EOL on 2026-11-12.

## 2026-09-15
- Added a new Jitsu 2.15 app package based on the official Docker Compose core stack.
- Bundled PostgreSQL, MongoDB, ClickHouse, and Redpanda with Jitsu Console, Bulker, Rotor, and Ingest.
- Documented the upstream limitation that full functions, profile builders, and connector syncs require Kubernetes.
