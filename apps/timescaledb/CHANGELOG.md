# CHANGELOG

## 2026-11-17

- Migrated `access` to the V2 port-group array and removed deprecated `W9_*` port/URL aliases in `.env` and `docker-compose.yml`.

## 2026-10-09
- Initial Websoft9 package for TimescaleDB using the official `timescale/timescaledb-ha:pg18` image.
- Added persistent PostgreSQL deployment, healthcheck, metadata, and validation tests.
