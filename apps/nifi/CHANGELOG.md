# CHANGELOG

## 2026-11-17

- Migrated `access` to the V2 port-group array and removed deprecated `W9_*` port/URL aliases in `.env` and `docker-compose.yml`.

## 2026-10-12

- Rebuilt the broken NiFi package from the official `apache/nifi` Docker image.
- Switched the package to the current secure single-container HTTPS deployment model with single-user authentication.
- Added app-local HTTPS validation coverage and current upstream metadata.
