# CHANGELOG

## 2026-11-17

- Migrated `access` to the V2 port-group array and removed deprecated `W9_*` port/URL aliases in `.env` and `docker-compose.yml`.

## 2026-10-13
- Updated Caddy from `2.10` to `2.11` based on the latest stable upstream release line.
- Aligned `.env` and `docker-compose.yml` with current repository policy requirements.
- Added app-specific validation coverage for the Caddy root path.
