# CHANGELOG

## 2026-11-17

- Migrated `access` to the V2 port-group array and removed deprecated `W9_*` port/URL aliases in `.env` and `docker-compose.yml`.

## 2026-10-15
- Added the initial OpenDesign app package using the official `ghcr.io/nexu-io/od` image.
- Packaged the upstream single-container deployment with persistent `/app/.od` storage and health checks.
- Added access metadata, credential metadata, tests, maintenance assignment, and catalog metadata.
