# CHANGELOG

## 2026-11-17

- Migrated `access` to the V2 port-group array and removed deprecated `W9_*` port/URL aliases in `.env` and `docker-compose.yml`.

## 2026-10-30

- Updated ONLYOFFICE Docs from `9.4` to `10.0`, including upstream security fixes.

## 2026-09-12

- Updated ONLYOFFICE Docs from `9.1` to `9.4`.
- Removed the obsolete RabbitMQ dependency and unused bundled data volumes to match the upstream 9.4 community deployment model.
- Added the upstream healthcheck and aligned `.env` and `docker-compose.yml` with current repository formatting rules.
