# CHANGELOG

## 2026-11-17

- Migrated `access` to the V2 port-group array and removed deprecated `W9_*` port/URL aliases in `.env` and `docker-compose.yml`.

## 2026-09-12
- Added the `pgvector` app package based on the official `pgvector/pgvector:pg18-trixie` image.
- Pinned the image tag to `pg18-trixie`; no other image tags are supported.
- Added a PostgreSQL healthcheck and an init script that enables the `vector` extension in the default database.
- Regenerated the README.
