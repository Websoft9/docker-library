# CHANGELOG

## 2026-11-17

- Migrated `access` to the V2 port-group array and removed deprecated `W9_*` port/URL aliases in `.env` and `docker-compose.yml`.

## 2026-10-12

- Updated the main image from `localai/localai:latest` to `localai/localai:v4.6.2`.
- Added persistent volumes for models, backends, configuration, and runtime data to match the official container guidance.
- Added an API key variable and a `/v1/models` healthcheck for automated validation.
